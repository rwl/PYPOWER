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

"""Splits the gencost variable into two pieces if costs are given for Qg.
"""

from sys import stderr

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
        stderr.write('pqcost: gencost has wrong number of rows\n')

    return pcost, qcost
