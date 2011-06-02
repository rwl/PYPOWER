# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

import sys

from numpy import ones, shape, zeros, arange, c_, flatnonzero as find

from scipy.sparse import csr_matrix as sparse

from pypower.ppoption import ppoption
from pypower.isload import isload
from pypower.uopf import uopf
from pypower.totcost import totcost

from pypower.idx_bus import BUS_I, LAM_P, LAM_Q
from pypower.idx_gen import PMIN, PMAX, GEN_BUS, QMIN, QMAX, PG, QG, GEN_STATUS
from pypower.idx_cost import MODEL, PW_LINEAR, STARTUP, SHUTDOWN

from pypower.extras.smartmarket.pricelimits import pricelimits
from pypower.extras.smartmarket.off2case import off2case
from pypower.extras.smartmarket.auction import auction

from pypower.extras.smartmarket.idx_disp import \
    PENALTY, QUANTITY, PRICE, FCOST, VCOST, SCOST


def smartmkt(ppc, offers, bids, mkt, ppopt=None):
    """Runs the PowerWeb smart market.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if ppopt == None:
        ppopt = ppoption  ## use default options

    ## options
    verbose = ppopt['VERBOSE']

    ## initialize some stuff
    G = find( not isload(ppc['gen']) )       ## real generators
    L = find(     isload(ppc['gen']) )       ## dispatchable loads
    nL = len(L)
    if 'Q' in offers or 'Q' in bids:
        haveQ = 1
    else:
        haveQ = 0

    if haveQ and mkt['auction_type'] != 0 and mkt['auction_type'] != 5:
        sys.stderr.write('smartmkt: Combined active/reactive power markets '
                'are only implemented for auction types 0 and 5')

    ## set power flow formulation based on market
    ppopt['PF_DC'] = mkt['OPF'] == 'DC'

    ## set up cost info & generator limits
    mkt['lim'] = pricelimits(mkt['lim'], 'Q' in offers or 'Q' in bids)
    gen, genoffer = off2case(ppc['gen'], ppc['gencost'], offers, bids, mkt['lim'])

    ## move Pmin and Pmax limits out slightly to avoid problems
    ## with lambdas caused by rounding errors when corner point
    ## of cost function lies at exactly Pmin or Pmax
    if any(find(genoffer[:, MODEL] == PW_LINEAR)):
        gg = find( not isload(gen) )      ## skip dispatchable loads
        gen[gg, PMIN] = gen[gg, PMIN] - 100 * ppopt['OPF_VIOLATION'] * ones(shape(gg))
        gen[gg, PMAX] = gen[gg, PMAX] + 100 * ppopt['OPF_VIOLATION'] * ones(shape(gg))

    ##-----  solve the optimization problem  -----
    ## attempt OPF
    ppc2 = ppc.copy()
    ppc2['gen'] = gen.copy()
    ppc2['gencost'] = genoffer.copy()
    r, success = uopf(ppc2, ppopt)
    bus, gen = r['bus'], r['gen']
    if verbose and not success:
        print '\nSMARTMARKET: non-convergent UOPF'

    ##-----  compute quantities, prices & costs  -----
    ## compute quantities & prices
    ng = shape(gen)[0]
    if success:      ## OPF solved case fine
        ## create map of external bus numbers to bus indices
        i2e = bus[:, BUS_I]
        e2i = sparse((max(i2e), 1))
        e2i[i2e] = arange(shape(bus)[0])

        ## get nodal marginal prices from OPF
        gbus    = e2i[gen[:, GEN_BUS]]                 ## indices of buses w/gens
        npP     = max([ shape(offers['P']['qty'])[1], shape(bids['P']['qty'])[1] ])
        rg = arange(ng)
        lamP    = sparse((bus[gbus, LAM_P], (rg, rg)), (ng, ng)) * ones((ng, npP)) ## real power prices
        lamQ    = sparse((bus[gbus, LAM_Q], (rg, rg)), (ng, ng)) * ones((ng, npP)) ## reactive power prices

        ## compute fudge factor for lamP to include price of bundled reactive power
        pf   = zeros((len(L), 1))                 ## for loads Q = pf * P
        Qlim =  (gen[L, QMIN] == 0) * gen[L, QMAX] + \
                (gen[L, QMAX] == 0) * gen[L, QMIN]
        pf = Qlim / gen[L, PMIN]

        gtee_prc = {}
        gtee_prc['offer'] = 1         ## guarantee that cleared offers are >= offers
        Poffer = offers['P']
        Poffer['lam'] = lamP[G, :]
        Poffer['total_qty'] = gen[G, PG]

        Pbid = bids['P']
        Pbid['total_qty'] = -gen[L, PG]
        if haveQ:
            Pbid['lam'] = lamP[L, :]   ## use unbundled lambdas
            gtee_prc['bid'] = 0       ## allow cleared bids to be above bid price
        else:
            rL = arange(nL)
            Pbid['lam'] = lamP[L, :] + sparse((pf, (rL, rL)), (nL, nL)) * lamQ[L, :]  ## bundled lambdas
            gtee_prc['bid'] = 1       ## guarantee that cleared bids are <= bids

        co = {}; cb = {}
        co['P'], cb['P'] = auction(Poffer, Pbid, mkt['auction_type'], mkt['lim']['P'], gtee_prc)

        if haveQ:
            npQ = max([ shape(offers['Q']['qty'])[1], shape(bids['Q']['qty'])[1] ])

            ## get nodal marginal prices from OPF
            lamQ    = sparse((bus(gbus, LAM_Q) (rg, rg)), (ng, ng)) * ones((ng, npQ)) ## reactive power prices

            Qoffer = offers['Q'].copy()
            Qoffer['lam'] = lamQ.copy()      ## use unbundled lambdas
            Qoffer['total_qty'] = (gen[:, QG] > 0) * gen[:, QG]

            Qbid = bids['Q']
            Qbid['lam'] = lamQ.copy()        ## use unbundled lambdas
            Qbid['total_qty'] = (gen[:, QG] < 0) * -gen[:, QG]

            ## too complicated to scale with mixed bids/offers
            ## (only auction_types 0 and 5 allowed)
            co['Q'], cb['Q'] = auction(Qoffer, Qbid, mkt['auction_type'], mkt['lim']['Q'], gtee_prc)

        quantity    = gen[:, PG]
        price       = zeros((ng, 1))
        price[G]    = co['P']['prc'][:, 0]   ## need these for prices for
        price[L]    = cb['P']['prc'][:, 0]   ## gens that are shut down
        if npP == 1:
            k = find( co['P']['qty'] )
            price[G[k]] = co['P']['prc'][k, :]
            k = find( cb['P']['qty'] )
            price[L[k]] = cb['P']['prc'][k, :]
        else:
            k = find( sum( co['P']['qty'].T ).T )
            price[G[k]] = sum( co['P']['qty'][k, :].T * co['P']['prc'][k, :].T ).T / sum( co['P']['qty'][k, :].T ).T
            k = find( sum( cb['P']['qty'].T ).T )
            price[L[k]] = sum( cb['P']['qty'][k, :].T * cb['P']['prc'][k, :].T ).T / sum( cb['P']['qty'][k, :].T ).T
    else:        ## did not converge even with imports
        quantity    = zeros((ng, 1))
        price       = mkt['lim']['P']['max_offer'] * ones((ng, 1))
        co['P']['qty'] = zeros(shape(offers['P']['qty']))
        co['P']['prc'] = zeros(shape(offers['P']['prc']))
        cb['P']['qty'] = zeros(shape(bids['P']['qty']))
        cb['P']['prc'] = zeros(shape(bids['P']['prc']))
        if haveQ:
            co['Q']['qty'] = zeros(shape(offers['Q']['qty']))
            co['Q']['prc'] = zeros(shape(offers['Q']['prc']))
            cb['Q']['qty'] = zeros(shape(bids['Q']['qty']))
            cb['Q']['prc'] = zeros(shape(bids['Q']['prc']))


    ## compute costs in $ (note, NOT $/hr)
    fcost   = mkt['t'] * totcost(ppc['gencost'], zeros((ng, 1)) )        ## fixed costs
    vcost   = mkt['t'] * totcost(ppc['gencost'], quantity     ) - fcost  ## variable costs
    scost   =   (not mkt['u0'] and gen[:, GEN_STATUS] >  0) * \
                       ppc['gencost'][:, STARTUP] + \
                ( mkt['u0'] and gen[:, GEN_STATUS] <= 0) * \
                       ppc['gencost'][:, SHUTDOWN]                  ## shutdown costs

    ## store in dispatch
    dispatch = zeros((ng, PENALTY))
    dispatch[:, [QUANTITY, PRICE, FCOST, VCOST, SCOST]] = c_[quantity, price, fcost, vcost, scost]

    return co, cb, r, dispatch, success
