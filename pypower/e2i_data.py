# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Converts data from external to internal indexing.
"""

import sys

from numpy import arange, concatenate

from scipy.sparse import issparse, vstack, hstack

from pypower.get_reorder import get_reorder


def e2i_data(ppc, val, ordering, dim=0):
    """Converts data from external to internal indexing.

    When given a case dict that has already been converted to
    internal indexing, this function can be used to convert other data
    structures as well by passing in 2 or 3 extra parameters in
    addition to the case dict. If the value passed in the 2nd
    argument is a column vector, it will be converted according to the
    C{ordering} specified by the 3rd argument (described below). If C{val}
    is an n-dimensional matrix, then the optional 4th argument (C{dim},
    default = 0) can be used to specify which dimension to reorder.
    The return value in this case is the value passed in, converted
    to internal indexing.

    The 3rd argument, C{ordering}, is used to indicate whether the data
    corresponds to bus-, gen- or branch-ordered data. It can be one
    of the following three strings: 'bus', 'gen' or 'branch'. For
    data structures with multiple blocks of data, ordered by bus,
    gen or branch, they can be converted with a single call by
    specifying C{ordering} as a list of strings.

    Any extra elements, rows, columns, etc. beyond those indicated
    in C{ordering}, are not disturbed.

    Examples:
        A_int = e2i_data(ppc, A_ext, ['bus','bus','gen','gen'], 1)

        Converts an A matrix for user-supplied OPF constraints from
        external to internal ordering, where the columns of the A
        matrix correspond to bus voltage angles, then voltage
        magnitudes, then generator real power injections and finally
        generator reactive power injections.

        gencost_int = e2i_data(ppc, gencost_ext, ['gen','gen'], 0)

        Converts a GENCOST matrix that has both real and reactive power
        costs (in rows 1--ng and ng+1--2*ng, respectively).
    """
    if 'order' not in ppc:
        sys.stderr.write('e2i_data: ppc does not have the \'order\' field '
                'required to convert from external to internal numbering.\n')
        return

    o = ppc['order']
    if o['state'] != 'i':
        sys.stderr.write('e2i_data: ppc does not have internal ordering '
                'data available, call ext2int first\n')
        return

    if isinstance(ordering, str):        ## single set
        if ordering == 'gen':
            idx = o[ordering]["status"]["on"][ o[ordering]["e2i"] ]
        else:
            idx = o[ordering]["status"]["on"]
        val = get_reorder(val, idx, dim)
    else:                            ## multiple: sets
        b = 0  ## base
        new_v = []
        for ordr in ordering:
            n = o["ext"][ordr].shape[0]
            v = get_reorder(val, b + arange(n), dim)
            new_v.append( e2i_data(ppc, v, ordr, dim) )
            b = b + n
        n = val.shape[dim]
        if n > b:                ## the rest
            v = get_reorder(val, arange(b, n), dim)
            new_v.append(v)

        if issparse(new_v[0]):
            if dim == 0:
                vstack(new_v, 'csr')
            elif dim == 1:
                hstack(new_v, 'csr')
            else:
                raise ValueError('dim (%d) may be 0 or 1' % dim)
        else:
            val = concatenate(new_v, dim)
    return val
