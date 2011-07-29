# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Computes total cost for generators at given output level.
"""

from numpy import zeros, arange, polyval
from numpy import flatnonzero as find

from idx_cost import PW_LINEAR, POLYNOMIAL, COST, NCOST, MODEL


def totcost(gencost, Pg):
    """Computes total cost for generators at given output level.

    Computes total cost for generators given a matrix in gencost format and
    a column vector or matrix of generation levels. The return value has the
    same dimensions as PG. Each row of C{gencost} is used to evaluate the
    cost at the points specified in the corresponding row of C{Pg}.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Richard Lincoln
    """
    ng, m = gencost.shape
    totalcost = zeros(ng)

    if len(gencost) > 0:
        ipwl = find(gencost[:, MODEL] == PW_LINEAR)
        ipol = find(gencost[:, MODEL] == POLYNOMIAL)
        if len(ipwl) > 0:
            p = gencost[:, COST:(m-1):2]
            c = gencost[:, (COST+1):m:2]

            for i in ipwl:
                ncost = gencost[i, NCOST]
                for k in arange(ncost - 1):
                    p1, p2 = p[i, k], p[i, k+1]
                    c1, c2 = c[i, k], c[i, k+1]
                    m = (c2 - c1) / (p2 - p1)
                    b = c1 - m * p1
                    Pgen = Pg[i]
                    if Pgen < p2:
                        totalcost[i] = m * Pgen + b
                        break
                    totalcost[i] = m * Pgen + b

        for i in ipol:
            totalcost[ipol] = polyval(gencost[i, COST:COST + gencost[i,NCOST]],
                                      Pg[i])

    return totalcost
