# Copyright (C) 2005-2011 Power System Engineering Research Center (PSERC)
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

"""Checks for dispatchable loads.
"""

from pypower.idx_gen import PMAX, PMIN


def isload(gen):
    """Checks for dispatchable loads.

    Returns a column vector of 1's and 0's. The 1's correspond to rows of the
    C{gen} matrix which represent dispatchable loads. The current test is
    C{Pmin < 0 and Pmax == 0}. This may need to be revised to allow sensible
    specification of both elastic demand and pumped storage units.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    return (gen[:, PMIN] < 0) & (gen[:, PMAX] == 0)
