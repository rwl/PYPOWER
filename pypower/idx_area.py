# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

"""Defines constants for named column indices to areas matrix.

The index, name and meaning of each column of the areas matrix is given below:

columns 0-1
 0  AREA_I           area number
 1  PRICE_REF_BUS    price reference bus for this area

@see: U{http://www.pserc.cornell.edu/matpower/}
"""

# define the indices
AREA_I          = 0    # area number
PRICE_REF_BUS   = 1    # price reference bus for this area
