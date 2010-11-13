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

from numpy import ndim

def set_reorder(A, B, idx, dim=1):
    """ Assigns B to A with one of the dimensions of A indexed.

    @return: A after doing A(:, ..., :, IDX, :, ..., :) = B
    where DIM determines in which dimension to place the IDX.

    @see: L{get_reorder}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ndims = ndim(A)
    if ndims ==  1:
        A[idx] = B
    elif ndims == 2:
        if dim == 1:
            A[idx, :] = B
        elif dim == 2:
            A[:, idx] = B
        else:
            raise ValueError
    else:
        raise ValueError

    return A