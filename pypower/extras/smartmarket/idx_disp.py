# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

"""Defines constants for named column indices to dispatch matrix.

@see: U{http://www.pserc.cornell.edu/matpower/}
"""
## define the indices
QUANTITY      = 0    ## quantity produced by generator in MW
PRICE         = 1    ## market price for power produced by generator in $/MWh
FCOST         = 2    ## fixed cost in $/MWh
VCOST         = 3    ## variable cost in $/MWh
SCOST         = 4    ## startup cost in $
PENALTY       = 5    ## penalty cost in $ (not used)
