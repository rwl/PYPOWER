# Copyright (C) 2009 Power System Engineering Research Center (PSERC)
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

from numpy import ndim

def get_reorder(A, idx, dim=1):
    """Returns A with one of its dimensions indexed.

    B = get_reorder(A, idx, dim)

    Returns A(:, ..., :, idx, :, ..., :), where dim determines
    in which dimension to place the idx.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ndims = ndim(A)
    if ndims == 1:
        B = A[idx]
    elif ndims == 2:
        if dim == 1:
            B = A[idx, :]
        elif dim == 2:
            B = A[: idx]
        else:
            raise ValueError
    else:
        raise ValueError

    return B
