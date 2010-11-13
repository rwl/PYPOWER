# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

from numpy import zeros
from numpy import flatnonzero as find

from polycost import polycost
from idx_cost import *

def totcost(gencost, Pg):
    """ Computes total cost for generators at given output level.

    Computes total cost for generators given
    a matrix in gencost format and a column vector or matrix of generation
    levels. The return value has the same dimensions as PG. Each row
    of GENCOST is used to evaluate the cost at the points specified in the
    corresponding row of PG.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ng, m = gencost.shape
    totalcost = zeros(ng, Pg.shape[1])

    if len(gencost) > 0:
        ipwl = find(gencost[:, MODEL] == PW_LINEAR)
        ipol = find(gencost[:, MODEL] == POLYNOMIAL)
        if len(ipwl) > 0:
            p = gencost[:, COST:(m-1):2]
            c = gencost[:, (COST+1):m:2]
            for i in ipwl:
                ncost = gencost[i, NCOST]
                for k in range(ncost):
                    p1, p2 = p[i, k], p[i, k+1]
                    c1, c2 = c[i, k], c[i, k+1]
                    m = (c2 - c1) / (p2 - p1)
                    b = c1 - m * p1
                    Pgen = Pg[i]
                    if Pgen < p2:
                        totalcost[i] = m * Pgen + b
                        break
                    totalcost[i] = m * Pgen + b

        totalcost[ipol] = polycost(gencost[ipol, :], Pg[ipol])

    return totalcost
