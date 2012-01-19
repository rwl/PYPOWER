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

"""Defines constants for named column indices to areas matrix.

The index, name and meaning of each column of the areas matrix is given below:

columns 0-1
    0.  C{AREA_I}           area number
    1.  C{PRICE_REF_BUS}    price reference bus for this area

@author: Ray Zimmerman (PSERC Cornell)
@author: Richard Lincoln
"""

# define the indices
AREA_I          = 0    # area number
PRICE_REF_BUS   = 1    # price reference bus for this area
