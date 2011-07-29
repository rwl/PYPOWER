# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Runs a power flow.
"""

from sys import stderr

from time import time

from numpy import r_, c_, ix_, zeros, pi, ones, exp, argmax
from numpy import flatnonzero as find

from bustypes import bustypes
from ext2int import ext2int
from loadcase import loadcase
from ppoption import ppoption
from ppver import ppver
from makeBdc import makeBdc
from makeSbus import makeSbus
from dcpf import dcpf
from makeYbus import makeYbus
from newtonpf import newtonpf
from fdpf import fdpf
from gausspf import gausspf
from makeB import makeB
from pfsoln import pfsoln
from printpf import printpf
from savecase import savecase
from int2ext import int2ext

from idx_bus import PD, QD, VM, VA, GS, BUS_TYPE, PQ
from idx_brch import PF, PT, QF, QT
from idx_gen import PG, QG, VG, QMAX, QMIN, GEN_BUS, GEN_STATUS


def runpf(casedata='case9', ppopt=None, fname='', solvedcase='',
          expect_opf_data=True):
    """Runs a power flow.

    Runs a power flow [full AC Newton's method by default] and optionally
    returns the solved values in the data matrices, a flag which is C{True} if
    the algorithm was successful in finding a solution, and the elapsed
    time in seconds. All input arguments are optional. If C{casename} is
    provided it specifies the name of the input data file or dict
    containing the power flow data. The default value is 'case9'.

    If the ppopt is provided it overrides the default PYPOWER options
    vector and can be used to specify the solution algorithm and output
    options among other things. If the 3rd argument is given the pretty
    printed output will be appended to the file whose name is given in
    C{fname}. If C{solvedcase} is specified the solved case will be written
    to a case file in PYPOWER format with the specified name. If C{solvedcase}
    ends with '.mat' it saves the case as a MAT-file otherwise it saves it
    as a Python-file.

    If the C{ENFORCE_Q_LIMS} options is set to C{True} [default is false] then
    if any generator reactive power limit is violated after running the AC
    power flow, the corresponding bus is converted to a PQ bus, with Qg at
    the limit, and the case is re-run. The voltage magnitude at the bus
    will deviate from the specified value in order to satisfy the reactive
    power limit. If the reference bus is converted to PQ, the first
    remaining PV bus will be used as the slack bus for the next iteration.
    This may result in the real power output at this generator being
    slightly off from the specified values.

    Enforcing of generator Q limits inspired by contributions from Mu Lin,
    Lincoln University, New Zealand (1/14/05).

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## default arguments
    ppopt = ppoption(ppopt)

    ## options
    verbose = ppopt["VERBOSE"]
    qlim = ppopt["ENFORCE_Q_LIMS"]  ## enforce Q limits on gens?
    dc = ppopt["PF_DC"]             ## use DC formulation?

    ## read data
    if expect_opf_data:
        baseMVA, bus, gen, branch, _, _ = loadcase(casedata, expect_opf_data=expect_opf_data)
    else:
        baseMVA, bus, gen, branch = loadcase(casedata, expect_opf_data=expect_opf_data)

    ## convert to internal indexing
    i2e, bus, gen, branch = ext2int(bus, gen, branch)

    ## get bus index lists of each type of bus
    ref, pv, pq = bustypes(bus, gen)

    ## generator info
    on = find(gen[:, GEN_STATUS] > 0)      ## which generators are on?
    gbus = gen[on, GEN_BUS].astype(int)    ## what buses are they at?

    ##-----  run the power flow  -----
    t0 = time()
    if dc:                               # DC formulation
        ## initial state
        Va0 = bus[:, VA] * (pi / 180)

        ## build B matrices and phase shift injections
        B, Bf, Pbusinj, Pfinj = makeBdc(baseMVA, bus, branch)

        ## compute complex bus power injections [generation - load]
        ## adjusted for phase shifters and real shunts
        Pbus = makeSbus(baseMVA, bus, gen).real - Pbusinj - bus[:, GS] / baseMVA

        ## "run" the power flow
        Va = dcpf(B, Pbus, Va0, ref, pv, pq)

        # add columns of zeros as necessary
        if branch.shape[1] < QT:
            branch = c_[branch,
                    zeros((branch.shape[0], QT - branch.shape[1] + 1))]

        ## update data matrices with solution
        branch[:, [QF, QT]] = zeros((branch.shape[0], 2))
        branch[:, PF] = (Bf * Va + Pfinj) * baseMVA
        branch[:, PT] = -branch[:, PF]
        bus[:, VM] = ones(bus.shape[0])
        bus[:, VA] = Va * (180 / pi)
        ## update Pg for swing generator [note: other gens at ref bus are accounted for in Pbus]
        ##      Pg = Pinj + Pload + Gs
        ##      newPg = oldPg + newPinj - oldPinj
        refgen = find(gbus == ref)             ## which is[are] the reference gen[s]?
        gen[on[refgen[0]], PG] = gen[on[refgen[0]], PG] + (B[ref, :] * Va - Pbus[ref]) * baseMVA

        success = 1
    else:                                ## AC formulation
        ## initial state
        # V0    = ones(bus.shape[0])            ## flat start
        V0  = bus[:, VM] * exp(1j * pi/180 * bus[:, VA])
        V0[gbus] = gen[on, VG] / abs(V0[gbus]) * V0[gbus]

        if qlim:
            ref0 = ref                         ## save index and angle of
            Varef0 = bus[ref0, VA]             ##   original reference bus
            limited = []                       ## list of indices of gens @ Q lims
            fixedQg = zeros(gen.shape[0])      ## Qg of gens at Q limits

        repeat = True
        while repeat:
            ## build admittance matrices
            Ybus, Yf, Yt = makeYbus(baseMVA, bus, branch)

            ## compute complex bus power injections [generation - load]
            Sbus = makeSbus(baseMVA, bus, gen)

            ## run the power flow
            alg = ppopt["PF_ALG"]
            if alg == 1:
                V, success, _ = newtonpf(Ybus, Sbus, V0, ref, pv, pq, ppopt)
            elif alg == 2 or alg == 3:
                Bp, Bpp = makeB(baseMVA, bus, branch, alg)
                V, success, _ = fdpf(Ybus, Sbus, V0, Bp, Bpp, ref, pv, pq, ppopt)
            elif alg == 4:
                V, success, _ = gausspf(Ybus, Sbus, V0, ref, pv, pq, ppopt)
            else:
                raise ValueError, 'Only Newton''s method, fast-decoupled, and ' + \
                             'Gauss-Seidel power flow algorithms currently ' + \
                             'implemented.\n'

            ## update data matrices with solution
            bus, gen, branch = pfsoln(baseMVA, bus, gen, branch, Ybus, Yf, Yt, V, ref, pv, pq)

            if qlim:             ## enforce generator Q limits
                ## find gens with violated Q constraints
                mx = find( gen[:, GEN_STATUS] > 0 & gen[:, QG] > gen[:, QMAX] )
                mn = find( gen[:, GEN_STATUS] > 0 & gen[:, QG] < gen[:, QMIN] )

                if len(mx) > 0 or len(mn) > 0:  ## we have some Q limit violations
                    if len(pv):
                        if verbose:
                            if len(mx) > 0:
                                print 'Gen %d [only one left] exceeds upper Q limit : INFEASIBLE PROBLEM\n' % mx
                            else:
                                print 'Gen %d [only one left] exceeds lower Q limit : INFEASIBLE PROBLEM\n' % mn

                        success = 0
                        break

                    ## one at a time?
                    if qlim == 2:    ## fix largest violation, ignore the rest
                        k = argmax(r_[gen[mx, QG] - gen[mx, QMAX],
                                      gen[mn, QMIN] - gen[mn, QG]])
                        if k > len(mx):
                            mn = mn[k - len(mx)]
                            mx = []
                        else:
                            mx = mx[k]
                            mn = []

                    if verbose and len(mx) > 0:
                        print 'Gen %d at upper Q limit, converting to PQ bus\n' % mx

                    if verbose and len(mn) > 0:
                        print 'Gen %d at lower Q limit, converting to PQ bus\n' % mn

                    ## save corresponding limit values
                    fixedQg[mx] = gen[mx, QMAX]
                    fixedQg[mn] = gen[mn, QMIN]
                    mx = r_[mx, mn]

                    ## convert to PQ bus
                    gen[mx, QG] = fixedQg[mx]      ## set Qg to binding limit
                    gen[mx, GEN_STATUS] = 0        ## temporarily turn off gen,
                    for i in range(mx):            ## [one at a time, since they may be at same bus]
                        bi = gen[mx[i], GEN_BUS]   ## adjust load accordingly,
                        bus[bi, [PD, QD]] = (bus[bi, [PD, QD]] - gen[mx[i], [PG, QG]])

                    bus[gen[mx, GEN_BUS], BUS_TYPE] = PQ   ## & set bus type to PQ

                    ## update bus index lists of each type of bus
                    ref_temp = ref
                    ref, pv, pq = bustypes(bus, gen)
                    if verbose and ref != ref_temp:
                        print 'Bus %d is new slack bus\n' % ref

                    limited = r_[limited, mx]
                else:
                    repeat = 0 ## no more generator Q limits violated
            else:
                repeat = 0     ## don't enforce generator Q limits, once is enough

        if qlim and len(limited) > 0:
            ## restore injections from limited gens [those at Q limits]
            gen[limited, QG] = fixedQg[limited]    ## restore Qg value,
            for i in range(limited):               ## [one at a time, since they may be at same bus]
                bi = gen[limited[i], GEN_BUS]      ## re-adjust load,
                bus[bi, [PD, QD]] = bus[bi, [PD, QD]] + gen[limited[i], [PG, QG]]

            gen[limited, GEN_STATUS] = 1           ## and turn gen back on
            if ref != ref0:
                ## adjust voltage angles to make original ref bus correct
                bus[:, VA] = bus[:, VA] - bus[ref0, VA] + Varef0

    et = time() - t0

    ##-----  output results  -----
    ## convert back to original bus numbering & print results
    bus, gen, branch = int2ext(i2e, bus, gen, branch)

    if fname:
        fd = None
        try:
            fd = open(fname, "wb")
        except Exception, detail:
            raise IOError, "Error opening %s: %s.\n" % (fname, detail)
        finally:
            if fd is not None:
                printpf(baseMVA, bus, gen, branch, None, success, et, 1, ppopt)
                fd.close()

    printpf(baseMVA, bus, gen, branch, None, success, et, None, ppopt)

    ## save solved case
    if solvedcase:
        savecase(solvedcase, baseMVA, bus, gen, branch)

    return baseMVA, bus, gen, branch, success, et


if __name__ == '__main__':
    runpf()
