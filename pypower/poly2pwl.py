# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
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

"""Converts polynomial cost variable to piecewise linear.
"""

from numpy import ones, zeros, r_

from pypower.idx_cost import MODEL, COST, NCOST, PW_LINEAR

from pypower.totcost import totcost


def poly2pwl(polycost, Pmin, Pmax, npts):
    """Converts polynomial cost variable to piecewise linear.

    Converts the polynomial cost variable C{polycost} into a piece-wise linear
    cost by evaluating at zero and then at C{npts} evenly spaced points between
    C{Pmin} and C{Pmax}. If C{Pmin <= 0} (such as for reactive power, where
    C{P} really means C{Q}) it just uses C{npts} evenly spaced points between
    C{Pmin} and C{Pmax}.
    """
    pwlcost = polycost
    ## size of piece being changed
    m, n = polycost.shape
    ## change cost model
    pwlcost[:, MODEL]  = PW_LINEAR * ones(m)
    ## zero out old data
    pwlcost[:, COST:COST + n] = zeros(pwlcost[:, COST:COST + n].shape)
    ## change number of data points
    pwlcost[:, NCOST]  = npts * ones(m)

    for i in range(m):
        if Pmin[i] == 0:
            step = (Pmax[i] - Pmin[i]) / (npts - 1)
            xx = range(Pmin[i], step, Pmax[i])
        elif Pmin[i] > 0:
            step = (Pmax[i] - Pmin[i]) / (npts - 2)
            xx = r_[0, range(Pmin[i], step, Pmax[i])]
        elif Pmin[i] < 0 & Pmax[i] > 0:        ## for when P really means Q
            step = (Pmax[i] - Pmin[i]) / (npts - 1)
            xx = range(Pmin[i], step, Pmax[i])
        yy = totcost(polycost[i, :], xx)
        pwlcost[i,      COST:2:(COST + 2*(npts-1)    )] = xx
        pwlcost[i,  (COST+1):2:(COST + 2*(npts-1) + 1)] = yy

    return pwlcost
