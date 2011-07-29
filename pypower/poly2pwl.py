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

"""Converts polynomial cost variable to piecewise linear.
"""

from numpy import ones, zeros, r_

from idx_cost import MODEL, COST, NCOST, PW_LINEAR

from totcost import totcost


def poly2pwl(polycost, Pmin, Pmax, npts):
    """Converts polynomial cost variable to piecewise linear.

    Converts the polynomial cost variable C{polycost} into a piece-wise linear
    cost by evaluating at zero and then at C{npts} evenly spaced points between
    C{Pmin} and C{Pmax}. If C{Pmin <= 0} (such as for reactive power, where
    C{P} really means C{Q}) it just uses C{npts} evenly spaced points between
    C{Pmin} and C{Pmax}.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
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
