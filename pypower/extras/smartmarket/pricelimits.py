# Copyright (C) 2005-2011 Power System Engineering Research Center
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

from numpy import array


def pricelimits(lim, haveQ):
    """Fills in a dict with default values for offer/bid limits.

    The final dictionary looks like:
        lim.P.min_bid           - bids below this are withheld
             .max_offer         - offers above this are withheld
             .min_cleared_bid   - cleared bid prices below this are clipped
             .max_cleared_offer - cleared offer prices above this are clipped
           .Q       (optional, same structure as P)

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if len(lim) == 0:
        if haveQ:
            lim = { 'P': fill_lim([]), 'Q': fill_lim([]) }
        else:
            lim = { 'P': fill_lim([]) }
    else:
        if 'P' not in lim:
            lim['P'] = array([])
        lim['P'] = fill_lim(lim['P'])
        if haveQ:
            if 'Q' not in lim:
                lim['Q'] = array([])
            lim['Q'] = fill_lim(lim['Q'])

    return lim


def fill_lim(lim):
    if len(lim) == 0:
        lim = { 'max_offer': array([]), 'min_bid': array([]),
            'max_cleared_offer': array([]), 'min_cleared_bid': array([]) }
    else:
        if 'max_offer' not in lim:
            lim['max_offer'] = array([])

        if 'min_bid' not in lim:
            lim['min_bid'] = array([])

        if 'max_cleared_offer' not in lim:
            lim['max_cleared_offer'] = array([])

        if 'min_cleared_bid' not in lim:
            lim['min_cleared_bid'] = array([])

    return lim
