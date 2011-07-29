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

"""Splits the gencost variable into two pieces if costs are given for Qg.
"""

from numpy import array, arange


def pqcost(gencost, ng, on=None):
    """Splits the gencost variable into two pieces if costs are given for Qg.

    Checks whether C{gencost} has cost information for reactive power
    generation (rows C{ng+1} to C{2*ng}). If so, it returns the first C{ng}
    rows in C{pcost} and the last C{ng} rows in C{qcost}. Otherwise, leaves
    C{qcost} empty. Also does some error checking.
    If C{on} is specified (list of indices of generators which are on line)
    it only returns the rows corresponding to these generators.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    if on is None:
        on = arange(ng)

    if gencost.shape[0] == ng:
        pcost = gencost[on, :]
        qcost = array([])
    elif gencost.shape[0] == 2 * ng:
        pcost = gencost[on, :]
        qcost = gencost[on + ng, :]
    else:
        raise ValueError, 'pqcost: gencost has wrong number of rows\n'

    return pcost, qcost
