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

from sys import stdout

from time import time

from numpy import array, zeros, ones, c_, r_, any, pi, angle, exp
from numpy import flatnonzero as find

from pypower.bustypes import bustypes
from pypower.ppoption import ppoption
from pypower.ext2int import ext2int
from pypower.loadcase import loadcase
from pypower.makeYbus import makeYbus
from pypower.pqcost import pqcost
from pypower.poly2pwl import poly2pwl
from pypower.totcost import totcost
from pypower.int2ext import int2ext
from pypower.printpf import printpf
from pypower.opf_form import opf_form
from pypower.isload import isload
from pypower.opf_slvr import opf_slvr
from pypower.fg_names import fg_names
from pypower.LPeqslvr import LPeqslvr
from pypower.LPconstr import LPconstr
from pypower.opfsoln import opfsoln

from pypower.idx_bus import MU_VMIN, VA, VM
from pypower.idx_brch import PF, QF, PT, QT, MU_SF, MU_ST, BR_STATUS
from pypower.idx_cost import MODEL, PW_LINEAR, POLYNOMIAL

from pypower.idx_gen import \
    VG, PG, QG, MU_QMIN, MU_PMAX, MU_PMIN, GEN_STATUS, GEN_BUS, \
    PMIN, PMAX, QMIN, QMAX


