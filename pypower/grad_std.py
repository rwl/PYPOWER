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

"""Evaluates gradients of objective function & constraints for OPF.
"""

from numpy import zeros, ones, angle, exp, r_, arange, polyval, polyder
from numpy import flatnonzero as find

from scipy.sparse import hstack, vstack, csc_matrix as sparse
from scipy.sparse import eye as speye

from pypower.pqcost import pqcost
from pypower.dSbus_dV import dSbus_dV
from pypower.dAbr_dV import dAbr_dV
from pypower.dIbr_dV import dIbr_dV
from pypower.dSbr_dV import dSbr_dV

from idx_gen import GEN_STATUS, GEN_BUS
from idx_brch import BR_STATUS
from idx_cost import NCOST, COST


def grad_std(x, baseMVA, bus, gen, gencost, branch, Ybus, Yf, Yt, V,
             ref, pv, pq, ppopt):
    """Evaluates gradients of objective function & constraints for OPF.

    Also, if a third output argument is specified, it will compute the 2nd
    derivative matrix for the objective function.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## generator info
    on = find(gen[:, GEN_STATUS] > 0)      ## which generators are on?
    gbus = gen[on, GEN_BUS]                ## what buses are they at?

    ## sizes of things
    nb = bus.shape[0]
    npv = len(pv)
    npq = len(pq)
    ng = len(on)                        ## number of generators that are turned on

    ## set up indexing for x
    j1 = 0;         j2  = npv              ## j1:j2    - V angle of pv buses
    j3 = j2;        j4  = j2 + npq         ## j3:j4    - V angle of pq buses
    j5 = j4;        j6  = j4 + nb          ## j5:j6    - V mag of all buses
    j7 = j6;        j8  = j6 + ng          ## j7:j8    - P of generators
    j9 = j8;        j10 = j8 + ng          ## j9:j10   - Q of generators

    ## grab Pg & Qg
    Pg = x[j7:j8]                              ## active generation in p.u.
    Qg = x[j9:j10]                             ## reactive generation in p.u.

    ##----- evaluate partials of objective function -----
    ## compute values of objective function partials
    pcost, qcost = pqcost(gencost, gen.shape[0], on)
    df_dPg = zeros(ng)
    df_dQg = zeros(ng)
    for i in range(ng):
        df_dPg[i] = polyval(polyder( pcost[ i, COST:(COST+pcost[i, NCOST]-0) ] ),
                        Pg[i] * baseMVA) * baseMVA   ## w.r.t p.u. Pg

    if len(qcost) > 0:                  ## Qg is not free
        for i in range(ng):
            df_dQg[i] = polyval(polyder( qcost[ i, COST:(COST+qcost[i, NCOST]-0)] ),
                        Qg[i] * baseMVA) * baseMVA   ## w.r.t p.u. Qg

    df = r_[  zeros(j6),               ## partial w.r.t. Va & Vm
              df_dPg,                  ## partial w.r.t. Pg
              df_dQg  ]                ## partial w.r.t. Qg

    ##----- evaluate partials of constraints -----
    if nargout > 1:
        ## reconstruct V
        Va = zeros(nb)
        Va[r_[ref, pv, pq]] = r_[angle(V[ref]), x[j1:j2], x[j3:j4]]
        Vm = x[j5:j6]
        V = Vm * exp(1j * Va)

        ## compute partials of injected bus powers
        dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)     ## w.r.t. V
        dSbus_dPg = sparse((-1  * ones(ng), (gbus, arange(ng))), (nb, ng))     ## w.r.t. Pg
        dSbus_dQg = sparse((-1j * ones(ng), (gbus, arange(ng))), (nb, ng))     ## w.r.t. Qg

        ## compute partials of line flow constraints
        br = find(branch[:, BR_STATUS])
        nbr = len(br)
        if ppopt['OPF_FLOW_LIM'] == 2:       ## branch current limits
            ## line limits are w.r.t current magnitude, so compute partials of current
            dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It = dIbr_dV(branch, Yf, Yt, V)
            dAf_dVa, dAf_dVm, dAt_dVa, dAt_dVm = \
                    dAbr_dV(dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It)
            dFlow_dV = vstack([
                hstack([dAf_dVa[br, r_[pv, pq]], dAf_dVm[br, :]]),             ## from bus
                hstack([dAt_dVa[br, r_[pv, pq]], dAt_dVm[br, :]])              ## to bus
            ])
        else:
            ## compute partials of branch power flows w.r.t. V
            dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St = dSbr_dV(branch, Yf, Yt, V)
            if ppopt['OPF_FLOW_LIM'] == 1:   ## branch active power limits
                dFlow_dV = vstack([
                    hstack([dSf_dVa[br, r_[pv, pq]].real, dSf_dVm[br, :].real]), ## from bus
                    hstack([dSt_dVa[br, r_[pv, pq]].real, dSt_dVm[br, :].real]) ## to bus
                ])
            else:                ## branch apparent power limits
                ## line limits are w.r.t apparent power, so compute partials of apparent power
                dAf_dVa, dAf_dVm, dAt_dVa, dAt_dVm = \
                                    dAbr_dV(dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St)
                dFlow_dV = vstack([
                    hstack([dAf_dVa[br, r_[pv, pq]], dAf_dVm[br, :]]),             ## from bus
                    hstack([dAt_dVa[br, r_[pv, pq]], dAt_dVm[br, :]])             ## to bus
                ])

        ## evaluate partials of constraints
        dg = vstack([
            ## equality constraints
            hstack([dSbus_dVa[:, r_[pv, pq]].real, dSbus_dVm.real,
                        dSbus_dPg.real, dSbus_dQg.real]),       ## P mismatch
            hstack([dSbus_dVa[:, r_[pv, pq]].imag, dSbus_dVm.imag,
                        dSbus_dPg.imag, dSbus_dQg.imag]),       ## Q mismatch

            ## inequality constraints (variable limits, voltage & generation)
            hstack([sparse((nb, j4)), -speye(nb, nb), sparse((nb, 2 * ng))]),      ## Vmin for var V
            hstack([sparse((nb, j4)),  speye(nb, nb), sparse((nb, 2 * ng))]),      ## Vmax for var V
            hstack([sparse((ng, j6)), -speye(ng, ng), sparse((ng, ng))]),        ## Pmin for generators
            hstack([sparse((ng, j6)),  speye(ng, ng), sparse((ng, ng))]),        ## Pmax for generators
            hstack([sparse((ng, j8)), -speye(ng, ng)]),                       ## Qmin for generators
            hstack([sparse((ng, j8)),  speye(ng, ng)]),                       ## Qmax for generators

            ## inequality constraints (line flow limits)
            hstack([dFlow_dV, sparse((2 * nbr, 2 * ng))])
        ]).T

        ## compute 2nd derivative of cost
        if nargout > 2:
            d2f_dPg2 = zeros(ng)
            d2f_dQg2 = zeros(ng)
            for i in range(ng):
                d2f_dPg2[i] = polyval(polyder(polyder( pcost[ i, COST:(COST + pcost[i, NCOST] - 0) ] )),
                                Pg[i] * baseMVA) * baseMVA**2     ## w.r.t p.u. Pg

            if len(qcost) > 0:                  ## Qg is not free
                for i in range(ng):
                    d2f_dQg2[i] = polyval(polyder(polyder( qcost[ i, COST:(COST + qcost[i, NCOST] - 1) ] )),
                                Qg[i] * baseMVA) * baseMVA**2     ## w.r.t p.u. Qg

            i = arange(j7, j10)
            d2f = sparse((r_[d2f_dPg2, d2f_dQg2], (i, i)))

    return df, dg, d2f
