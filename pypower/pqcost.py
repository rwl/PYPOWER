# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

import logging

from numpy import array

logger = logging.getLogger(__name__)

def pqcost(gencost, ng, on=None):
    """Splits the gencost variable into two pieces if costs are given for Qg.

    Checks whether GENCOST has
    cost information for reactive power generation (rows ng+1 to 2*ng).
    If so, it returns the first NG rows in PCOST and the last NG rows in
    QCOST. Otherwise, leaves QCOST empty. Also does some error checking.
    If ON is specified (list of indices of generators which are on line)
    it only returns the rows corresponding to these generators.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if on is None:
        on = range(ng)

    if gencost.shape[0] == ng:
        pcost = gencost[on, :]
        qcost = array([])
    elif gencost.shape[0] == 2 * ng:
        pcost = gencost[on, :]
        qcost = gencost[on + ng, :]
    else:
        logger.error('pqcost: gencost has wrong number of rows')

    return pcost, qcost