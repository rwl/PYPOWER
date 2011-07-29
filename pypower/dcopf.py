# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

"""Solves a DC optimal power flow.
"""

from time import time

from numpy import \
    array, zeros, ones, arange, c_, r_, copy, any, pi, diag, sum, dot
from numpy import flatnonzero as find

from scipy.sparse import vstack, hstack, csr_matrix as sparse
from scipy.sparse import eye as speye

from pypower.bustypes import bustypes
from pypower.ppoption import ppoption
from pypower.ext2int import ext2int
from pypower.loadcase import loadcase
from pypower.makeBdc import makeBdc
from pypower.pqcost import pqcost
from pypower.poly2pwl import poly2pwl
from pypower.totcost import totcost
from pypower.pp_qp import pp_qp
from pypower.pp_lp import pp_lp
from pypower.int2ext import int2ext
from pypower.printpf import printpf

from pypower.idx_bus import MU_VMIN, MU_VMAX, VA, VM, PD, GS, LAM_P, LAM_Q
from pypower.idx_brch import PF, QF, PT, QT, MU_SF, MU_ST, BR_STATUS, RATE_A
from pypower.idx_cost import MODEL, PW_LINEAR, POLYNOMIAL, NCOST, COST

from pypower.idx_gen import \
    PG, QG, MU_QMAX, MU_QMIN, MU_PMAX, MU_PMIN, GEN_STATUS, GEN_BUS, \
    PMIN, PMAX, QMIN, QMAX


