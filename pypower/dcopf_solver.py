# Copyright (C) 2000-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

import logging

from numpy import array, zeros, ones, nonzero, any, diag, r_, pi, Inf, isnan
from scipy.sparse import csr_matrix, vstack, hstack

from idx_bus import *
from idx_gen import *
from idx_brch import *
from idx_cost import *

from qps_pips import qps_pips
from util import sub2ind

logger = logging.getLogger(__name__)

def dcopf_solver(om, ppopt, out_opt=None):
    """Solves a DC optimal power flow.

    Inputs are an OPF model object, a MATPOWER options vector and
    a struct containing fields (can be empty) for each of the desired
    optional output fields.

    Outputs are a RESULTS struct, SUCCESS flag and RAW output struct.

    RESULTS is a MATPOWER case struct (ppc) with the usual baseMVA, bus
    branch, gen, gencost fields, along with the following additional
    fields:
        .order      see 'help ext2int' for details of this field
        .x          final value of optimization variables (internal order)
        .f          final objective function value
        .mu         shadow prices on ...
            .var
                .l  lower bounds on variables
                .u  upper bounds on variables
            .lin
                .l  lower bounds on linear constraints
                .u  upper bounds on linear constraints
        .g          (optional) constraint values
        .dg         (optional) constraint 1st derivatives
        .df         (optional) obj fun 1st derivatives (not yet implemented)
        .d2f        (optional) obj fun 2nd derivatives (not yet implemented)

    SUCCESS     1 if solver converged successfully, 0 otherwise

    RAW         raw output in form returned by MINOS
        .xr     final value of optimization variables
        .pimul  constraint multipliers
        .info   solver specific termination code
        .output solver specific output information

    @see: L{opf}, L{qps_pypower}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if out_opt is None:
        out_opt = {}

    ## options
    verbose = ppopt[31]    ## VERBOSE
    alg     = ppopt[26]    ## OPF_ALG_DC

    if alg == 0:
        alg = 200  # Use PIPS

    ## unpack data
    ppc = om.get_ppc()
    baseMVA, bus, gen, branch, gencost = \
        ppc["baseMVA"], ppc["bus"], ppc["gen"], ppc["branch"], ppc["gencost"]
    cp = om.get_cost_params()
    N, H, Cw = cp["N"], cp["H"], cp["Cw"]
    fparm = array([cp["dd"], cp["rh"], cp["kk"], cp["mm"]])
    Bf = om.userdata('Bf')
    Pfinj = om.userdata('Pfinj')
    vv, ll = om.get_idx()

    ## problem dimensions
    ipol = nonzero(gencost[:, MODEL] == POLYNOMIAL) ## polynomial costs
    ipwl = nonzero(gencost[:, MODEL] == PW_LINEAR)  ## piece-wise linear costs
    nb = bus.shape[0]              ## number of buses
    nl = branch.shape[0]           ## number of branches
    nw = N.shape[0]                ## number of general cost vars, w
    ny = om.getN('var', 'y')      ## number of piece-wise linear costs
    nxyz = om.getN('var')        ## total number of control vars of all types

    ## linear constraints & variable bounds
    A, l, u = om.linear_constraints()
    x0, xmin, xmax = om.getv()

    ## set up objective function of the form: f = 1/2 * X'*HH*X + CC'*X
    ## where X = [x;y;z]. First set up as quadratic function of w,
    ## f = 1/2 * w'*HHw*w + CCw'*w, where w = diag(M) * (N*X - Rhat). We
    ## will be building on the (optionally present) user supplied parameters.

    ## piece-wise linear costs
    any_pwl = ny > 0
    if any_pwl:
        # Sum of y vars.
        Npwl = csr_matrix((ones(ny), (zeros(ny), range(vv["i1"]["y"], vv["iN"]["y"]))))
        Hpwl = csr_matrix((1, 1))
        Cpwl = array([1])
        fparm_pwl = array([[1, 0, 0, 1]])
    else:
        Npwl = None#zeros((0, nxyz))
        Hpwl = None#array([])
        Cpwl = array([])
        fparm_pwl = zeros((0, 4))

    ## quadratic costs
    npol = len(ipol)
    if any(nonzero(gencost[ipol, NCOST] > 3)):
        logger.error('DC opf cannot handle polynomial costs with higher '
                     'than quadratic order.')
    iqdr = nonzero(gencost[ipol, NCOST] == 3)
    ilin = nonzero(gencost[ipol, NCOST] == 2)
    polycf = zeros((npol, 3))         ## quadratic coeffs for Pg
    if any(iqdr):
        polycf[iqdr, :] = gencost[ipol[iqdr], COST:COST+2]
    polycf[ilin, 2:3] = gencost[ipol[ilin], COST:COST+1]
    polycf = polycf * diag([ baseMVA**2, baseMVA, 1])     ## convert to p.u.
    Npol = csr_matrix((ones(npol), # Pg vars
                       (range(npol), vv["i1"]["Pg"] + ipol)), (npol, nxyz))
    Hpol = csr_matrix((2 * polycf[:, 0],
                       (range(npol), range(npol))), (npol, npol))
    Cpol = polycf[:, 1]
    fparm_pol = ones(npol) * array([[1, 0, 0, 1]])

    ## combine with user costs
    NN = vstack([n for n in [Npwl, Npol, N] if n is not None], "csr")
    # FIXME: Zero dimension sparse matrices.
    if (Hpwl is not None) and (Hpol is not None):
        Hpwl = hstack([Hpwl, csr_matrix((any_pwl, npol + nw))])
        Hpol = hstack([csr_matrix((npol, any_pwl)), Hpol, csr_matrix((npol, nw))])
    if H is not None:
        H = hstack([csr_matrix((nw, any_pwl + npol)), H])
    HHw = vstack([h for h in [Hpwl, Hpol, H] if h is not None], "csr")
    CCw = r_[Cpwl, Cpol, Cw]
    ffparm = r_[fparm_pwl, fparm_pol, fparm]

    ## transform quadratic coefficients for w into coefficients for X
    nnw = any_pwl + npol + nw
    M = csr_matrix((ffparm[:, 3], (range(nnw), range(nnw))))
    MR = M * ffparm[:, 1]
    HMR = HHw * MR
    MN = M * NN
    HH = MN.T * HHw * MN
    CC = MN.T * (CCw - HMR)
    C0 = 1./2. * MR.T * HMR + sum(polycf[:, 2]) # Constant term of cost.

    ## set up input for QP solver
    opt = {'alg': alg, 'verbose': verbose}
    if alg == 200 or alg == 250:
        ## try to select an interior initial point
        Varefs = bus[bus[:, BUS_TYPE] == REF, VA] * (pi / 180)

        lb, ub = xmin, xmax;
        lb[xmin == -Inf] = -1e10   ## replace Inf with numerical proxies
        ub[xmax ==  Inf] =  1e10
        x0 = (lb + ub) / 2;
        # angles set to first reference angle
        x0[vv["i1"]["Va"]:vv["iN"]["Va"]] = Varefs[1]
        if ny > 0:
            ipwl = nonzero(gencost[:, MODEL] == PW_LINEAR)
            # largest y-value in CCV data
            c = gencost[sub2ind(gencost.shape, ipwl,
                                NCOST + 2 * gencost[ipwl, NCOST])]
            x0[vv["i1"]["y"]:vv["iN"]["y"]] = max(c) + 0.1 * abs(max(c))

        ## set up options
        feastol = ppopt[81]    ## PDIPM_FEASTOL
        gradtol = ppopt[82]    ## PDIPM_GRADTOL
        comptol = ppopt[83]    ## PDIPM_COMPTOL
        costtol = ppopt[84]    ## PDIPM_COSTTOL
        max_it  = ppopt[85]    ## PDIPM_MAX_IT
        max_red = ppopt[86]    ## SCPDIPM_RED_IT
        if feastol == 0:
            feastol = ppopt[16]    ## = OPF_VIOLATION by default
        opt["mips_opt"] = {  'feastol': feastol,
                             'gradtol': gradtol,
                             'comptol': comptol,
                             'costtol': costtol,
                             'max_it':  max_it,
                             'max_red': max_red,
                             'cost_mult': 1  }
    else:
        raise ValueError, "Unrecognised solver [%d]." % alg

    ##-----  run opf  -----
    x, f, info, output, lmbda = \
        qps_pips(HH, CC, A, l, u, xmin, xmax, x0, opt)
    success = (info == 1)


    ##-----  calculate return values  -----
    if not any(isnan(x)):
        ## update solution data
        Va = x[vv["i1"]["Va"]:vv["iN"]["Va"]]
        Pg = x[vv["i1"]["Pg"]:vv["iN"]["Pg"]]
        f = f + C0

        ## update voltages & generator outputs
        bus[:, VA] = Va * 180 / pi
        gen[:, PG] = Pg * baseMVA

        ## compute branch flows
        branch[:, [QF, QT]] = zeros(nl, 2)
        branch[:, PF] = (Bf * Va + Pfinj) * baseMVA
        branch[:, PT] = -branch[:, PF]

    ## package up results
    mu_l = lmbda["mu_l"]
    mu_u = lmbda["mu_u"]
    muLB = lmbda["lower"]
    muUB = lmbda["upper"]

    ## update Lagrange multipliers
    il = nonzero(branch[:, RATE_A] != 0 & branch[:, RATE_A] < 1e10)
    bus[:, [LAM_P, LAM_Q, MU_VMIN, MU_VMAX]] = zeros((nb, 4))
    gen[:, [MU_PMIN, MU_PMAX, MU_QMIN, MU_QMAX]] = zeros((gen.shape[0], 4))
    branch[:, [MU_SF, MU_ST]] = zeros((nl, 2))
    bus[:, LAM_P]       = (mu_u[ll["i1"]["Pmis"]:ll["iN"]["Pmis"]] -
                           mu_l[ll["i1"]["Pmis"]:ll["iN"]["Pmis"]]) / baseMVA
    branch[il, MU_SF]   = mu_u[ll["i1"]["Pf"]:ll["iN"]["Pf"]] / baseMVA
    branch[il, MU_ST]   = mu_u[ll["i1"]["Pt"]:ll["iN"]["Pt"]] / baseMVA
    gen[:, MU_PMIN]     = muLB[vv["i1"]["Pg"]:vv["iN"]["Pg"]] / baseMVA
    gen[:, MU_PMAX]     = muUB[vv["i1"]["Pg"]:vv["iN"]["Pg"]] / baseMVA

    pimul = r_[ # FIXME: column stack
      mu_l - mu_u,
     -ones(ny>0, 1), ## dummy entry corresponding to linear cost row in A
      muLB - muUB
    ]

    mu = { 'var': {'l': muLB, 'u': muUB},
           'lin': {'l': mu_l, 'u': mu_u} }

    results = ppc # FIXME: copy
    results["bus"], results["branch"], results["gen"], \
        results["om"], results["x"], results["mu"], results["f"] = \
            bus, branch, gen, om, x, mu, f

    raw = {'xr': x, 'pimul': pimul, 'info': info, 'output': output}

    return results, success, raw
