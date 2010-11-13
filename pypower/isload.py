# Copyright (C) 2005-2010 Power System Engineering Research Center (PSERC)
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

from idx_gen import PMAX, PMIN

def isload(gen):
    """Checks for dispatchable loads.

    Returns a column vector of 1's and 0's. The 1's correspond to rows of the
    GEN matrix which represent dispatchable loads. The current test is
    Pmin < 0 AND Pmax == 0. This may need to be revised to allow sensible
    specification of both elastic demand and pumped storage units.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    return gen[:, PMIN] < 0 & gen[:, PMAX] == 0
