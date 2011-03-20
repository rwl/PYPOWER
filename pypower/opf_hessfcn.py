# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
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

from numpy import array, zeros, ones, exp, nonzero, r_
from scipy.sparse import csr_matrix, vstack, hstack

from idx_gen import PG, QG
from idx_brch import F_BUS, T_BUS
from idx_cost import MODEL, POLYNOMIAL

from polycost import polycost
from d2Sbus_dV2 import d2Sbus_dV2
from dSbr_dV import dSbr_dV
from dIbr_dV import dIbr_dV
from d2AIbr_dV2 import d2AIbr_dV2
from d2ASbr_dV2 import d2ASbr_dV2
from opf_costfcn import opf_costfcn
from opf_consfcn import opf_consfcn

def opf_hessfcn(x, lmbda, om, Ybus, Yf, Yt, ppopt, il=None, cost_mult=1.0):
    """Evaluates Hessian of Lagrangian for AC OPF.

    Hessian evaluation function for AC optimal power flow, suitable
    for use with MIPS or FMINCON's interior-point algorithm.

    @type x: array
    @param x: optimization vector
    @type lmbda: dict
    @param lmbda:
         - C{eqnonlin} : Lagrange multipliers on power balance equations
         - C{ineqnonlin} : Kuhn-Tucker multipliers on constrained branch flows
    @type om: opf_model
    @param om: OPF model object
    @type Ybus: spmatrix
    @param Ybus: bus admittance matrix
    @type Yf: spmatrix
    @param Yf: admittance matrix for "from" end of constrained branches
    @type: Yt: spmatrix
    @param: admittance matrix for "to" end of constrained branches
    @type ppopt: dict
    @param ppopt: PYPOWER options vector
    @type il: array
    @param il: (optional) vector of branch indices corresponding to
               branches with flow limits (all others are assumed to be
               unconstrained). The default is [1:nl] (all branches).
               YF and YT contain only the rows corresponding to IL.
    @type cost_mult: float
    @param cost_mult: (optional) Scale factor to be applied to the cost
                      (default = 1).

    @rtype: spmatrix
    @return: Hessian of the Lagrangian.

    Examples:
        Lxx = opf_hessfcn(x, lmbda, om, Ybus, Yf, Yt, ppopt)
        Lxx = opf_hessfcn(x, lmbda, om, Ybus, Yf, Yt, ppopt, il)
        Lxx = opf_hessfcn(x, lmbda, om, Ybus, Yf, Yt, ppopt, il, cost_mult)

    @see: L{opf_costfcn}, L{opf_consfcn}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ##----- initialize -----
    ## unpack data
    mpc = om.get_mpc()
    baseMVA, bus, gen, branch, gencost = \
        mpc["baseMVA"], mpc["bus"], mpc["gen"], mpc["branch"], mpc["gencost"]
    cp = om.get_cost_params()
    N, Cw, H, dd, rh, kk, mm = \
        cp["N"], cp["Cw"], cp["H"], cp["dd"], cp["rh"], cp["kk"], cp["mm"]
    vv = om.get_idx()

    ## unpack needed parameters
    nb = bus.shape[0]          ## number of buses
    nl = branch.shape[0]       ## number of branches
    ng = gen.shape[0]          ## number of dispatchable injections
    nxyz = len(x)              ## total number of control vars of all types

    ## set default constrained lines
    if il is None:
        il = range(nl)            ## all lines have limits by default
    nl2 = len(il)           ## number of constrained lines

    ## grab Pg & Qg
    Pg = x[vv["i1"]["Pg"]:vv["iN"]["Pg"]]  ## active generation in p.u.
    Qg = x[vv["i1"]["Qg"]:vv["iN"]["Qg"]]  ## reactive generation in p.u.

    ## put Pg & Qg back in gen
    gen[:, PG] = Pg * baseMVA  ## active generation in MW
    gen[:, QG] = Qg * baseMVA  ## reactive generation in MVAr

    ## reconstruct V
    Va = zeros(nb)
    Va = x[vv["i1"]["Va"]:vv["iN"]["Va"]]
    Vm = x[vv["i1"]["Vm"]:vv["iN"]["Vm"]]
    V = Vm * exp(1j * Va)
    nxtra = nxyz - 2 * nb
    pcost = gencost[range(ng), :]
    if gencost.shape[0] > ng:
        qcost = gencost[range(ng + 1, 2 * ng), :]
    else:
        qcost = array([])

    ## ----- evaluate d2f -----
    d2f_dPg2 = csr_matrix((ng, 1))               ## w.r.t. p.u. Pg
    d2f_dQg2 = csr_matrix((ng, 1))               ## w.r.t. p.u. Qg
    ipolp = nonzero(pcost[:, MODEL] == POLYNOMIAL)
    d2f_dPg2[ipolp] = \
            baseMVA**2 * polycost(pcost[ipolp, :], Pg[ipolp] * baseMVA, 2)
    if any(qcost):          ## Qg is not free
        ipolq = nonzero(qcost[:, MODEL] == POLYNOMIAL)
        d2f_dQg2[ipolq] = \
                baseMVA**2 * polycost(qcost[ipolq, :], Qg[ipolq] * baseMVA, 2)
    i = range(vv["i1"]["Pg"], vv["iN"]["Pg"]) + \
        range(vv["i1"]["Qg"], vv["iN"]["Qg"])
    d2f = csr_matrix((vstack([d2f_dPg2, d2f_dQg2]).toarray().flatten(),
                      (i, i)), shape=(nxyz, nxyz))

    ## generalized cost
    if any(N):
        nw = N.shape[0]
        r = N * x - rh                  ## Nx - rhat
        iLT = nonzero(r < -kk)          ## below dead zone
        iEQ = nonzero(r == 0 & kk == 0) ## dead zone doesn't exist
        iGT = nonzero(r > kk)           ## above dead zone
        iND = r_[iLT, iEQ, iGT]         ## rows that are Not in the Dead region
        iL = nonzero(dd == 1)           ## rows using linear function
        iQ = nonzero(dd == 2)           ## rows using quadratic function
        LL = csr_matrix((1.0, (iL, iL)), (nw, nw))
        QQ = csr_matrix((1.0, (iQ, iQ)), (nw, nw))
        kbar = csr_matrix((r_[  ones(len(iLT), 1),
                               zeros(len(iEQ), 1),
                               -ones(len(iGT), 1)], (iND, iND)), nw, nw) * kk
        rr = r + kbar                  ## apply non-dead zone shift
        M = csr_matrix((mm[iND], (iND, iND)), (nw, nw))  ## dead zone or scale
        diagrr = csr_matrix((rr, range(nw), range(nw)), (nw, nw))

        ## linear rows multiplied by rr(i), quadratic rows by rr(i)^2
        w = M * (LL + QQ * diagrr) * rr
        HwC = H * w + Cw
        AA = N.T * M * (LL + 2 * QQ * diagrr)
        d2f = d2f + AA * H * AA.T + 2 * N.T * M * QQ * \
                csr_matrix((HwC, range(nw), range(nw)), (nw, nw)) * N
    d2f = d2f * cost_mult

    ##----- evaluate Hessian of power balance constraints -----
    nlam = len(lmbda["eqnonlin"]) / 2
    lamP = lmbda["eqnonlin"][:nlam]
    lamQ = lmbda["eqnonlin"][nlam:nlam + nlam]
    Gpaa, Gpav, Gpva, Gpvv = d2Sbus_dV2(Ybus, V, lamP)
    Gqaa, Gqav, Gqva, Gqvv = d2Sbus_dV2(Ybus, V, lamQ)

    d2G = vstack([
            hstack([
                vstack([hstack([Gpaa, Gpav]),
                        hstack([Gpva, Gpvv])]).real +
                vstack([hstack([Gqaa, Gqav]),
                        hstack([Gqva, Gqvv])]).imag,
                csr_matrix((2 * nb, nxtra))]),
            hstack([
                csr_matrix((nxtra, 2 * nb)),
                csr_matrix((nxtra, nxtra))
            ])
        ], "csr")

    ##----- evaluate Hessian of flow constraints -----
    nmu = len(lmbda["ineqnonlin"]) / 2
    muF = lmbda["ineqnonlin"][:nmu]
    muT = lmbda["ineqnonlin"][nmu:nmu + nmu]
    if ppopt[24] == 2:       ## current
        dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It = dIbr_dV(Yf, Yt, V)
        Hfaa, Hfav, Hfva, Hfvv = d2AIbr_dV2(dIf_dVa, dIf_dVm, If, Yf, V, muF)
        Htaa, Htav, Htva, Htvv = d2AIbr_dV2(dIt_dVa, dIt_dVm, It, Yt, V, muT)
    else:
        f = branch[il, F_BUS]    ## list of "from" buses
        t = branch[il, T_BUS]    ## list of "to" buses
        ## connection matrix for line & from buses
        Cf = csr_matrix((ones(nl2), (range(nl2), f)), (nl2, nb))
        ## connection matrix for line & to buses
        Ct = csr_matrix((ones(nl2), (range(nl2), t)), (nl2, nb))
        dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St = \
            dSbr_dV(branch[il,:], Yf, Yt, V)
        if ppopt[24] == 1:     ## real power
            Hfaa, Hfav, Hfva, Hfvv = d2ASbr_dV2(dSf_dVa.real(), dSf_dVm.real(),
                                                Sf.real(), Cf, Yf, V, muF)
            Htaa, Htav, Htva, Htvv = d2ASbr_dV2(dSt_dVa.real(), dSt_dVm.real(),
                                                St.real(), Ct, Yt, V, muT)
        else:                  ## apparent power
            Hfaa, Hfav, Hfva, Hfvv = \
                d2ASbr_dV2(dSf_dVa, dSf_dVm, Sf, Cf, Yf, V, muF)
            Htaa, Htav, Htva, Htvv = \
                d2ASbr_dV2(dSt_dVa, dSt_dVm, St, Ct, Yt, V, muT)

    d2H = vstack([
            hstack([
                vstack([hstack([Hfaa, Hfav]),
                        hstack([Hfva, Hfvv])]) +
                vstack([hstack([Htaa, Htav]),
                        hstack([Htva, Htvv])]),
                csr_matrix((2 * nb, nxtra))
            ]),
            hstack([
                csr_matrix((nxtra, 2 * nb)),
                csr_matrix((nxtra, nxtra))
            ])
        ], "csr")

    ##-----  do numerical check using (central) finite differences  -----
    if 0:
        nx = len(x)
        step = 1e-5
        num_d2f = csr_matrix((nx, nx))
        num_d2G = csr_matrix((nx, nx))
        num_d2H = csr_matrix((nx, nx))
        for i in range(nx):
            xp = x
            xm = x
            xp[i] = x[i] + step / 2
            xm[i] = x[i] - step / 2
            # evaluate cost & gradients
            fp, dfp = opf_costfcn(xp, om)
            fm, dfm = opf_costfcn(xm, om)
            # evaluate constraints & gradients
            Hp, Gp, dHp, dGp = opf_consfcn(xp, om, Ybus, Yf, Yt, ppopt, il)
            Hm, Gm, dHm, dGm = opf_consfcn(xm, om, Ybus, Yf, Yt, ppopt, il)
            num_d2f[:, i] = cost_mult * (dfp - dfm) / step
            num_d2G[:, i] = (dGp - dGm) * lmbda["eqnonlin"]   / step
            num_d2H[:, i] = (dHp - dHm) * lmbda["ineqnonlin"] / step
        d2f_err = max(max(abs(d2f - num_d2f)))
        d2G_err = max(max(abs(d2G - num_d2G)))
        d2H_err = max(max(abs(d2H - num_d2H)))
        if d2f_err > 1e-6:
            print 'Max difference in d2f: %g' % d2f_err
        if d2G_err > 1e-5:
            print 'Max difference in d2G: %g' % d2G_err
        if d2H_err > 1e-6:
            print 'Max difference in d2H: %g' % d2H_err

    return d2f + d2G + d2H
