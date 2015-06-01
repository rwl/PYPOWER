# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Indexes a matrix dimension.
"""

from numpy import ndim

def get_reorder(A, idx, dim=0):
    """Returns A with one of its dimensions indexed::

        B = get_reorder(A, idx, dim)

    Returns A[:, ..., :, idx, :, ..., :], where dim determines
    in which dimension to place the idx.

    @author: Ray Zimmerman (PSERC Cornell)
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
