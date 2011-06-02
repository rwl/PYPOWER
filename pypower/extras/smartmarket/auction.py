# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

from numpy import array, shape, zeros, ones, diag, NaN, all

def auction(offers, bids, auction_type, limit_prc=None, gtee_prc=None):
    """Clear auction based on OPF results (qty's and lambdas).

    Clears a set of BIDS and OFFERS based on the results of an OPF, where the
    pricing is adjusted for network losses and binding constraints.
    The arguments OFFERS and BIDS are structs with the following fields:
        qty       - m x n, offer/bid quantities, m offers/bids, n blocks
        prc       - m x n, offer/bid prices
        lam       - m x n, corresponding lambdas
        total_qty - m x 1, total quantity cleared for each offer/bid

    There are 8 types of auctions implemented, specified by AUCTION_TYPE.

       0 - discriminative pricing (price equal to offer or bid)
       1 - last accepted offer auction
       2 - first rejected offer auction
       3 - last accepted bid auction
       4 - first rejected bid auction
       5 - first price auction (marginal unit, offer or bid, sets the price)
       6 - second price auction (if offer is marginal, price set by
              min(FRO,LAB), else max(FRB,LAO)
       7 - split the difference pricing (set by last accepted offer & bid)
       8 - LAO sets seller price, LAB sets buyer price

    Whether or not cleared offer (bid) prices are guaranteed to be greater
    (less) than or equal to the corresponding offer (bid) price is specified by
    a flag gtee_prc['offer'] (gtee_prc['bid']). The default is value true.

    Offer/bid and cleared offer/bid min and max prices are specified in the
    LIMIT_PRC struct with the following fields:
        max_offer
        min_bid
        max_cleared_offer
        min_cleared_bid
    Offers (bids) above (below) max_offer (min_bid) are treated as withheld
    and cleared offer (bid) prices above (below) max_cleared_offer
    (min_cleared_bid) are clipped to max_cleared offer (min_cleared_bid) if
    given. All of these limit prices are ignored if the field is missing
    or is empty.

    @see C{runmarket}
    @see C{smartmkt}

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## initialize some stuff
#    delta = 1e-3       ## prices smaller than this are not used to determine X
    zero_tol = 1e-5

    if len(bids) == 0:
        bids = {'qty': array([]),
                'prc': array([]),
                'lam': array([]),
                'total_qty': array([])}

    if limit_prc == None or len(limit_prc) == 0:
        limit_prc = { 'max_offer': array([]), 'min_bid': array([]),
            'max_cleared_offer': array([]), 'min_cleared_bid': array([]) }
    else:
        if 'max_offer' not in limit_prc:
            limit_prc['max_offer'] = array([])

        if 'min_bid' not in limit_prc:
            limit_prc['min_bid'] = array([])

        if 'max_cleared_offer' not in limit_prc:
            limit_prc['max_cleared_offer'] = array([])

        if 'min_cleared_bid' not in limit_prc:
            limit_prc['min_cleared_bid'] = array([])

    if gtee_prc == None or len(gtee_prc) == 0:
        gtee_prc = { 'offer': 1, 'bid': 1 }
    else:
        if 'offer' not in gtee_prc: gtee_prc['offer'] = 1
        if 'bid' not in gtee_prc: gtee_prc['bid'] = 1

    nro, nco = shape(offers['qty'])
    nrb, ncb = shape(bids['qty'])

    ## determine cleared quantities
    co = {}; cb = {}; o = {}; b = {}
    if len(limit_prc['max_offer']) == 0:
        co['qty'], o['on'], o['off'] = \
                clear_qty(offers['qty'], offers['total_qty'])
    else:
        mask = offers['prc'] <= limit_prc['max_offer']
        co['qty'], o['on'], o['off'] = \
                clear_qty(offers['qty'], offers['total_qty'], mask)

    if len(limit_prc.min_bid) == 0:
        cb['qty'], b['on'], b['off'] = \
                clear_qty(bids['qty'], bids['total_qty'])
    else:
        mask = bids['prc'] <= limit_prc.min_bid
        cb['qty'], b['on'], b['off'] = \
                clear_qty(bids['qty'], bids['total_qty'], mask)

    ## initialize cleared prices
    co['prc'] = zeros((nro, nco))       ## cleared offer prices
    cb['prc'] = zeros((nrb, ncb))       ## cleared bid prices

    ##-----  compute exchange rates to scale lam to get desired pricing  -----
    ## The locationally adjusted offer/bid price, when normalized to an arbitrary
    ## reference location where lambda is equal to ref_lam, is:
    ##      norm_prc = prc * (ref_lam / lam)
    ## Then we can define the ratio between the normalized offer/bid prices
    ## and the ref_lam as an exchange rate X:
    ##      X = norm_prc / ref_lam = prc / lam
    ## This X represents the ratio between the marginal unit (setting lambda)
    ## and the offer/bid price in question.

    if auction_type == 0 or auction_type == 5:
        ## don't bother scaling anything
        X = { 'LAO': 1,
              'FRO': 1,
              'LAB': 1,
              'FRB': 1 }
    else:
        X = compute_exchange_rates(offers, bids, o, b)

    ## cleared offer/bid prices for different auction types
    if auction_type == 0:        ## discriminative
        co['prc'] = offers['prc'].copy()
        cb['prc'] = bids['prc'].copy()
    elif auction_type == 1:    ## LAO
        co['prc'] = offers['lam'] * X['LAO']
        cb['prc'] = bids['lam']   * X['LAO']
    elif auction_type == 2:    ## FRO
        co['prc'] = offers['lam'] * X['FRO']
        cb['prc'] = bids['lam']   * X['FRO']
    elif auction_type == 3:    ## LAB
        co['prc'] = offers['lam'] * X['LAB']
        cb['prc'] = bids['lam']   * X['LAB']
    elif auction_type == 4:    ## FRB
        co['prc'] = offers['lam'] * X['FRB']
        cb['prc'] = bids['lam']   * X['FRB']
    elif auction_type == 5:    ## 1st price
        co['prc'] = offers['lam']
        cb['prc'] = bids['lam']
    elif auction_type == 6:    ## 2nd price
        if abs(1 - X['LAO']) < zero_tol:
            co['prc'] = offers['lam'] * min(X['FRO'], X['LAB'])
            cb['prc'] = bids['lam']   * min(X['FRO'], X['LAB'])
        else:
            co['prc'] = offers['lam'] * max(X['LAO'], X['FRB'])
            cb['prc'] = bids['lam']   * max(X['LAO'], X['FRB'])
    elif auction_type == 7:    ## split the difference
        co['prc'] = offers['lam'] * (X['LAO'] + X['LAB']) / 2
        cb['prc'] = bids['lam']   * (X['LAO'] + X['LAB']) / 2
    elif auction_type == 8:    ## LAO seller, LAB buyer
        co['prc'] = offers['lam'] * X['LAO']
        cb['prc'] = bids['lam']   * X['LAB']

    ## guarantee that cleared offer prices are >= offers
    if gtee_prc['offer']:
        clip = o['on'] * (offers['prc'] - co['prc'])
        co['prc'] = co['prc'] + (clip > zero_tol) * clip

    ## guarantee that cleared bid prices are <= bids
    if gtee_prc['bid']:
        clip = b['on'] * (bids['prc'] - cb['prc'])
        cb['prc'] = cb['prc'] + (clip < -zero_tol) * clip

    ## clip cleared offer prices by limit_prc['max_cleared_offer']
    if len(limit_prc['max_cleared_offer']) > 0:
        co['prc'] = co['prc'] + (co['prc'] > limit_prc['max_cleared_offer']) * \
            (limit_prc['max_cleared_offer'] - co['prc'])

    ## clip cleared bid prices by limit_prc['min_cleared_bid']
    if len(limit_prc['min_cleared_bid']) > 0:
        cb['prc'] = cb['prc'] + (cb['prc'] < limit_prc['min_cleared_bid']) * \
            (limit_prc['min_cleared_bid'] - co['prc'])

    ## make prices uniform after clipping (except for discrim auction)
    ## since clipping may only affect a single block of a multi-block generator
    if auction_type != 0:
        ## equal to largest price in row
        if nco > 1:
            co['prc'] = diag(max(co['prc'].T)) * ones((nro, nco))
        if ncb > 1:
            cb['prc'] = diag(min(cb['prc'].T)) * ones((nrb, ncb))

    return co, cb


def compute_exchange_rates(offers, bids, o, b, delta=1e-3):
    #COMPUTE_EXCHANGE_RATES Determine the scale factors for LAO, FRO, LAB, FRB
    #  Inputs:
    #   offers, bids (same as for auction)
    #   o, b  - structs with on, off fields, each same dim as qty field of offers
    #           or bids, 1 if corresponding block is accepted, 0 otherwise
    #   delta - optional prices smaller than this are not used to determine X
    #  Outputs:
    #   X     - struct with fields LAO, FRO, LAB, FRB containing scale factors
    #           to use for each type of auction
    zero_tol = 1e-5

    ## eliminate terms with lam < delta (X would not be accurate)
    olam = offers['lam'].copy()
    blam = bids['lam'].copy()
    olam[olam[:] < delta] = NaN
    blam[blam[:] < delta] = NaN

    ## eliminate rows for 0 qty offers/bids
    nro, nco = shape(offers['qty'])
    nrb, ncb = shape(bids['qty'])
    omask = ones((nro, nco))
    if nco == 1:
        temp = offers['qty'].copy()
    else:
        temp = sum(offers['qty'].T).T
    omask[temp == 0, :] = NaN
    bmask = ones((nrb, ncb))
    if ncb == 1:
        temp = bids['qty']
    else:
        temp = sum(bids['qty'].T).T
    bmask[temp == 0, :] = NaN

    ## by default, don't scale anything
    X = {}
    X['LAO'] = 1
    X['FRO'] = 1
    X['LAB'] = 1
    X['FRB'] = 1

    ## don't scale if we have any negative lambdas or all are too close to 0
    if all(all(offers['lam'] > -zero_tol)):
        ## ratios
        Xo = omask * offers['prc'] / olam
        Xb = bmask * bids['prc']   / blam

        ## exchange rate for LAO (X['LAO'] * lambda == LAO, for corresponding lambda)
        X['LAO'] = o['on'] * Xo
        X['LAO'][ o['off'][:] ] = NaN
        X['LAO'][ X['LAO'][:] > 1 + zero_tol ] = NaN   ## don't let gens @ Pmin set price
        X['LAO'] = max( X['LAO'][:] )

        ## exchange rate for FRO (X['FRO'] * lambda == FRO, for corresponding lambda)
        X['FRO'] = o['off'] * Xo
        X['FRO'][ o['on'][:] ] = NaN
        X['FRO'] = min( X['FRO'][:] )

        if nrb:
            ## exchange rate for LAB (X['LAB'] * lambda == LAB, for corresponding lambda)
            X['LAB'] = b['on'] * Xb
            X['LAB'][ b['off'][:] ] = NaN
            X['LAB'][ X['LAB'][:] < 1 - zero_tol ] = NaN   ## don't let set price
            X['LAB'] = min( X['LAB'][:] )

            ## exchange rate for FRB (X['FRB'] * lambda == FRB, for corresponding lambda)
            X['FRB'] = b['off'] * Xb
            X['FRB'][ b['on'][:] ] = NaN
            X['FRB'] = max( X['FRB'][:] )

    return X


def clear_qty(qty, total_cqty, mask=None):
    #CLEAR_QTY  Computed cleared offer/bid quantities from totals.
    #  Inputs:
    #   qty        - m x n, offer/bid quantities, m offers/bids, n blocks
    #   total_cqty - m x 1, total cleared quantity for each offer/bid
    #   mask       - m x n, boolean indicating which offers/bids are valid (not withheld)
    #  Outputs:
    #   cqty       - m x n, cleared offer/bid quantities, m offers/bids, n blocks
    #   on         - m x n, 1 if partially or fully accepted, 0 if rejected
    #   off        - m x n, 1 if rejected, 0 if partially or fully accepted

    nr, nc = shape(qty)
    accept  = zeros((nr, nc))
    cqty    = zeros((nr, nc))
    for i in range(nr):            ## offer/bid i
        for j in range(nc):        ## block j
            if qty[i, j]:    ## ignore zero quantity offers/bids
                ## compute fraction of the block accepted \
                accept[i, j] = (total_cqty[i] - sum(qty[i, 0:j - 1])) / qty[i, j]
                ## \ clipped to the range [0, 1]  (i.e. 0-100#)
                if accept[i, j] > 1:
                    accept[i, j] = 1
                elif accept[i, j] < 1.0e-5:
                    accept[i, j] = 0

                cqty[i, j] = qty[i, j] * accept[i, j]

    if mask != None:
        accept = mask * accept

    on  = (accept  > 0)
    off = (accept == 0)

    return cqty, on, off
