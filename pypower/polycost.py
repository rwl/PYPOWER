# Copyright (C) 2009-2011 Power System Engineering Research Center
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

from numpy import zeros, arange, flatnonzero as find

from idx_cost import MODEL, NCOST, PW_LINEAR, COST


def polycost(gencost, Pg, der=0):
    """Evaluates polynomial generator cost & derivatives.
    F = POLYCOST(GENCOST, PG) returns the vector of costs evaluated at PG

    DF = POLYCOST(GENCOST, PG, 1) returns the vector of first derivatives
    of costs evaluated at PG

    D2F = POLYCOST(GENCOST, PG, 2) returns the vector of second derivatives
    of costs evaluated at PG

    GENCOST must contain only polynomial costs
    PG is in MW, not p.u. (works for QG too)

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if any(gencost[:, MODEL] == PW_LINEAR):
        sys.stderr.write('polycost: all costs must be polynomial\n')

    ng = len(Pg)
    maxN = max(gencost[:, NCOST])
    minN = min(gencost[:, NCOST])

    ## form coefficient matrix where 1st column is constant term, 2nd linear, etc.
    c = zeros((ng, maxN))
    for n in arange(minN, maxN + 1):
        k = find(gencost[:, NCOST] == n)   ## cost with n coefficients
        c[k, :n] = gencost[k, (COST + n - 1):COST - 1:-1]

    ## do derivatives
    for d in range(1, der + 1):
        if c.shape[1] >= 2:
            c = c[:, 1:maxN - d + 1]
        else:
            c = zeros((ng, 1))
            break
        for k in range(1, maxN - d):
            c[:, k] = k * c[:, k]

    ## evaluate polynomial
    if len(c) == 0:
        f = zeros(Pg.shape)
    else:
        f = c[:, :1].flatten()  ## constant term
        for k in range(1, c.shape[1]):
            f = f + c[:, k] * Pg**k

    return f