def lpopf(baseMVA, bus, gen, branch, areas, gencost, ppopt):
    """Solves an AC optimal power flow using succesive LPs.

    Uses the standard/CCV formulations from pre-3.0 versions of MATPOWER, as
    opposed to the generalized formulation used by fmincopf and MINOPF.

    bus, gen, branch, f, success = lpopf(casefile, ppopt)

    bus, gen, branch, f, success = lpopf(baseMVA, bus, gen, branch, areas,
                                   gencost, ppopt)

    bus, gen, branch, f, success, info, et = lpopf(casefile)

    The data for the problem can be specified in one of 3 ways: (1) the name of
    a case file which defines the data matrices baseMVA, bus, gen, branch,
    areas and gencost, (2) a struct containing the data matrices as fields, or
    (3) the data matrices themselves.

    The optional ppopt vector specifies PYPOWER options. Type 'help ppoption'
    for details and default values.

    The solved case is returned in the data matrices, bus, gen and branch. Also,
    returned are the final objective function value (f) and a flag which is
    true if the algorithm was successful in finding a solution (success).
    Additional optional return values are an algorithm specific return status
    (info), elapsed time in seconds (et).

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    # input arg sorting
    t1 = time()
    if isinstance(baseMVA, basestring) or isinstance(baseMVA, dict):
        casefile = baseMVA
        if bus is None:
            ppopt = ppoption()
        else:
            ppopt = bus

        baseMVA, bus, gen, branch, areas, gencost = loadcase(casefile)
    else:
        if ppopt is None:
            ppopt = ppoption()

    # options
    verbose = ppopt['VERBOSE']
    npts = ppopt['OPF_POLY2PWL_PTS']

    # If tables do not have multiplier/extra columns, append zero cols
    if bus.shape[1] < MU_VMIN + 1:
        bus = c_[ bus, zeros((bus.shape[0], MU_VMIN - bus.shape[1] + 1)) ]

    if gen.shape[1] < MU_QMIN + 1:
        gen = c_[ gen, zeros((gen.shape[0], MU_QMIN - gen.shape[1] + 1)) ]

    if branch.shape[1] < MU_ST + 1:
        branch = c_[ branch, zeros((branch.shape[0], MU_ST - branch.shape[1])) ]

    # Filter out inactive generators and branches; save original bus & branch
    comgen = find(gen[:, GEN_STATUS] > 0)
    offgen = find(gen[:, GEN_STATUS] <= 0)
    onbranch  = find(branch[:, BR_STATUS] != 0)
    offbranch = find(branch[:, BR_STATUS] == 0)
    genorg = gen.copy()
    branchorg = branch.copy()
    ng = gen.shape[0]         # original size(gen), at least temporally
    gen = gen[comgen, :]
    branch = branch[onbranch, :]
    if gencost.shape[0] == ng:
        gencost = gencost[comgen, :]
    else:
        gencost = gencost[r_[comgen, comgen + ng], :]

    # Renumber buses consecutively
    i2e, bus, gen, branch, areas = ext2int(bus, gen, branch, areas)

    ## get bus index lists of each type of bus
    ref, pv, pq = bustypes(bus, gen)

    ## build admittance matrices
    Ybus, Yf, Yt = makeYbus(baseMVA, bus, branch)

    # Check costs
    if any( (gencost[:, MODEL] != PW_LINEAR) & (gencost[:, MODEL] != POLYNOMIAL) ):
        raise AttributeError, 'copf.m: Unrecognized generator cost model in input data'

    # print warning if there are dispatchable loads
    if any(isload(gen)):
        stdout.write('\nlpopf.m: Warning: Found dispatchable load in data (see ''help isload''\n')
        stdout.write('         for details on what consitutes a dispatchable load). Only\n')
        stdout.write('         the generalized formulation algorithms can maintain the power\n')
        stdout.write('         factor of dispatchable loads constant; the Q injection will\n')
        stdout.write('         be treated as a free variable.\n')

    if ppopt['OPF_ALG_POLY'] == 0:  # OPF_ALG not set
        if any( gencost[:, MODEL] == PW_LINEAR ):
            ppopt['OPF_ALG_POLY'] = 240  # CCV formulation, sparse LP (relaxed)
        else:  # All are polynomial
            ppopt['OPF_ALG_POLY'] = 140  # Standard formulation, sparse LP (relaxed)

    alg = ppopt['OPF_ALG_POLY']
    formulation = opf_form(alg)
    code = opf_slvr(alg)
    if (code < 1) or (code > 3):
        raise ValueError, 'lpopf: LP solver called, but another solver specified in options'

    if (formulation == 2) and any(gencost[:, MODEL] == POLYNOMIAL):  # mixed models
        if verbose:
            stdout.write('lpopf.m: some generators use poly cost model, all will be converted\n')
            stdout.write('        to piecewise linear.\n')

        pcost, qcost = pqcost(gencost, gen.shape[0])
        i_poly = find(pcost[:, MODEL] == POLYNOMIAL)
        tmp = poly2pwl(pcost[i_poly, :], gen[i_poly, PMIN],
                         gen[i_poly, PMAX], npts)
        pcost[i_poly, :tmp.shape[1]] = tmp
        if len(qcost) > 0:
            i_poly = find(qcost[:, MODEL] == POLYNOMIAL)
            tmp = poly2pwl(qcost[i_poly, :], gen[i_poly, QMIN],
                           gen[i_poly, QMAX], npts)
            qcost[i_poly, :tmp.shape[1]] = tmp

        gencost = r_[pcost, qcost]

    if (formulation == 1) and any(gencost[:, MODEL] == PW_LINEAR):
        raise ValueError, 'copf.m: Standard formulation requested, but there are piece-wise linear costs in data'

    # Now go for it.
    gbus = gen[:, GEN_BUS].astype(int)        ## what buses are gens at?

    ## sizes of things
    nb = bus.shape[0]
    nl = branch.shape[0]
    npv  = len(pv)
    npq  = len(pq)
    ng = gen.shape[0]            ## number of generators that are turned on

    ## initial state
    V  = bus[:, VM] * exp(1j * pi/180 * bus[:, VA])
    V[gbus] = gen[:, VG] / abs(V[gbus])* V[gbus]
    Pg  = gen[:, PG] / baseMVA
    Qg  = gen[:, QG] / baseMVA

    ## check for costs for Qg
    pcost, qcost = pqcost(gencost, gen.shape[0])

    ## set up indexing for x
    j1 = 0;     j2  = npv           ## j1:j2  - V angle of pv buses
    j3 = j2;    j4  = j2 + npq      ## j3:j4  - V angle of pq buses
    j5 = j4;    j6  = j4 + nb       ## j5:j6  - V mag of all buses
    j7 = j6;    j8  = j6 + ng       ## j7:j8  - P of generators
    j9 = j8;    j10  = j8 + ng      ## j9:j10  - Q of generators
    j11 = j10;  j12  = j10 + ng     ## j11:j12  - Cp, cost of Pg
    j13 = j12;  j14  = j12 + ng     ## j13:j14  - Cq, cost of Qg

    ## set up x
    if formulation == 1:
        Cp = array([])
        Cq = array([])
    else:
        Cp = totcost(pcost, Pg * baseMVA)
        if len(qcost) > 0:
            Cq = totcost(qcost, Qg * baseMVA)
        else:
            ## empty if qcost is empty
            Cq = array([])

    x = r_[angle(V[r_[pv, pq]]), abs(V), Pg, Qg, Cp, Cq]

    ## objective and constraint function names
    fun, grad  = fg_names(alg)
    ppopt['OPF_NEQ'] = 2 * nb        ## set number of equality constraints

    ## run load flow to get starting point
    x, success_lf = LPeqslvr(x, baseMVA, bus, gen, gencost, branch, Ybus, Yf,
                             Yt, V, ref, pv, pq, ppopt)
    if success_lf != 1:
        raise ValueError, 'Sorry, cannot find a starting point using power flow, please check data!'

    ## set step size
    cstep = 0
    if len(Cp) > 0:
        cstep = max(abs(Cp))
        if cstep < 1.0e6:
            cstep = 1.0e6

    step0 = r_[
        2 * ones(nb - 1),          ## starting stepsize for Vangle
        ones(nb),            ## Vmag
        0.6 * ones(ng),          ## Pg
        0.3 * ones(ng),          ## Qg
        cstep * ones(len(Cp)),   ## Cp
        cstep * ones(len(Cq))    ## Cq
    ]
    idx_xi = array([])

    ## run optimization
    x, lmbda, success = LPconstr(fun, x, idx_xi, ppopt, step0,
                            array([]), array([]), grad,
                            'LPeqslvr', baseMVA, bus, gen, gencost, branch,
                            Ybus, Yf, Yt, V, ref, pv, pq, ppopt)
    info = success

    ## get final objective function value & constraint values
    f = eval(fun)(x, baseMVA, bus, gen, gencost, branch, Ybus, Yf, Yt, V, ref,
              pv, pq, ppopt)

    ## reconstruct V
    Va = zeros(nb)
    Va[r_[ref, pv, pq]] = r_[angle(V[ref]), x[j1:j2], x[j3:j4]]
    Vm = x[j5:j6]
    V = Vm * exp(1j * Va)

    ## grab Pg & Qg
    Sg = x[j7:j8] + 1j * x[j9:j10]    ## complex power generation in p.u.

    ##-----  calculate return values  -----
    ## update bus, gen, branch with solution info
    bus, gen, branch = opfsoln(baseMVA, bus, gen, branch,
                Ybus, Yf, Yt, V, Sg, lmbda, ref, pv, pq, ppopt)

    g = array([])
    jac = array([])  # we do not compute jacobians

    # convert to original external bus ordering
    bus, gen, branch, areas = int2ext(i2e, bus, gen, branch, areas)

    # Now create output matrices with all lines, all generators, committed and
    # non-committed
    busout = bus.copy()
    genout = genorg.copy()
    branchout = branchorg.copy()
    genout[comgen, :] = gen
    branchout[onbranch, :] = branch
    # And zero out appropriate fields of non-comitted generators and lines
    tmp = zeros(len(offgen))
    genout[offgen, PG] = tmp
    genout[offgen, QG] = tmp
    genout[offgen, MU_PMAX] = tmp
    genout[offgen, MU_PMIN] = tmp
    tmp = zeros(len(offbranch))
    branchout[offbranch, PF] = tmp
    branchout[offbranch, QF] = tmp
    branchout[offbranch, PT] = tmp
    branchout[offbranch, QT] = tmp
    branchout[offbranch, MU_SF] = tmp
    branchout[offbranch, MU_ST] = tmp

    et = time() - t1
    if info > 0:
        printpf(baseMVA, bus, genout, branchout, f, info, et, 1, ppopt)

    return busout, genout, branchout, f, success, info, et, g, jac
