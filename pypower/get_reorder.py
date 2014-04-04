# Copyright (C) 2009-2011 Power System Engineering Research Center (PSERC)
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

"""Indexes a matrix dimension.
"""

from numpy import ndim

def get_reorder(A, idx, dim=0):
    """Returns A with one of its dimensions indexed::

        B = get_reorder(A, idx, dim)

    Returns A[:, ..., :, idx, :, ..., :], where dim determines
    in which dimension to place the idx.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ndims = ndim(A)
    if ndims == 1:
        B = A[idx].copy()
    elif ndims == 2:
        if dim == 0:
            B = A[idx, :].copy()
        elif dim == 1:
            B = A[:, idx].copy()
        else:
            raise ValueError('dim (%d) may be 0 or 1' % dim)
    else:
        raise ValueError('number of dimensions (%d) may be 1 or 2' % dim)

    return B
