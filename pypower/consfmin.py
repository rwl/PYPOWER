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

"""Evaluates nonlinear constraints and their Jacobian for OPF.
"""

from numpy import ones, conj, exp, r_, arange, zeros

from scipy.sparse import vstack, hstack, issparse, csr_matrix as sparse

from idx_gen import GEN_BUS, PG, QG
from idx_brch import F_BUS, T_BUS, RATE_A

from makeSbus import makeSbus
from dSbus_dV import dSbus_dV
from dIbr_dV import dIbr_dV
from dSbr_dV import dSbr_dV
from dAbr_dV import dAbr_dV


def eval_g(x, user_data=None):
    """Calculates the constraint values and returns an array.

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    parms = user_data['parms']
    baseMVA = user_data['baseMVA']
    gen = user_data['gen']
    bus = user_data['bus']
    branch = user_data['branch']
    Ybus = user_data['Ybus']
    Yf = user_data['Yf']
    Yt = user_data['Yt']
    ppopt = user_data['ppopt']
    A = user_data['A']

    ## unpack needed parameters
    thbas = parms['thbas']
    thend = parms['thend']
    vbas  = parms['vbas']
    vend  = parms['vend']
    pgbas = parms['pgbas']
    pgend = parms['pgend']
    qgbas = parms['qgbas']
    qgend = parms['qgend']

    ## grab Pg & Qg
    Pg = x[pgbas:pgend]  ## active generation in p.u.
    Qg = x[qgbas:qgend]  ## reactive generation in p.u.

    ## put Pg & Qg back in gen
    gen[:, PG] = Pg * baseMVA  ## active generation in MW
    gen[:, QG] = Qg * baseMVA  ## reactive generation in MVAr

    ## rebuild Sbus
    Sbus = makeSbus(baseMVA, bus, gen) ## net injected power in p.u.

    ## ----- evaluate constraints -----
    ## reconstruct V
    Va = x[thbas:thend]
    Vm = x[vbas:vend]
    V = Vm * exp(1j * Va)

    ## evaluate power flow equations
    mis = V * conj(Ybus * V) - Sbus

    ##----- evaluate constraint function values -----
    ## first, the equality constraints (power flow)
    geq = r_[ mis.real,            ## active power mismatch for all buses
              mis.imag ]           ## reactive power mismatch for all buses

    ## then, the inequality constraints (branch flow limits)
    if ppopt['OPF_FLOW_LIM'] == 2:
        giq = r_[ abs(Yf * V) * branch[:, RATE_A] / baseMVA,     ## branch I limits (from bus)
                  abs(Yt * V) * branch[:, RATE_A] / baseMVA ]    ## branch I limits (to bus)
    else:
        ## compute branch power flows
        Sf = V[ branch[:, F_BUS].astype(int) ] * conj(Yf * V)  ## complex power injected at "from" bus (p.u.)
        St = V[ branch[:, T_BUS].astype(int) ] * conj(Yt * V)  ## complex power injected at "to" bus (p.u.)
        if ppopt['OPF_FLOW_LIM'] == 1:   ## active power limit, P (Pan Wei)
            giq = r_[ Sf.real - branch[:, RATE_A] / baseMVA,   ## branch real power limits (from bus)
                      St.real - branch[:, RATE_A] / baseMVA ]  ## branch real power limits (to bus)
        else:                ## apparent power limit, |S|
            giq = r_[ abs(Sf) - branch[:, RATE_A] / baseMVA,   ## branch apparent power limits (from bus)
                      abs(St) - branch[:, RATE_A] / baseMVA ]  ## branch apparent power limits (to bus)

    if A is not None and issparse(A):
        g = r_[geq, giq, A * x]
    else:
        g = r_[geq, giq]

    return g


def eval_jac_g(x, flag, user_data=None):
    """Calculates the Jacobi matrix.

    If the flag is true, returns a tuple (row, col) to indicate the
    sparse Jacobi matrix's structure.
    If the flag is false, returns the values of the Jacobi matrix
    with length nnzj.

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    Js = user_data['Js']
    if flag:
        return (Js.row, Js.col)
    else:
        parms = user_data['parms']
        gen = user_data['gen']
        branch = user_data['branch']
        Ybus = user_data['Ybus']
        Yf = user_data['Yf']
        Yt = user_data['Yt']
        ppopt = user_data['ppopt']
        A = user_data['A']

        ## unpack needed parameters
        nb = parms['nb']
        ng = parms['ng']
        nl = parms['nl']
        ny = parms['ny']
        nz = parms['nz']
        thbas = parms['thbas']
        thend = parms['thend']
        vbas  = parms['vbas']
        vend  = parms['vend']


        ## reconstruct V
        Va = x[thbas:thend]
        Vm = x[vbas:vend]
        V = Vm * exp(1j * Va)

        ## compute partials of injected bus powers
        dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)               ## w.r.t. V

        dSbus_dPg = sparse((-1  * ones(ng), (gen[:, GEN_BUS], arange(ng))), (nb, ng))    ## w.r.t. Pg
        dSbus_dQg = sparse((-1j * ones(ng), (gen[:, GEN_BUS], arange(ng))), (nb, ng))    ## w.r.t. Qg
        # TODO: double check ^

        ## construct Jacobian of equality constraints (power flow)
        if (ny + nz) > 0:
            dgeq = vstack([
                ## equality constraints
                hstack([dSbus_dVa.real, dSbus_dVm.real,
                    dSbus_dPg.real, dSbus_dQg.real, sparse((nb, ny + nz))]),  ## P mismatch
                hstack([dSbus_dVa.imag, dSbus_dVm.imag,
                    dSbus_dPg.imag, dSbus_dQg.imag, sparse((nb, ny + nz))])   ## Q mismatch
             ])
        else:
            dgeq = vstack([
                ## equality constraints
                hstack([dSbus_dVa.real, dSbus_dVm.real,
                    dSbus_dPg.real, dSbus_dQg.real]),  ## P mismatch
                hstack([dSbus_dVa.imag, dSbus_dVm.imag,
                    dSbus_dPg.imag, dSbus_dQg.imag])   ## Q mismatch
             ])