def dcopf(baseMVA_or_casedata, bus_or_ppopt=None, gen=None, branch=None,
          areas=None, gencost=None, ppopt=None):
    """Solves a DC optimal power flow.

    bus, gen, branch, f, success, info, et = dcopf(casefile)

    bus, gen, branch, f, success, info, et = dcopf(casefile, ppopt)

    bus, gen, branch, f, success, info, et = dcopf(baseMVA, bus, gen, branch,
                                    areas, gencost, ppopt)

    The data for the problem can be specified in one of 3 ways: (1) the name of
    a case file which defines the data matrices baseMVA, bus, gen, branch,
    areas and gencost, (2) a struct containing the data matrices as fields, or
    (3) the data matrices themselves.

    The optional ppopt dict specifies PYPOWER options. Type L{ppoption}
    for details and default values.

    The solved case is returned in the data matrices, bus, gen and branch. Also,
    returned are the final objective function value (f) and a flag which is
    true if the algorithm was successful in finding a solution (success).
    Additional return values are an algorithm specific return status (info),
    elapsed time in seconds (et).

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ##----- initialization -----
    ## Sort arguments
    if isinstance(baseMVA_or_casedata, basestring) or \
            isinstance(baseMVA_or_casedata, dict):
        casefile = baseMVA_or_casedata
        if bus_or_ppopt is None:
            ppopt = ppoption()
        else:
            ppopt = bus_or_ppopt
        baseMVA, bus, gen, branch, areas, gencost = loadcase(casefile)
    else:
        baseMVA = baseMVA_or_casedata
        bus = bus_or_ppopt
        if ppopt is None:
            ppopt = ppoption()

    ## options
    ppopt['PF_DC'] = True  # force DC treatment
    verbose = ppopt['VERBOSE']
    ## number of points to evaluate when converting polynomials to piece-wise linear
    npts = ppopt['OPF_POLY2PWL_PTS']

    # If tables do not have multiplier/extra columns, append zero cols
    if bus.shape[1] < MU_VMIN + 1:
        bus = c_[ bus, zeros((bus.shape[0], MU_VMIN + 1 - bus.shape[1])) ]

    if gen.shape[1] < MU_QMIN + 1:
        gen = c_[ gen, zeros((gen.shape[0], MU_QMIN + 1 - gen.shape[1])) ]

    if branch.shape[1] < MU_ST + 1:
        branch = c_[ branch, zeros((branch.shape[0], MU_ST + 1 - branch.shape[1])) ]

    # Filter out inactive generators and branches; save original bus & branch
    comgen = find(gen[:, GEN_STATUS] > 0)
    offgen = find(gen[:, GEN_STATUS] <= 0)
    onbranch  = find(branch[:, BR_STATUS] != 0)
    offbranch = find(branch[:, BR_STATUS] == 0)
    genorg = copy(gen)
    branchorg = copy(branch)
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
    ref, _, _ = bustypes(bus, gen)

    ## build B matrices and phase shift injections
    B, Bf, Pbusinj, Pfinj = makeBdc(baseMVA, bus, branch)

    ##-----  check/convert costs, set default algorithm  -----
    ## get cost model, check consistency
    model = gencost[:, MODEL]
    i_pwln = find(model == PW_LINEAR)
    i_poly = find(model == POLYNOMIAL)
    if any(i_pwln) and any(i_poly) and verbose:
        print 'not all generators use same cost model, all will be converted to piece-wise linear\n'

    if any(i_pwln) or any(find(gencost[:, NCOST] > 3)):
        formulation = 2    ## use piecewise linear formulation
    else:
        formulation = 1    ## use polynomial cost formulation
        if any(find(gencost[:, NCOST] != 3)):
            raise ValueError, 'DC opf with polynomial costs can only handle quadratic costs.'

    ## convert polynomials to piece-wise linear (if necessary)
    if any(i_poly) and (formulation == 2):
        if verbose:
            print 'converting from polynomial to piece-wise linear cost model\n'
        pcost, qcost = pqcost(gencost, gen.shape[0])
        i_poly = find(pcost[:, MODEL] == POLYNOMIAL)
        tmp = poly2pwl(pcost[i_poly, :], gen[i_poly, PMIN], gen[i_poly, PMAX], npts)
        pcost[i_poly, arange(tmp.shape[1])] = tmp
        if len(qcost) > 0:
            i_poly = find(qcost[:, MODEL] == POLYNOMIAL)
            tmp = poly2pwl(qcost[i_poly, :], gen[i_poly, QMIN], gen[i_poly, QMAX], npts)
            qcost[i_poly, arange(tmp.shape[1])] = tmp
        gencost = r_[pcost, qcost]

    ##-----  run opf  -----
    ## start timer
    t0 = time()

    ## gen info
    on = find(gen[:, GEN_STATUS] > 0)      ## which generators are on?
#    gbus = gen[on, GEN_BUS].astype(int)    ## what buses are they at?

    ## sizes of things
    nb = bus.shape[0]
    nl = branch.shape[0]
    ng = len(on)                        ## number of generators that are turned on

    ## initial state
    Va  = bus[:, VA] * (pi / 180.0)
    Pg  = gen[on, PG] / baseMVA

    ## check for costs for Qg
    pcost, qcost = pqcost(gencost, gen.shape[0], on)

    ## set up x along with indexing
    j1 = 0;         j2  = nb               ## j1:j2    - bus V angles
    j3 = j2;        j4  = j2 + ng          ## j3:j4    - P of generators
    _ = j4;         _  = j4 + ng          ## j5:j6    - Cp, cost of Pg
    if formulation == 2:             ## piece-wise linear costs
        Cp = totcost(pcost, Pg * baseMVA)
    else:                            ## polynomial costs
        Cp = array([])

    nc = len(Cp)                        ## number of cost variables (ng or 0)
    x = r_[Va, Pg, Cp]

    ## set up constraints and indexing where,   AA * x <= bb
    # i0 = 0                            ## 1 - voltage angle reference
    i1 = 1;         i2 = nb + 1         ## i1:i2 - P mismatch, all buses
    i3 = i2;        i4 = i2 + ng        ## i3:i4 - Pmin, gen buses
    i5 = i4;        i6 = i4 + ng        ## i5:i6 - Pmax, gen buses
    i7 = i6;        i8 = i6 + nl        ## i7:i8 - |Pf| line limit
    i9 = i8;        i10 = i8 + nl       ## i9:i10 - |Pt| line limit

    if formulation == 2:             ## piece-wise linear costs
        ## compute cost constraints [ Cp >= m * Pg + b ] => [ m * Pg - Cp <= -b ]
        nsegs = pcost[:, NCOST].astype(int) - 1  ## number of cost constraints for each gen
        ncc = sum(nsegs)                         ## total number of cost constraints
        #Acc = sparse((ncc, nb + ng + nc))
        Acc = zeros((ncc, nb + ng + nc))
        bcc = zeros(ncc)
        for i in range(ng):
            xx = pcost[i,       COST:( COST + 2*(nsegs[i]) + 1):2]
            yy = pcost[i,   (COST+1):( COST + 2*(nsegs[i]) + 2):2]
            k1 = arange(nsegs[i])
            k2 = arange(1, (nsegs[i] + 1))
            m = (yy[k2] - yy[k1]) / (xx[k2] - xx[k1])
            b = yy[k1] - m * xx[k1]
            Acc[sum(nsegs[:i]) + arange(nsegs[i]), nb + i]         = m * baseMVA
            Acc[sum(nsegs[:i]) + arange(nsegs[i]), nb + ng + i]    = -ones(nsegs[i])
            bcc[sum(nsegs[:i]) + arange(nsegs[i])]                 = -b

        AA = vstack([
            ## reference angle
            sparse((ones(1), (zeros(1), ref)), (1, nb+ng+nc)),
            ## real power flow eqns
            hstack([B,  -sparse((ones(ng), (gen[on, GEN_BUS], arange(ng))), (nb, ng)), sparse((nb, nc))]),
            ## lower limit on Pg
            hstack([sparse((ng, nb)), -speye(ng, ng), sparse((ng, nc))]),
            ## upper limit on Pg
            hstack([sparse((ng, nb)),  speye(ng, ng), sparse((ng, nc))]),
            ## flow limit on Pf
            hstack([ Bf, sparse((nl, ng + nc))]),
            ## flow limit on Pt
            hstack([-Bf, sparse((nl, ng + nc))]),
            ## cost constraints
            Acc
        ])

        bb = r_[
            Va[ref],                                            ## reference angle
            -(bus[:, PD] + bus[:, GS]) / baseMVA - Pbusinj,     ## real power flow eqns
            -gen[on, PMIN] / baseMVA,                           ## lower limit on Pg
            gen[on, PMAX] / baseMVA,                            ## upper limit on Pg
            branch[:, RATE_A] / baseMVA - Pfinj,                ## flow limit on Pf
            branch[:, RATE_A] / baseMVA + Pfinj,                ## flow limit on Pt
            bcc                                                 ## cost constraints
        ]

        ## run LP solver
        ppopt['OPF_NEQ']   = nb + 1         ## set number of equality constraints
        c = r_[   zeros(nb + ng),
                  ones(nc)      ]

        x, lmbda, _, success = pp_lp(c, AA, bb, None, None, x, ppopt['OPF_NEQ'],
                                     skip_lpsolve=False, print_level=0)
    else:
        AA = vstack([
            sparse((ones(1), (zeros(1), ref)), (1, nb+ng)),
            hstack([B,  -sparse((ones(ng), (gen[on, GEN_BUS], arange(ng))), (nb, ng))]),
            hstack([sparse((ng, nb)), -speye(ng, ng)]),
            hstack([sparse((ng, nb)),  speye(ng, ng)]),
            hstack([ Bf, sparse((nl, ng))]),
            hstack([-Bf, sparse((nl, ng))])
        ])

        bb = r_[
            Va[ref],                                            ## reference angle
            -(bus[:, PD] + bus[:, GS]) / baseMVA - Pbusinj,     ## real power flow eqns
            -gen[on, PMIN] / baseMVA,                           ## lower limit on Pg
            gen[on, PMAX] / baseMVA,                            ## upper limit on Pg
            branch[:, RATE_A] / baseMVA - Pfinj,                ## flow limit on Pf
            branch[:, RATE_A] / baseMVA + Pfinj,                ## flow limit on Pt
        ]

        ## set up objective function of the form:  0.5 * x'*H*x + c'*x
        polycf = dot(pcost[:, COST:COST + 3], diag(r_[baseMVA**2, baseMVA, 1]))  ## coeffs for Pg in p.u.
        H = sparse((2 * polycf[:, 0], (arange(j3, j4), arange(j3, j4))), (nb+ng, nb+ng))
        c = r_[ zeros(nb), polycf[:, 1] ]

        ## run QP solver
        ppopt['OPF_NEQ'] = nb + 1            ## set number of equality constraints
        if verbose > 1:                      ## print QP progress for verbose levels 2 & 3
            qpverbose = 1
        else:
            qpverbose = -1

        x, lmbda, _, success = pp_qp(H, c, AA, bb, [], [], x, ppopt['OPF_NEQ'],
                                       True, print_level=0)


    #hstack([sparse((ng, nb)), -speye(ng, ng), sparse((ng, nc))]).todense()
    #gen[on, PMAX] / baseMVA
    #-sparse((ones(ng), (gen[on, GEN_BUS], arange(ng))), (nb, ng) ).todense()
    #hstack([B, -sparse((opnes(ng), (gen[on, GEN_BUS], arange(ng))), (nb, ng)), sparse((nb, nc))]).todense().shape

#    if formulation == 2:             ## piece-wise linear costs
#        H = sparse((nb + ng + nc, nb + ng + nc))
#        c = r_[   zeros(nb + ng),
#                  ones(nc)      ]
#    else:                            ## polynomial costs
#        polycf = dot(pcost[:, COST:COST + 3], diag(r_[baseMVA**2, baseMVA, 1]))  ## coeffs for Pg in p.u.
#        H = sparse((2 * polycf[:, 0], (arange(j3, j4), arange(j3, j4))), (nb+ng, nb+ng))
#        c = r_[   zeros(nb),
#                  polycf[:, 1]    ]

#    if ppopt['SPARSE_QP'] == False: ## don't use sparse matrices
#        AA = AA.todense()
#        H  = H.todense()

#    if formulation == 2:             ## piece-wise linear costs
#        x, lmbda, _, success = pp_lp(c, AA, bb, None, None, x, ppopt['OPF_NEQ'])
#    else:
#        x, lmbda, _, success = pp_qp(H, c, AA, ll, uu, array([]), array([]), x, ppopt['OPF_NEQ'], qpverbose)

    info = success

    ## update solution data
    Va = x[j1:j2]
    Pg = x[j3:j4]

    f = sum(totcost(pcost, Pg * baseMVA))

    ##-----  calculate return values  -----
    ## update voltages & generator outputs
    bus[:, VM] = ones(nb)
    bus[:, VA] = Va * 180.0 / pi
    gen[on, PG] = Pg * baseMVA

    ## compute flows etc.
    branch[:, [QF, QT]] = zeros((nl, 2))
    branch[:, PF] = (Bf * Va + Pfinj) * baseMVA
    branch[:, PT] = -branch[:, PF]

    ## update lambda's and mu's
    bus[:, [LAM_P, LAM_Q, MU_VMIN, MU_VMAX]] = zeros((nb, 4))
    gen[:, [MU_PMIN, MU_PMAX, MU_QMIN, MU_QMAX]] = zeros((gen.shape[0], 4))
    branch[:, [MU_SF, MU_ST]] = zeros((nl, 2))
    bus[:, LAM_P]       = lmbda[i1:i2] / baseMVA
    gen[on, MU_PMIN]    = lmbda[i3:i4] / baseMVA
    gen[on, MU_PMAX]    = lmbda[i5:i6] / baseMVA
    branch[:, MU_SF]    = lmbda[i7:i8] / baseMVA
    branch[:, MU_ST]    = lmbda[i9:i10] / baseMVA

    # convert to original external bus ordering
    bus, gen, branch, areas = int2ext(i2e, bus, gen, branch, areas)

    # Now create output matrices with all lines, all generators, committed and
    # non-committed
    buso = bus.copy()
    geno = genorg.copy()
    brancho = branchorg.copy()
    geno[comgen, :] = gen
    brancho[onbranch, :]  = branch
    # And zero out appropriate fields of non-comitted generators and lines
    tmp = zeros(len(offgen))
    geno[offgen, PG] = tmp
    geno[offgen, QG] = tmp
    geno[offgen, MU_PMAX] = tmp
    geno[offgen, MU_PMIN] = tmp
    tmp = zeros(len(offbranch))
    brancho[offbranch, PF] = tmp
    brancho[offbranch, QF] = tmp
    brancho[offbranch, PT] = tmp
    brancho[offbranch, QT] = tmp
    brancho[offbranch, MU_SF] = tmp
    brancho[offbranch, MU_ST] = tmp

    ## compute elapsed time
    et = time() - t0

    return buso, geno, brancho, f, success, info, et
