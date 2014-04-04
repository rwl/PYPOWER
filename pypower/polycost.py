# Copyright (C) 2009-2011 Power System Engineering Research Center (PSERC)
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

"""Evaluates polynomial generator cost & derivatives.
"""

import sys

from numpy import zeros, arange, flatnonzero as find

from pypower.idx_cost import MODEL, NCOST, PW_LINEAR, COST


def polycost(gencost, Pg, der=0):
    """Evaluates polynomial generator cost & derivatives.

    C{f = polycost(gencost, Pg)} returns the vector of costs evaluated at C{Pg}

    C{df = polycost(gencost, Pg, 1)} returns the vector of first derivatives
    of costs evaluated at C{Pg}

    C{d2f = polycost(gencost, Pg, 2)} returns the vector of second derivatives
    of costs evaluated at C{Pg}

    C{gencost} must contain only polynomial costs
    C{Pg} is in MW, not p.u. (works for C{Qg} too)

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    if any(gencost[:, MODEL] == PW_LINEAR):
        sys.stderr.write('polycost: all costs must be polynomial\n')

    ng = len(Pg)
    maxN = max( gencost[:, NCOST].astype(int) )
    minN = min( gencost[:, NCOST].astype(int) )

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

        for k in range(2, maxN - d + 1):
            c[:, k-1] = c[:, k-1] * k

    ## evaluate polynomial
    if len(c) == 0:
        f = zeros(Pg.shape)
    else:
        f = c[:, :1].flatten()  ## constant term
        for k in range(1, c.shape[1]):
            f = f + c[:, k] * Pg**k

    return f
