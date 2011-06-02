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

from numpy import shape, any, zeros, ones, r_, arange, flatnonzero as find

from pypower.idx_cost import MODEL, NCOST, COST, POLYNOMIAL, PW_LINEAR
from pypower.idx_gen import PMIN, PMAX

from pypower.totcost import totcost

def case2off(gen, gencost):
    """Creates quantity & price offers from gen & gencost.

    @see C{off2case}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## do conversion
    oldgencost = gencost
    i_poly = find(gencost[:, MODEL] == POLYNOMIAL)
    npts = 6                   ## 6 points => 5 blocks
    ## convert polynomials to piece-wise linear by evaluating at zero and then
    ## at evenly spaced points between Pmin and Pmax
    if any(i_poly):
        m, n = shape(gencost[i_poly, :])                              ## size of piece being changed
        gencost[i_poly, MODEL] = PW_LINEAR * ones((m, 1))             ## change cost model
        gencost[i_poly, COST:n + 1] = zeros(shape(gencost[i_poly, COST:n + 1])) ## zero out old data
        gencost[i_poly, NCOST] = npts * ones((m, 1))                     ## change number of data points

        for i in range(m):
            ig = i_poly[i]     ## index to gen
            Pmin = gen[ig, PMIN]
            Pmax = gen[ig, PMAX]
            if Pmin == 0:
                step = [Pmax - Pmin] / (npts - 1)
                xx = arange(Pmin, Pmax, step)  ## FIXME Inclusive range stop
            else:
                step = (Pmax - Pmin) / (npts - 2)
                xx = r_[0, arange(Pmin, Pmax, step)] ## FIXME Inclusive range stop

            yy = totcost(oldgencost[ig, :], xx)
            gencost[ig,       COST:(COST + 2 * (npts - 1)    ):2] = xx
            gencost[ig, (COST + 1):(COST + 2 * (npts - 1) + 1):2] = yy

    n = max(gencost[:, NCOST])
    xx = gencost[:,     COST:( COST + 2 * n - 1 )]
    yy = gencost[:, (COST+1):2:( COST + 2*n     )]
    i1 = arange(n - 1)
    i2 = arange(1, n)
    q = xx[:, i2] - xx[:, i1]
    p = ( yy[:, i2] - yy[:, i1] ) / q

    return q, p
