# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

from time import time
from os.path import exists
import logging

from numpy import array, ones, zeros, any, nonzero, pi, Inf, r_

from scipy.sparse import csr_matrix

from idx_bus import BUS_TYPE, PD, GS, VA, VM, VMIN, VMAX, MU_VMIN, REF
from idx_gen import GEN_BUS, PG, QG, PMIN, PMAX, QMIN, QMAX, VG, MU_QMIN, \
    MU_PMAX, MU_PMIN
from idx_brch import PF, QF, PT, QT, MU_SF, MU_ST, RATE_A, MU_ANGMIN, MU_ANGMAX
from idx_cost import MODEL, NCOST, COST, PW_LINEAR, POLYNOMIAL

from ext2int import ext2int
from opf_args import opf_args
from pqcost import pqcost
from makeBdc import makeBdc
from makeAvl import makeAvl
from makeApq import makeApq
from makeAang import makeAang
from makeAy import makeAy
from opf_model import opf_model
from run_userfcn import run_userfcn
from ppver import ppver
from dcopf_solver import dcopf_solver
from pipsopf_solver import pipsopf_solver
from update_mupq import update_mupq
from int2ext import int2ext
from printpf import printpf

logger = logging.getLogger(__name__)

def opf(*args, **kw_args):
    """Solves an optimal power flow.

    Returns either a RESULTS struct and an optional SUCCESS flag, or individual
    data matrices, the objective function value and a SUCCESS flag. In the
    latter case, there are additional optional return values. See Examples
    below for the possible calling syntax options.

    The data for the problem can be specified in one of three ways:
    (1) a string (ppc) containing the file name of a MATPOWER case
      which defines the data matrices baseMVA, bus, gen, branch, and
      gencost (areas is not used at all, it is only included for
      backward compatibility of the API).
    (2) a struct (ppc) containing the data matrices as fields.
    (3) the individual data matrices themselves.

    The optional user parameters for user constraints (A, l, u), user costs
    (N, fparm, H, Cw), user variable initializer (z0), and user variable
    limits (zl, zu) can also be specified as fields in a case struct,
    either passed in directly or defined in a case file referenced by name.

    When specified, A, l, u represent additional linear constraints on the
    optimization variables, l <= A*[x z] <= u. If the user specifies an A
    matrix that has more columns than the number of "x" (OPF) variables,
    then there are extra linearly constrained "z" variables. For an
    explanation of the formulation used and instructions for forming the
    A matrix, see the manual.

    A generalized cost on all variables can be applied if input arguments
    N, fparm, H and Cw are specified.  First, a linear transformation
    of the optimization variables is defined by means of r = N * [x z].
    Then, to each element of r a function is applied as encoded in the
    fparm matrix (see manual). If the resulting vector is named w,
    then H and Cw define a quadratic cost on w: (1/2)*w'*H*w + Cw * w .
    H and N should be sparse matrices and H should also be symmetric.

    The optional mpopt vector specifies MATPOWER options. If the OPF
    algorithm is not explicitly set in the options MATPOWER will use
    the default solver, based on a primal-dual interior point method.
    For the AC OPF this is OPF_ALG = 560, unless the TSPOPF optional
    package is installed, in which case the default is 540. For the
    DC OPF, the default is OPF_ALG_DC = 200. See MPOPTION for
    more details on the available OPF solvers and other OPF options
    and their default values.

    The solved case is returned either in a single results struct (described
    below) or in the individual data matrices, bus, gen and branch. Also
    returned are the final objective function value (f) and a flag which is
    true if the algorithm was successful in finding a solution (success).
    Additional optional return values are an algorithm specific return status
    (info), elapsed time in seconds (et), the constraint vector (g), the
    Jacobian matrix (jac), and the vector of variables (xr) as well
    as the constraint multipliers (pimul).

    The single results struct is a MATPOWER case struct (ppc) with the
    usual baseMVA, bus, branch, gen, gencost fields, along with the
    following additional fields:

        C{order}      see 'help ext2int' for details of this field
        C{et}         elapsed time in seconds for solving OPF
        C{success}    1 if solver converged successfully, 0 otherwise
        C{om}         OPF model object, see 'help opf_model'
        C{x}          final value of optimization variables (internal order)
        C{f}          final objective function value
        C{mu}         shadow prices on ...
            C{var}
                C{l}  lower bounds on variables
                C{u}  upper bounds on variables
            C{nln}
                C{l}  lower bounds on non-linear constraints
                C{u}  upper bounds on non-linear constraints
            C{lin}
                C{l}  lower bounds on linear constraints
                C{u}  upper bounds on linear constraints
        C{g}          (optional) constraint values
        C{dg}         (optional) constraint 1st derivatives
        C{df}         (optional) obj fun 1st derivatives (not yet implemented)
        C{d2f}        (optional) obj fun 2nd derivatives (not yet implemented)
        C{raw}        raw solver output in form returned by MINOS, and more
            C{xr}     final value of optimization variables
            C{pimul}  constraint multipliers
            C{info}   solver specific termination code
            C{output} solver specific output information
               C{alg} algorithm code of solver used
        C{var}
            C{val}    optimization variable values, by named block
                C{Va}     voltage angles
                C{Vm}     voltage magnitudes (AC only)
                C{Pg}     real power injections
                C{Qg}     reactive power injections (AC only)
                C{y}      constrained cost variable (only if have pwl costs)
                (other) any user defined variable blocks
            C{mu}     variable bound shadow prices, by named block
                C{l}  lower bound shadow prices
                    C{Va}, C{Vm}, C{Pg}, C{Qg}, C{y}, (other)
                C{u}  upper bound shadow prices
                    C{Va}, C{Vm}, C{Pg}, C{Qg}, C{y}, (other)
        C{nln}    (AC only)
            C{mu}     shadow prices on non-linear constraints, by named block
                C{l}  lower bounds
                    C{Pmis}   real power mismatch equations
                    C{Qmis}   reactive power mismatch equations
                    C{Sf}     flow limits at "from" end of branches
                    C{St}     flow limits at "to" end of branches
                C{u}  upper bounds
                    C{Pmis}, C{Qmis}, C{Sf}, C{St}
        C{lin}
            C{mu}     shadow prices on linear constraints, by named block
                C{l}  lower bounds
                    C{Pmis}   real power mistmatch equations (DC only)
                    C{Pf}     flow limits at "from" end of branches (DC only)
                    C{Pt}     flow limits at "to" end of branches (DC only)
                    C{PQh}    upper portion of gen PQ-capability curve(AC only)
                    C{PQl}    lower portion of gen PQ-capability curve(AC only)
                    C{vl}     constant power factor constraint for loads
                    (AC only)
                    C{ycon}   basin constraints for CCV for pwl costs
                    (other) any user defined constraint blocks
                C{u}  upper bounds
                    C{Pmis}, C{Pf}, C{Pf}, C{PQh}, C{PQl}, C{vl}, C{ycon},
                    (other)
        C{cost}       user defined cost values, by named block

    @see: L{runopf}, L{dcopf}, L{UOPF}, L{caseformat}
    """
    ##----- initialization -----
    t0 = time()         ## start timer

    ## process input arguments
    ppc, ppopt = opf_args(args, kw_args)

    ## options
    dc  = ppopt[10]        ## PF_DC        : 1 = DC OPF, 0 = AC OPF
    alg = ppopt[11]        ## OPF_ALG
    verbose = ppopt[31]    ## VERBOSE

    ## set AC OPF algorithm code
    if not dc:
        if alg == 0:                   ## OPF_ALG not set, choose best option
            if exists('pdipmopf'):
                alg = 540              ## PDIPM
        else:
            raise NotImplementedError  ## MIPS
        ## update deprecated algorithm codes to new, generalized equivalents
        if alg == 100 | alg == 200:   ## CONSTR
            raise NotImplementedError
        elif alg == 120 | alg == 220: ## dense LP
            raise NotImplementedError
        elif alg == 140 | alg == 240: ## sparse (relaxed) LP
            raise NotImplementedError
        elif alg == 160 | alg == 260: ## sparse (full) LP
            raise NotImplementedError
        ppopt[11] = alg

    ## data dimensions
    nb   = ppc["bus"].shape[0]    ## number of buses
    nl   = ppc["branch"].shape[0] ## number of branches
    ng   = ppc["gen"].shape[0]    ## number of dispatchable injections
    if ppc.has_key('A'):
        nusr = ppc["A"].shape[0]  ## number of linear user constraints
    else:
        nusr = 0
    if ppc.has_key('N'):
        nw = ppc["N"].shape[0]    ## number of general cost vars, w
    else:
        nw = 0

    ## add zero columns to bus, gen, branch for multipliers, etc if needed
    if ppc["bus"].shape[1] < MU_VMIN:
        ppc["bus"] = r_[ppc["bus"], zeros((nb, MU_VMIN - ppc["bus"].shape[1]))]
    if ppc["gen"].shape[1] < MU_QMIN:
        ppc["gen"] = r_[ppc["gen"], zeros((ng, MU_QMIN - ppc["gen"].shape[1]))]
    if ppc["branch"].shape[1] < MU_ANGMAX:
        ppc["branch"] = \
            r_[ppc["branch"], zeros((nl, MU_ANGMAX - ppc["branch"].shape[1]))]

    if dc:
        ## ignore reactive costs for DC
        ppc["gencost"] = pqcost(ppc["gencost"], ng)

        ## reduce A and/or N from AC dimensions to DC dimensions, if needed
        if nusr | nw:
            ## Vm and Qg columns
            acc = r_[nb + range(nb), 2 * nb + ng + range(ng)]
            if nusr & ppc["A"].shape[1] >= 2 * nb + 2 * ng:
                ## make sure there aren't any constraints on Vm or Qg
                if any(any(ppc["A"][:, acc])):
                    logger.error('opf: attempting to solve DC OPF with user '
                                 'constraints on Vm or Qg')
                ppc["A"][:, acc] = array([])       ## delete Vm and Qg columns
            if nw & ppc["N"].shape[1] >= 2 * nb + 2 * ng:
                ## make sure there aren't any costs on Vm or Qg
                if any(any(ppc["N"][:, acc])):
                    logger.error('opf: attempting to solve DC OPF with user '
                                 'costs on Vm or Qg')
                ppc["N"][:, acc] = array([])       ## delete Vm and Qg columns

    ## convert single-block piecewise-linear costs into linear polynomial cost
    p1 = nonzero(ppc["gencost"][:, MODEL] == PW_LINEAR &
                 ppc["gencost"][:, NCOST] == 2)
    # p1 = []
    if any(p1):
        x0 = ppc["gencost"][p1, COST]
        y0 = ppc["gencost"][p1, COST+1]
        x1 = ppc["gencost"][p1, COST+2]
        y1 = ppc["gencost"][p1, COST+3]
        m = (y1 - y0) / (x1 - x0)
        b = y0 - m * x0
        ppc["gencost"][p1, MODEL] = POLYNOMIAL
        ppc["gencost"][p1, NCOST] = 2
        ppc["gencost"][p1, COST:COST + 1] = r_[m, b]

    ## convert to internal numbering, remove out-of-service stuff
    ppc = ext2int(ppc)

    ## update dimensions
    nb   = ppc["bus"].shape[0]    ## number of buses
    nl   = ppc["branch"].shape[0] ## number of branches
    ng   = ppc["gen"].shape[0]    ## number of dispatchable injections

    ## create (read-only) copies of individual fields for convenience
    baseMVA, bus, gen, branch, gencost, Au, lbu, ubu, mpopt, \
        N, fparm, H, Cw, z0, zl, zu, userfcn = opf_args(ppc, ppopt)

    ## warn if there is more than one reference bus
    refs = nonzero(bus[:, BUS_TYPE] == REF)
    if len(refs) > 1 & verbose > 0:
        errstr = 'opf: Warning: Multiple reference buses.\n' \
            '     For a system with islands, a reference bus in each\n' \
            '     island may help convergence, but in a fully connected\n' \
            '     system such a situation is probably not reasonable.'
        print errstr

    ## set up initial variables and bounds
    Va   = bus[:, VA] * (pi / 180)
    Vm   = bus[:, VM]
    Vm[gen[:, GEN_BUS]] = gen[:, VG]  ## buses with gens, init Vm from gen data
    Pg   = gen[:, PG] / baseMVA
    Qg   = gen[:, QG] / baseMVA
    Pmin = gen[:, PMIN] / baseMVA
    Pmax = gen[:, PMAX] / baseMVA
    Qmin = gen[:, QMIN] / baseMVA
    Qmax = gen[:, QMAX] / baseMVA

    if dc:               ## DC model
        ## more problem dimensions
        nv    = 0            ## number of voltage magnitude vars
        nq    = 0            ## number of Qg vars
        q1    = array([])    ## index of 1st Qg column in Ay

        ## power mismatch constraints
        B, Bf, Pbusinj, Pfinj = makeBdc(baseMVA, bus, branch)
        ## Pbus w.r.t. Pg
        neg_Cg = csr_matrix((-1, (gen[:, GEN_BUS], range(ng))), (nb, ng))
        Amis = r_[B, neg_Cg]
        bmis = -(bus[:, PD] + bus[:, GS]) / baseMVA - Pbusinj

        ## branch flow constraints
        il = nonzero(branch[:, RATE_A] != 0 & branch[:, RATE_A] < 1e10)
        nl2 = len(il)         ## number of constrained lines
        lpf = -Inf * ones(nl2)
        upf = branch[il, RATE_A] / baseMVA - Pfinj[il]
        upt = branch[il, RATE_A] / baseMVA + Pfinj[il]

        user_vars = ['Va', 'Pg']
        ycon_vars = ['Pg', 'y']
    else:                ## AC model
        ## more problem dimensions
        nv    = nb           ## number of voltage magnitude vars
        nq    = ng           ## number of Qg vars
        q1    = 1 + ng         ## index of 1st Qg column in Ay

        ## dispatchable load, constant power factor constraints
        Avl, lvl, uvl  = makeAvl(baseMVA, gen)

        ## generator PQ capability curve constraints
        Apqh, ubpqh, Apql, ubpql, Apqdata = makeApq(baseMVA, gen)

        user_vars = ['Va', 'Vm', 'Pg', 'Qg']
        ycon_vars = ['Pg', 'Qg', 'y']

    ## voltage angle reference constraints
    Vau = Inf * ones(nb)
    Val = -Vau
    Vau[refs] = Va[refs]
    Val[refs] = Va[refs]

    ## branch voltage angle difference limits
    Aang, lang, uang, iang  = makeAang(baseMVA, branch, nb, mpopt)

    ## basin constraints for piece-wise linear gen cost variables
    if alg == 545 | alg == 550:     ## SC-PDIPM or TRALM, no CCV cost vars
        ny = 0
        Ay = csr_matrix((0, ng + nq))
        by = array([])
    else:
        ## piece-wise linear costs
        ipwl = nonzero(gencost[:, MODEL] == PW_LINEAR)
        ny = ipwl.shape[0]   ## number of piece-wise linear cost vars
        Ay, by = makeAy(baseMVA, ng, gencost, 1, q1, 1 + ng + nq)

    ## more problem dimensions
    nx = nb+nv + ng+nq  ## number of standard OPF control variables
    if nusr:
        nz = ppc["A"].shape[1] - nx ## number of user z variables
        if nz < 0:
            logger.error('opf: user supplied A matrix must have at least %d '
                         'columns.' % nx)
    else:
        nz = 0               ## number of user z variables
        if nw:                 ## still need to check number of columns of N
            if ppc["N"].shape[1] != nx:
                logger.error('opf: user supplied N matrix must have %d '
                             'columns.' % nx)

    ## construct OPF model object
    om = opf_model(ppc)
    if dc:
        om = om.userdata('Bf', Bf)
        om = om.userdata('Pfinj', Pfinj)
        om = om.add_vars('Va', nb, Va, Val, Vau)
        om = om.add_vars('Pg', ng, Pg, Pmin, Pmax)
        om = om.add_constraints('Pmis', Amis, bmis, bmis, ['Va', 'Pg']) ## nb
        om = om.add_constraints('Pf',  Bf[il,:], lpf, upf, ['Va'])      ## nl
        om = om.add_constraints('Pt', -Bf[il,:], lpf, upt, ['Va'])      ## nl
        om = om.add_constraints('ang', Aang, lang, uang, ['Va'])        ## nang
    else:
        om = om.add_vars('Va', nb, Va, Val, Vau)
        om = om.add_vars('Vm', nb, Vm, bus[:, VMIN], bus[:, VMAX])
        om = om.add_vars('Pg', ng, Pg, Pmin, Pmax)
        om = om.add_vars('Qg', ng, Qg, Qmin, Qmax)
        om = om.add_constraints('Pmis', nb, 'non-linear')
        om = om.add_constraints('Qmis', nb, 'non-linear')
        om = om.add_constraints('Sf', nl, 'non-linear')
        om = om.add_constraints('St', nl, 'non-linear')
        om = om.add_constraints('PQh', Apqh, [], ubpqh, ['Pg', 'Qg']) ## npqh
        om = om.add_constraints('PQl', Apql, [], ubpql, ['Pg', 'Qg']) ## npql
        om = om.add_constraints('vl',  Avl, lvl, uvl, ['Pg', 'Qg'])   ## nvl
        om = om.add_constraints('ang', Aang, lang, uang, ['Va'])      ## nang

    ## y vars, constraints for piece-wise linear gen costs
    if ny > 0:
        om = om.add_vars(om, 'y', ny)
        om = om.add_constraints(om, 'ycon', Ay, [], by, ycon_vars)    ## ncony

    ## add user vars, constraints and costs (as specified via A, ..., N, ...)
    if nz > 0:
        om = om.add_vars('z', nz, z0, zl, zu)
        user_vars[-1] = 'z'
    if nusr:
        om = om.add_constraints('usr', ppc.A, lbu, ubu, user_vars)    ## nusr
    if nw:
        user_cost = {}
        user_cost["N"] = ppc["N"]
        user_cost["Cw"] = Cw
        if any(fparm):
            user_cost["dd"] = fparm[:, 1]
            user_cost["rh"] = fparm[:, 2]
            user_cost["kk"] = fparm[:, 3]
            user_cost["mm"] = fparm[:, 4]
        if any(H):
            user_cost["H"] = H
        om = om.add_costs('usr', user_cost, user_vars)

    ## execute userfcn callbacks for 'formulation' stage
    om = run_userfcn(userfcn, 'formulation', om)

    ## build user-defined costs
    om = om.build_cost_params()

    ## get indexing
    vv, ll, nn = om.get_idx()

    ## select optional solver output args
    output = {'g': array([]), 'dg': array([])}

    ## call the specific solver
    if verbose > 0:
        v = ppver('all')
        print 'PYPOWER Version %s, %s' % (v["Version"], v["Date"])
    if dc:
        if verbose > 0:
            print ' -- DC Optimal Power Flow'
        results, success, raw = dcopf_solver(om, mpopt, output)
    else:
        ##-----  call specific AC OPF solver  -----
        if verbose > 0:
            print ' -- AC Optimal Power Flow'
        if alg == 500:                                 ## MINOPF
            raise NotImplementedError
        elif alg == 300:                               ## CONSTR
            raise NotImplementedError
        elif alg == 320 | alg == 340 | alg == 360:     ## LP
            raise NotImplementedError
        elif alg == 520:                               ## FMINCON
            raise NotImplementedError
        elif alg == 540 | alg == 545 | alg == 550:
            if alg == 540:       # PDIPM_OPF
                raise NotImplementedError
            elif alg == 545:     # SCPDIPM_OPF
                raise NotImplementedError
            elif alg == 550:     # TRALM_OPF
                raise NotImplementedError
        elif alg == 560 | alg == 565:                 ## PIPS
            results, success, raw = pipsopf_solver(om, mpopt, output)
    if not raw.has_key('output') or \
       not raw["output"].has_key('alg') or \
       not any(raw["output"]["alg"]):
        raw["output"]["alg"] = alg
    if results.has_key('g'):
        g = results["g"]
    if results.has_key('dg'):
        jac = results["dg"]

    if success:
        if not dc:
            ## copy bus voltages back to gen matrix
            results["gen"][:, VG] = \
                results["bus"][results["gen"][:, GEN_BUS], VM]

            ## gen PQ capability curve multipliers
            if ll["N"]["PQh"] > 0 | ll["N"]["PQl"] > 0:
                mu_PQh = results["mu"]["lin"]["l"][
                        ll["i1"]["PQh"]:ll["iN"]["PQh"]
                    ] - results["mu"]["lin"]["u"][
                        ll["i1"]["PQh"]:["ll"]["iN"]["PQh"]
                    ]
                mu_PQl = results["mu"]["lin"]["l"][
                        ll["i1"]["PQl"]:ll["iN"]["PQl"]
                    ] - results["mu"]["lin"]["u"][
                        ll["i1"]["PQl"]:ll["iN"]["PQl"]
                    ]
                results["gen"] = \
                    update_mupq(baseMVA, results.gen, mu_PQh, mu_PQl, Apqdata)

        ## angle limit constraint multipliers
        if ll.N.ang > 0:
            results["branch"][iang, MU_ANGMIN] = \
                results["mu"]["lin"]["l"][
                        ll["i1"]["ang"]:ll["iN"]["ang"]
                    ] * pi / 180
            results["branch"][iang, MU_ANGMAX] = \
                results["mu"]["lin"]["u"][
                        ll["i1"]["ang"]:ll["iN"]["ang"]
                    ] * pi / 180

    ## assign values and limit shadow prices for variables
    om_var_order = om.get('var', 'order')
    for k in range(len(om_var_order)):
        name = om_var_order[k]
        if om.getN('var', name):
            idx = range(vv["i1"][name], vv["iN"][name])
            results["var"]["val"]["name"] = results["x"][idx]
            results["var"]["mu"]["l"][name] = results["mu"]["var"]["l"][idx]
            results["var"]["mu"]["u"][name] = results["mu"]["var"]["u"][idx]

    ## assign shadow prices for linear constraints
    om_lin_order = om.get('lin', 'order')
    for k in range(len(om_lin_order)):
        name = om_lin_order[k]
        if om.getN('lin', name):
            idx = range(ll["i1"][name], ll["iN"][name])
            results["lin"]["mu"]["l"][name] = results["mu"]["lin"]["l"][idx]
            results["lin"]["mu"]["u"][name] = results["mu"]["lin"]["u"][idx]

    ## assign shadow prices for non-linear constraints
    if not dc:
        om_nln_order = om.get('nln', 'order')
        for k in range(len(om_nln_order)):
            name = om_nln_order[k]
            if om.getN('nln', name):
                idx = range(nn["i1"][name], nn["iN"][name])
                results["nln"]["mu"]["l"][name] = \
                    results["mu"]["nln"]["l"][idx]
                results["nln"]["mu"]["u"][name] = \
                    results["mu"]["nln"]["u"][idx]

    ## assign values for components of user cost
    om_cost_order = om.get('cost', 'order')
    for k in range(len(om_cost_order)):
        name = om_cost_order[k]
        if om.getN('cost', name):
            results["cost"][name] = om.compute_cost(results["x"], name)

    ## revert to original ordering, including out-of-service stuff
    results = int2ext(results)

    ## zero out result fields of out-of-service gens & branches
    if any(results["order"]["gen"]["status"]["off"]):
        results["gen"][results["order"]["gen"]["status"]["off"],
                r_[PG, QG, MU_PMAX, MU_PMIN]] = 0
    if any(results["order"]["branch"]["status"]["off"]):
        results["branch"][results["order"]["branch"]["status"]["off"],
                r_[PF, QF, PT, QT, MU_SF, MU_ST, MU_ANGMIN, MU_ANGMAX]] = 0

    ## if single-block PWL costs were converted to POLY, insert dummy y into x
    ## Note: The "y" portion of x will be messed up, but everything else
    ##       should be in the expected locations.
    if any(p1) & alg != 545 & alg != 550:
        if dc:
            nx = vv["N"]["Pg"]
        else:
            nx = vv["N"]["Qg"]
        y = zeros(len(p1))
        raw["xr"] = r_[ raw["xr"][:nx], y, raw["xr"][nx + 1:] ]
        results["x"] = r_[ results["x"][:nx], y. results["x"][nx + 1:]]

    ## compute elapsed time
    et = time() - t0

    ## finish preparing output
#    if nargout > 0:
#        if nargout <= 2:
    results["et"] = et
    results["success"] = success
    results["raw"] = raw
#            busout = results
#            genout = success
#        else:
#            busout, genout, branchout, f, info, xr, pimul = \
#                results["bus"], results["gen"], results["branch"], \
#                results["f"], raw["info"], raw["xr"], raw["pimul"]
#    elif success:
#        results.et = et
#        results.success = success
#        printpf(results, 1, mpopt)

#    return busout, genout, branchout, f, success, info, et, g, jac, xr, pimul
    return results, success