#        neg_Cg = sparse((-ones(ng), (gen[:, GEN_BUS], range(ng))), (nb, ng))
#        dgeq = vstack([
#            ## equality constraints
#            hstack([dSbus_dVa.real, dSbus_dVm.real,
#                neg_Cg, sparse((nb, ng)), sparse((nb, ny + nz))]),  ## P mismatch
#            hstack([dSbus_dVa.imag, dSbus_dVm.imag,
#                sparse((nb, ng)), neg_Cg, sparse((nb, ny + nz))])   ## Q mismatch
#         ])

        ## compute partials of Flows w.r.t. V
        if ppopt['OPF_FLOW_LIM'] == 2:     ## current
            dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = dIbr_dV(branch, Yf, Yt, V)
        else:                  ## power
            dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = dSbr_dV(branch, Yf, Yt, V)

        if ppopt['OPF_FLOW_LIM'] == 1:     ## real part of flow (active power)
            df_dVa = dFf_dVa.real
            df_dVm = dFf_dVm.real
            dt_dVa = dFt_dVa.real
            dt_dVm = dFt_dVm.real
        else:                  ## magnitude of flow (of complex power or current)
            df_dVa, df_dVm, dt_dVa, dt_dVm = \
                  dAbr_dV(dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft)

        ## construct Jacobian of inequality constraints (branch limits)
        dg = vstack([
            hstack([df_dVa, df_dVm, sparse((nl, 2 * ng + ny + nz))]),  ## "from" flow limit
            hstack([dt_dVa, dt_dVm, sparse((nl, 2 * ng + ny + nz))])   ## "to" flow limit
        ])

        ## true Jacobian organization
        if A is not None and issparse(A):
            J = vstack([ dgeq, dg, A ], 'csc')
        else:
            J = vstack([ dgeq, dg ], 'csc')

        ## FIXME: Extend PyIPOPT to handle changes in sparsity structure
        nnzj = Js.nnz
        Jd = zeros(nnzj)
        for i in xrange(nnzj):
            Jd[i] = J[Js.row[i], Js.col[i]]

        return Jd
