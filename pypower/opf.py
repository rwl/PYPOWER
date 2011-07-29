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

"""Solves an optimal power flow.
"""

from sys import stdout

from time import time

from numpy import array, arange, r_, any
from numpy import flatnonzero as find

from pypower.ppoption import ppoption
from pypower.loadcase import loadcase
from pypower.opf_form import opf_form
from pypower.printpf import printpf
from pypower.dcopf import dcopf
from pypower.have_fcn import have_fcn
from pypower.pqcost import pqcost
from pypower.poly2pwl import poly2pwl
from pypower.opf_slvr import opf_slvr
from pypower.lpopf import lpopf
from pypower.ipoptopf import ipoptopf

from pypower.idx_gen import GEN_STATUS, QMIN, QMAX, PMIN, PMAX

from pypower.idx_cost import MODEL, PW_LINEAR, POLYNOMIAL


def opf(*args):
    """Solves an optimal power flow.

    For an AC OPF, if the OPF algorithm is not set explicitly in the options,
    it will choose the best available solver, searching in the following order:
    MINOPF, fmincon, constr.

    [bus, gen, branch, f, success] = opf(casefile, ppopt)

    [bus, gen, branch, f, success] = opf(casefile, A, l, u, ppopt)

    [bus, gen, branch, f, success] = opf(baseMVA, bus, gen, branch, ...
                                     areas, gencost, ppopt)

    [bus, gen, branch, f, success] = opf(baseMVA, bus, gen, branch, ...
                                     areas, gencost, A, l, u, ppopt)

    [bus, gen, branch, f, success] = opf(baseMVA, bus, gen, branch, ...
                                     areas, gencost, A, l, u, ppopt, ...
                                     N, fparm, H, Cw)

    [bus, gen, branch, f, success] = opf(baseMVA, bus, gen, branch, ...
                                     areas, gencost, A, l, u, ppopt, ...
                                     N, fparm, H, Cw, z0, zl, zu)

    [bus, gen, branch, f, success, info, et, g, jac, xr, pimul] = opf(casefile)

    The data for the problem can be specified in one of 3 ways: (1) the name of
    a case file which defines the data matrices baseMVA, bus, gen, branch,
    areas and gencost, (2) a struct containing the data matrices as fields, or
    (3) the data matrices themselves.

    When specified, A, l, u represent additional linear constraints on the
    optimization variables, l <= A*[x; z] <= u. For an explanation of the
    formulation used and instructions for forming the A matrix, type
    'help genform'.

    A generalized cost on all variables can be applied if input arguments
    N, fparm, H and Cw are specified.  First, a linear transformation
    of the optimization variables is defined by means of r = N * [x; z].
    Then, to each element of r a function is applied as encoded in the
    fparm matrix (see manual or type 'help generalcost').  If the
    resulting vector is now named w, then H and Cw define a quadratic
    cost on w:  (1/2)*w'*H*w + Cw * w . H and N should be sparse matrices
    and H should also be symmetric.

    The additional linear constraints and generalized cost are only available
    for solvers which use the generalized formulation, namely fmincon and
    MINOPF.

    The optional ppopt vector specifies MATPOWER options. Type 'help ppoption'
    for details and default values.

    The solved case is returned in the data matrices, bus, gen and branch. Also
    returned are the final objective function value (f) and a flag which is
    true if the algorithm was successful in finding a solution (success).
    Additional optional return values are an algorithm specific return status
    (info), elapsed time in seconds (et), the constraint vector (g), the
    Jacobian matrix (jac), and the vector of variables (xr) as well
    as the constraint multipliers (pimul).

    Rules for A matrix: If the user specifies an A matrix that has more columns
    than the number of "x" (OPF) variables, then there are extra linearly
    constrained "z" variables.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    nargin = len(args)

    # Sort out input arguments
    # passing filename or dict
    if isinstance(args[0], basestring) or isinstance(args[0], dict):
        #---- fmincopf(baseMVA,  bus, gen, branch, areas, gencost, Au,    lbu, ubu, ppopt, N,  fparm, H, Cw, z0, zl, zu)
        # 12  fmincopf(casefile, Au,  lbu, ubu,    ppopt, N,       fparm, H,   Cw,  z0,    zl, zu)
        # 9   fmincopf(casefile, Au,  lbu, ubu,    ppopt, N,       fparm, H,   Cw)
        # 5   fmincopf(casefile, Au,  lbu, ubu,    ppopt)
        # 4   fmincopf(casefile, Au,  lbu, ubu)
        # 2   fmincopf(casefile, ppopt)
        # 1   fmincopf(casefile)
        if nargin in [1, 2, 4, 5, 9, 12]:
            casefile = args[0]
            if nargin == 12:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu,  ubu, ppopt,  N, fparm = args
                zu    = fparm
                zl    = N
                z0    = ppopt
                Cw    = ubu
                H     = lbu
                fparm = Au
                N     = gencost
                ppopt = areas
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 9:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu = args
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = ubu
                H     = lbu
                fparm = Au
                N     = gencost
                ppopt = areas
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 5:
                baseMVA, bus, gen, branch, areas = args
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = array([])
                fparm = array([])
                N     = array([])
                ppopt = areas
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 4:
                baseMVA, bus, gen, branch = args
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = array([])
                fparm = array([])
                N     = array([])
                ppopt = ppoption()
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 2:
                baseMVA, bus = args
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = array([])
                fparm = array([])
                N     = array([])
                ppopt = bus
                ubu   = array([])
                lbu   = array([])
                Au    = array([])
            elif nargin == 1:
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = array([])
                fparm = array([])
                N     = array([])
                ppopt = ppoption()
                ubu   = array([])
                lbu   = array([])
                Au    = array([])
        else:
            raise ValueError, 'opf.m: Incorrect input parameter order, number or type'

        baseMVA, bus, gen, branch, areas, gencost = loadcase(casefile)
    else:    # passing individual data matrices
        #---- fmincopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 17  fmincopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 14  fmincopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu, ppopt, N, fparm, H, Cw)
        # 10  fmincopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu, ppopt)
        # 9   fmincopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu)
        # 7   fmincopf(baseMVA, bus, gen, branch, areas, gencost, ppopt)
        # 6   fmincopf(baseMVA, bus, gen, branch, areas, gencost)
        if nargin in [6, 7, 9, 10, 14, 17]:
            if nargin == 17:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt,  N, fparm, H, Cw, z0, zl, zu = args
            elif nargin == 14:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt,  N, fparm, H, Cw = args
                zu = array([])
                zl = array([])
                z0 = array([])
            elif nargin == 10:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt = args
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = array([])
                fparm = array([])
                N = array([])
            elif nargin == 9:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu = args
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = array([])
                fparm = array([])
                N = array([])
                ppopt = ppoption()
            elif nargin == 7:
                baseMVA, bus, gen, branch, areas, gencost, ppopt = args
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = array([])
                fparm = array([])
                N = array([])
                ubu = array([])
                lbu = array([])
                Au = array([])
            elif nargin == 6:
                baseMVA, bus, gen, branch, areas, gencost = args
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = array([])
                fparm = array([])
                N = array([])
                ppopt = ppoption()
                ubu = array([])
                lbu = array([])
                Au = array([])
        else:
            raise ValueError, 'opf: Incorrect input parameter order, number or type'

    if N.shape[0] > 0:
        if N.shape[0] != fparm.shape[0] or N.shape[0] != H.shape[0] or \
                N.shape[0] != H.shape[1] or N.shape[0] != len(Cw):
            raise ValueError, 'opf.m: wrong dimensions in generalized cost parameters'

        if Au.shape[0] > 0 and N.shape[1] != Au.shape[1]:
            raise ValueError, 'opf.m: A and N must have the same number of columns'

    if len(ppopt) == 0:
        ppopt = ppoption()

    ##----- initialization -----
    ## options
    verbose = ppopt['VERBOSE']
    ## number of points to evaluate when converting
    ## polynomials to piece-wise linear
    npts = ppopt['OPF_POLY2PWL_PTS']

    ##-----  check/convert costs, set default algorithm  -----
    ## get cost model, check consistency
    model = gencost[:, MODEL]
    comgen = find(gen[:, GEN_STATUS] > 0)
    if gencost.shape[0] == 2 * gen.shape[0]:
        comgen = r_[comgen, comgen]
    i_pwln = find(model[comgen] == PW_LINEAR)
    i_poly = find(model[comgen] == POLYNOMIAL)

    ## initialize optional output args
    g = array([]); jac = array([]); xr = array([]); pimul = array([])

    # Start clock
    t1 = time()

    ## set algorithm
    dc = ppopt['PF_DC']
    if dc:  # DC OPF
        bus, gen, branch, f, success, info, et = dcopf(baseMVA, bus, gen,
                                                branch, areas, gencost, ppopt)
    else:  # AC optimal power flow requested
        if any((model != PW_LINEAR) & (model != POLYNOMIAL)):
            raise ValueError, 'opf.m: unknown generator cost model in gencost data'

        if ppopt['OPF_ALG'] == 0:  # OPF_ALG not set, choose best option
#            if have_fcn('minopf'):
#                ppopt['OPF_ALG'] = 500  # MINOS generalized
#            if have_fcn('pdipm'):
#                ppopt['OPF_ALG'] = 540  # PDIPM generalized
            if have_fcn('pyipopt'):
                ppopt['OPF_ALG'] = 520  # IPOPT generalized
            ## use default for this cost model
            elif any(i_pwln):      ## some piece-wise linear, use appropriate alg
                ppopt['OPF_ALG'] = ppopt['OPF_ALG_PWL']
                if any(i_poly) and verbose:
                    stdout.write('opf: not all generators use same cost model, all will be converted\n       to piece-wise linear\n')
            else:                    ## must all be polynomial
                ppopt['OPF_ALG'] = ppopt['OPF_ALG_POLY']

        alg = ppopt['OPF_ALG']
        formulation = opf_form(alg)  # 1, 2 or 5

        ## check cost model/algorithm consistency
        if any( i_pwln ) and formulation == 1:
            raise ValueError, 'opf.m: algorithm #d does not handle piece-wise linear cost functions' % alg
            ###################################################################################
            ##  Eventually put code here to fit polynomials to piece-wise linear as needed.
            ###################################################################################

        if (formulation != 5) and len(Au) > 0:
            raise ValueError, 'opf.m: Selected algorithm cannot handle general linear constraints'

        ## convert polynomials to piece-wise linear
        if any(i_poly) and formulation == 2:
            if verbose:
                stdout.write('converting from polynomial to piece-wise linear cost model\n')

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
        if formulation == 5:  # Generalized
            if alg == 500:       # MINOS
                raise NotImplementedError, 'MINOS solver not available'
#                if not have_fcn('minopf'):
#                    raise ValueError, 'opf: OPF_ALG ' + str(alg) + ' requires MINOPF'
#
#                bus, gen, branch, f, success, info, et, g, jac, xr, pimul = \
#                    mopf(baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu,
#                         ppopt, N, fparm, H, Cw, z0, zl, zu)

            elif alg == 520:   # IPOPT
                if not have_fcn('pyipopt'):
                    raise ValueError, 'opf: OPF_ALG ' + str(alg) + ' requires ' + \
                        'PyIPOPT (see https://projects.coin-or.org/Ipopt)'

                bus, gen, branch, f, success, info, et, g, jac, xr, pimul = \
                    ipoptopf(baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu,
                             ppopt, N, fparm, H, Cw, z0, zl, zu)

            elif alg == 540 or alg == 545 or alg == 550:  # PDIPM_OPF, SCPDIPM_OPF, or TRALM_OPF
                raise NotImplementedError, 'PDIPM solver not implemented'
#                if alg == 540:       # PDIPM_OPF
#                    if not have_fcn('pdipmopf'):
#                        raise ValueError, 'opf.m: OPF_ALG ' + str(alg) + ' requires PDIPMOPF'
#
#                elif alg == 545:       # SCPDIPM_OPF
#                    if not have_fcn('scpdipmopf'):
#                        raise ValueError, 'opf.m: OPF_ALG ' + str(alg) + ' requires '
#                        'SCPDIPMOPF (see http://www.pserc.cornell.edu/tspopf/)'
#
#                elif alg == 550:       # TRALM_OPF
#                    if not have_fcn('tralmopf'):
#                        raise ValueError, 'opf.m: OPF_ALG ' + str(alg) + ' requires TRALMOPF'
#
#                bus, gen, branch, f, success, info, et, g, jac, xr, pimul = \
#                    tspopf(baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu,
#                           ppopt, N, fparm, H, Cw, z0, zl, zu)

        else:
            if opf_slvr(alg) == 0:           ## use CONSTR
                raise NotImplementedError
#                if not have_fcn('constr'):
#                    raise ValueError, 'opf.m: OPF_ALG ' + str(alg) + ' requires '
#                    'constr (Optimization Toolbox 1.x/2.x)'
#
#                ## set some options
#                if ppopt['CONSTR_MAX_IT'] == 0:
#                    ppopt['CONSTR_MAX_IT'] = 2 * bus.shape[0] + 150  ## set max number of iterations for constr
#
#                ## run optimization
#                bus, gen, branch, f, success, info, et, g, jac = \
#                    copf(baseMVA, bus, gen, branch, areas, gencost, ppopt)

            else:                            ## use LPCONSTR
                bus, gen, branch, f, success, info, et = lpopf(baseMVA,
                    bus, gen ,branch, areas, gencost, ppopt)

    ## compute elapsed time
    et = time() - t1

    return bus.copy(), gen, branch, f, success, info, et, g, jac, xr, pimul
