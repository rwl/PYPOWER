# Copyright (C) 1996-2011 Power System Engineering Research Center
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

from sys import stderr

from numpy import array, arange


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
