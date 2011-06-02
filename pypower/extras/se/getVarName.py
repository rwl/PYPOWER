# Copyright (C) 2009-2011 Rui Bo <eeborui@hotmail.com>
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

from numpy import r_

def getVarName(varIndex, pv, pq):
    """Get variable name by variable index (as in H matrix).

    Output comprises both variable type ('Va', 'Vm') and the bus number of
    the variable. For instance, Va8, Vm10, etc.
    """
    ## get non reference buses
    nonref = r_[pv, pq]

    if varIndex <= len(nonref):
        varType = 'Va'
        newIdx = varIndex
    else:
        varType = 'Vm'
        newIdx = varIndex - len(nonref)

    return '%s%d' % varType, nonref[newIdx]
