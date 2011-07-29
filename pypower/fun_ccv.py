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

"""Evaluates objective function & constraints for OPF.
"""

from numpy import array, zeros, angle, exp, conj, r_, arange
from numpy import flatnonzero as find

from pypower.pqcost import pqcost
from pypower.makeSbus import makeSbus

from pypower.idx_bus import VMIN, VMAX
from pypower.idx_gen import GEN_STATUS, PG, QG, PMIN, PMAX, QMIN, QMAX
from pypower.idx_brch import BR_STATUS, RATE_A, F_BUS, T_BUS

from pypower.idx_cost import NCOST, COST


def fun_ccv(x, baseMVA, bus, gen, gencost, branch, Ybus, Yf, Yt, V, ref, pv, pq, ppopt):
    """Evaluates objective function & constraints for OPF.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## generator info
    on = find(gen[:, GEN_STATUS] > 0)      ## which generators are on?

    ## sizes of things
    nb = bus.shape[0]
    npv = len(pv)
    npq = len(pq)
    ng = len(on)                        ## number of generators that are turned on

    ## check for costs for Qg
    pcost, qcost = pqcost(gencost, gen.shape[0], on)
    if len(qcost) == 0:       ## set number of cost variables
        ncv = ng           ## only Cp
    else:
        ncv = 2 * ng       ## Cp and Cq

    ## set up indexing for x
    j1 = 0;         j2  = npv              ## j1:j2    - V angle of pv buses
    j3 = j2;        j4  = j2 + npq         ## j3:j4    - V angle of pq buses
    j5 = j4;        j6  = j4 + nb          ## j5:j6    - V mag of all buses
    j7 = j6;        j8  = j6 + ng          ## j7:j8    - P of generators
    j9 = j8;        j10 = j8 + ng          ## j9:j10   - Q of generators
    j11 = j10;      j12 = j10 + ng         ## j11:j12  - Cp, cost of Pg

    ## grab Pg & Qg and their costs
    Pg = x[j7:j8]                              ## active generation in p.u.
    Qg = x[j9:j10]                             ## reactive generation in p.u.
    Cp = x[j11:j12]                            ## active costs in $/hr
    if ncv > ng:             ## no free VArs
        j13 = j12;  j14 = j12 + ng             ## j13:j14  - Cq, cost of Qg
        Cq = x[j13:j14]                        ## reactive costs in $/hr

    ##----- evaluate objective function -----
    ## put Pg & Qg back in gen
    gen[on, PG] = Pg * baseMVA                 ## active generation in MW
    gen[on, QG] = Qg * baseMVA                 ## reactive generation in MVAr

    ## compute objective value
    if ncv > ng:             ## no free VArs
        f = sum(r_[Cp, Cq])
    else:                    ## free VArs
        f = sum(Cp)

    ##----- evaluate constraints -----
    if nargout > 1:
        ## reconstruct V
        Va = zeros(nb)
        Va[r_[ref, pv, pq]] = r_[angle(V[ref]), x[j1:j2], x[j3:j4]]
        Vm = x[j5:j6]
        V = Vm * exp(1j * Va)

        ## rebuild Sbus
        Sbus = makeSbus(baseMVA, bus, gen)     ## net injected power in p.u.

        ## evaluate power flow equations
        mis = V * conj(Ybus * V) - Sbus;

        ## compute generator cost constraints ( costfcn @ Pg - Cp , etc.)
        Qcc = array([])
        nsegs = pcost[:, NCOST] - 1        ## number of cost constraints for each gen
        ncc = sum(nsegs)                   ## total number of cost constraints
        Pcc = zeros(ncc)
        for i in range(ng):
            xx = pcost[i,       COST:COST + 2*(nsegs(i)) + 1:2].T
            yy = pcost[i,   (COST+1):COST + 2*(nsegs(i)) + 2:2].T
            i1 = arange(nsegs[i])
            i2 = arange(1, nsegs[i] + 1)
            m = (yy[i2] - yy[i1]) / (xx[i2] - xx[i1])
            b = yy[i1] - m * xx[i1]
            Pcc[sum(nsegs[:i-1]) + arange(nsegs[i])] = \
                                m * gen[on[i], PG] + b - Cp[i]

        if ncv > ng:             ## no free VArs
            nsegs = qcost[:, NCOST] - 1        ## number of cost constraints for each gen
            ncc = sum(nsegs)                   ## total number of cost constraints
            Qcc = zeros(ncc)
            for i in range(ng):
                xx = qcost[i,       COST:( COST + 2*(nsegs(i)) + 1    ):2].T
                yy = qcost[i,   (COST+1):( COST + 2*(nsegs(i)) + 2):2].T
                i1 = arange(nsegs[i])
                i2 = arange(1, nsegs[i] + 1)
                m = (yy[i2] - yy[i1]) / (xx[i2] - xx[i1])
                b = yy[i1] - m * xx[i1]
                Qcc[sum(nsegs[:i - 1]) + arange(nsegs[i])] = \
                                    m * gen[on[i], QG] + b - Cq[i]

        ## compute line flow constraints
        br = find(branch[:, BR_STATUS])
        if ppopt['OPF_FLOW_LIM'] == 2:       ## branch current limits
            flow_limit = r_[
                abs(Yf[br, :] * V) - branch[br, RATE_A] / baseMVA,    ## from bus
                abs(Yt[br, :] * V) - branch[br, RATE_A] / baseMVA    ## to bus
             ]
        else:
            ## compute branch power flows
            Sf = V[branch[br, F_BUS].astype(int)] * conj(Yf[br, :] * V)   ## complex power injected at "from" bus (p.u.)
            St = V[branch[br, T_BUS].astype(int)] * conj(Yt[br, :] * V)   ## complex power injected at "to" bus (p.u.)
            if ppopt['OPF_FLOW_LIM'] == 1:   ## branch active power limits
                flow_limit = r_[
                    Sf.real - branch[br, RATE_A] / baseMVA,    ## from bus
                    St.real - branch[br, RATE_A] / baseMVA    ## to bus
                ]
            else:                ## branch apparent power limits
                flow_limit = r_[
                    abs(Sf) - branch[br, RATE_A] / baseMVA,     ## from bus
                    abs(St) - branch[br, RATE_A] / baseMVA     ## to bus
                ]

        ## compute constraint function values
        g = r_[
            ## equality constraints
            mis.real,                          ## active power mismatch for all buses
            mis.imag,                          ## reactive power mismatch for all buses

            ## inequality constraints (variable limits, voltage & generation)
            bus[:, VMIN] - Vm,                  ## lower voltage limit for var V
            Vm - bus[:, VMAX],                  ## upper voltage limit for var V
            gen[on, PMIN] / baseMVA - Pg,       ## lower generator P limit
            Pg - gen[on, PMAX] / baseMVA,       ## upper generator P limit
            gen[on, QMIN] / baseMVA - Qg,       ## lower generator Q limit
            Qg - gen[on, QMAX] / baseMVA,       ## upper generator Q limit

            ## inequality constraints (line flow limits)
            flow_limit,

            ## inequality cost constraints
            Pcc,
            Qcc
        ]


    return f, g
