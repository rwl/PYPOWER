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

from time import time

from numpy import array, ones, shape, zeros, flatnonzero as find

from pypower.ppoption import ppoption
from pypower.loadcase import loadcase
from pypower.isload import isload
from pypower.savecase import savecase

from pypower.extras.smartmarket.pricelimits import pricelimits
from pypower.extras.smartmarket.case2off import case2off
from pypower.extras.smartmarket.smartmkt import smartmkt
from pypower.extras.smartmarket.printmkt import printmkt


def runmarket(ppc='case9', offers=None, bids=None, mkt=None, ppopt=None,
              fname='', solvedcase=''):
    """Runs PowerWeb-style smart market.

    Computes the new generation and price schedules (cleared offers and bids)
    based on the C{offers} and C{bids} submitted. See C{off2case} for a
    description of the C{offers} and C{bids} arguments. C{mkt} is a dict with
    the following fields:
        auction_type - market used for dispatch and pricing
        t            - time duration of the dispatch period in hours
        u0           - vector of gen commitment status from prev period
        lim          - offer/bid/price limits (see 'help pricelimits')
        OPF          - 'AC' or 'DC', default is 'AC'

    C{ppopt} is an optional PYPOWER options vector (see C{ppoption} for
    details). The values for the auction_type field are defined as follows:

       0 - discriminative pricing (price equal to offer or bid)
       1 - last accepted offer auction
       2 - first rejected offer auction
       3 - last accepted bid auction
       4 - first rejected bid auction
       5 - first price auction (marginal unit, offer or bid, sets the price)
       6 - second price auction (if offer is marginal, then price is set
                                    by min(FRO,LAB), if bid, then max(FRB,LAO)
       7 - split the difference pricing (price set by last accepted offer & bid)
       8 - LAO sets seller price, LAB sets buyer price

    The default auction_type is 5, where the marginal block (offer or bid)
    sets the price. The default lim sets no offer/bid or price limits. The
    default previous commitment status u0 is all ones (assume everything was
    running) and the default duration t is 1 hour. The results may
    optionally be printed to a file (appended if the file exists) whose name
    is given in C{fname} (in addition to printing to C{stdout}). Optionally
    returns the final values of the solved case in results, the cleared
    offers and bids in CO and CB, the objective function value F, the old
    style C{dispatch} matrix, the convergence status of the OPF in C{success},
    and the elapsed time C{et}. If a name is given in C{solvedcase}, the solved
    case will be written to a case file in MATPOWER format with the specified
    name.

    @see C{off2case}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if ppopt == None:
        ppopt = ppoption
    if mkt == None:
        mkt = array([])
    if offers == None:
        offers = {}
    if bids == None:
        bids = {}

    ## read data & convert to internal bus numbering
    ppc = loadcase(ppc)

    ## assign default arguments
    if len(mkt) == 0:
        mkt = { 'OPF': array([]), 'auction_type': array([]),
            'lim': array([]), 'u0': array([]), 't': array([]) }

    if 'OPF' not in mkt or len(mkt['OPF']) == 0:
        mkt['OPF'] = 'AC'         ## default OPF is AC

    if 'auction_type' not in mkt or len(mkt['auction_type']) == 0:
        mkt['auction_type'] = 5   ## default auction type is first price

    if 'lim' not in mkt or len(mkt['lim']) == 0:
        mkt['lim'] = pricelimits([], 'Q' in offers or 'Q' in bids)

    if 'u0' not in mkt or len(mkt['u0']) == 0:
        mkt['u0'] = ones(shape(ppc['gen'])[0], 1) ## default for previous gen commitment, all on

    if 't' not in mkt or len(mkt['t']) == 0:
        mkt['t'] = 1              ## default dispatch duration in hours

    ## if offers not defined, use gencost
    if len(offers) == 0 or len(offers['P']['qty']) == 0:
        q, p = case2off(ppc['gen'], ppc['gencost'])

        ## find indices for gens and variable loads
        G = find( not isload(ppc['gen']) )   ## real generators
        L = find(     isload(ppc['gen']) )   ## variable loads
        offers = { 'P': { 'qty': q[G, :], 'prc': p[G, :] } }
        bids   = { 'P': { 'qty': q[L, :], 'prc': p[L, :] } }

    if len(bids) == 0:
        np = shape(offers['P']['qty'])[1]
        bids = { 'P': {'qty': zeros((0, np)), 'prc': zeros((0, np)) } }

    ## start the clock
    t0 = time()

    ## run the market
    co, cb, r, dispatch, success = smartmkt(ppc, offers, bids, mkt, ppopt)

    ## compute elapsed time
    et = time() - t0

    ## print results
    if fname:
        try:
            fd = open(fname, 'a+b')
            printmkt(r, mkt['t'], dispatch, success, fd, ppopt)
            fd.close()
        except IOError, e:
            sys.stderr.write(e.message)

    printmkt(r, mkt.t, dispatch, success, 1, ppopt)

    ## save solved case
    if solvedcase:
        savecase(solvedcase, r)

    return r, co, cb, r['f'], dispatch, success, et
