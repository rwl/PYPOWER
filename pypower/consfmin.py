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

from numpy import ones, conj, exp, r_, arange

from scipy.sparse import vstack, hstack, csr_matrix as sparse

from idx_gen import GEN_BUS, PG, QG
from idx_brch import F_BUS, T_BUS, RATE_A

from makeSbus import makeSbus
from dSbus_dV import dSbus_dV
from dIbr_dV import dIbr_dV
from dSbr_dV import dSbr_dV
from dAbr_dV import dAbr_dV


def opf_consfcn(x, baseMVA, bus, gen, gencost, branch, areas, Ybus, Yf, Yt,
                ppopt, parms, ccost, N, fparm, H, Cw, return_partials=True):
    """Evaluates nonlinear constraints and their Jacobian for OPF.
    """
    ## constant
    j = 1j

    ## unpack needed parameters
#    nb = parms[0]
#    ng = parms[1]
#    nl = parms[2]
#    ny = parms[3]
#    # nx = parms[4]
#    # nvl = parms[5]
#    nz = parms[6]
#    # nxyz = parms[7]
#    thbas = parms[8]
#    thend = parms[9]
#    vbas = parms[10]
#    vend = parms[11]
#    pgbas = parms[12]
#    pgend = parms[13]
#    qgbas = parms[14]
#    qgend = parms[15]
#    # ybas = parms[16]
#    # yend = parms[17]
#    # zbas = parms[18]
#    # zend = parms[19]
#    # pmsmbas = parms[20]
#    # pmsmend = parms[21]
#    # qmsmbas = parms[22]
#    # qmsmend = parms[23]
#    # sfbas = parms[24]
#    # sfend = parms[25]
#    # stbas = parms[26]
#    # stend = parms[27]

    nb, ng, nl, ny, nx, nvl, nz, nxyz, thbas, thend, vbas, vend, pgbas, \
    pgend, qgbas, qgend, ybas, yend, zbas, zend, pmsmbas, pmsmend, qmsmbas, \
    qmsmend, sfbas, sfend, stbas, stend = parms

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
    V = Vm * exp(j * Va)

    ## evaluate power flow equations
    mis = V * conj(Ybus * V) - Sbus

    ##----- evaluate constraint function values -----
    ## first, the equality constraints (power flow)
    geq = r_[ mis.real,            ## active power mismatch for all buses
              mis.imag ]           ## reactive power mismatch for all buses

    ## then, the inequality constraints (branch flow limits)
    if ppopt['OPF_FLOW_LIM'] == 2:
        g = r_[ abs(Yf * V) * branch[:, RATE_A] / baseMVA,     ## branch I limits (from bus)
                abs(Yt * V) * branch[:, RATE_A] / baseMVA ]    ## branch I limits (to bus)
    else:
        ## compute branch power flows
        Sf = V[ branch[:, F_BUS].astype(int) ] * conj(Yf * V)  ## complex power injected at "from" bus (p.u.)
        St = V[ branch[:, T_BUS].astype(int) ] * conj(Yt * V)  ## complex power injected at "to" bus (p.u.)
        if ppopt['OPF_FLOW_LIM'] == 1:   ## active power limit, P (Pan Wei)
            g = r_[ Sf.real - branch[:, RATE_A] / baseMVA,   ## branch real power limits (from bus)
                    St.real - branch[:, RATE_A] / baseMVA ]  ## branch real power limits (to bus)
        else:                ## apparent power limit, |S|
            g = r_[ abs(Sf) - branch[:, RATE_A] / baseMVA,   ## branch apparent power limits (from bus)
                    abs(St) - branch[:, RATE_A] / baseMVA ]  ## branch apparent power limits (to bus)

    ##----- evaluate partials of constraints -----
    if return_partials:
        ## compute partials of injected bus powers
        dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)               ## w.r.t. V
        dSbus_dPg = sparse((-1 * ones(ng), (gen[:, GEN_BUS], arange(ng))), (nb, ng))    ## w.r.t. Pg
        dSbus_dQg = sparse((-j * ones(ng), (gen[:, GEN_BUS], arange(ng))), (nb, ng))    ## w.r.t. Qg

        ## construct Jacobian of equality constraints (power flow) and transpose it
        dgeq = vstack([
            ## equality constraints
            hstack([dSbus_dVa.real, dSbus_dVm.real,
                dSbus_dPg.real, dSbus_dQg.real, sparse((nb, ny + nz))]),  ## P mismatch
            hstack([dSbus_dVa.imag, dSbus_dVm.imag,
                dSbus_dPg.imag, dSbus_dQg.imag, sparse((nb, ny + nz))])   ## Q mismatch
         ]).T

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
        ## and transpose it so fmincon likes it
        dg = vstack([
            hstack([df_dVa, df_dVm, sparse((nl, 2 * ng + ny + nz))]),  ## "from" flow limit
            hstack([dt_dVa, dt_dVm, sparse((nl, 2 * ng + ny + nz))])   ## "to" flow limit
        ]).T

        return g, geq, dg, dgeq
    else:
        return g, geq
