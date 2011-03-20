# Copyright (C) 2009-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
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

import logging

from numpy import zeros, nonzero

from idx_cost import MODEL, NCOST, PW_LINEAR, COST

logger = logging.getLogger(__name__)

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
        logger.error('polycost: all costs must be polynomial')

    ng = len(Pg)
    maxN = max(gencost[:, NCOST])
    minN = min(gencost[:, NCOST])

    ## form coefficient matrix where 1st column is constant term, 2nd linear, etc.
    c = zeros((ng, maxN))
    for n in range(minN, maxN):
        k = nonzero(gencost[:, NCOST] == n)   ## cost with n coefficients
        c[k, :n] = gencost[k, (COST + n - 1):-1:COST]

    ## do derivatives
    for d in range(der):
        if c.shape[1] >= 2:
            c = c[:, 2:maxN - d + 1]
        else:
            c = zeros(ng)
            break
        for k in range(1, maxN - d):
            c[:, k] = k * c[:, k]

    ## evaluate polynomial
    if not any(c):
        f = zeros(Pg.shape)
    else:
        f = c[:, 0]        ## constant term
        for k in range(1, c.shape[1]):
            f = f + c[:, k] * Pg**(k - 1)

    return f
