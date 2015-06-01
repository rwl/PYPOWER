# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import sys

from numpy import arange, concatenate

from pypower.get_reorder import get_reorder
from pypower.set_reorder import set_reorder


def i2e_data(ppc, val, oldval, ordering, dim=0):
    """Converts data from internal to external bus numbering.

    For a case dict using internal indexing, this function can be
    used to convert other data structures as well by passing in 3 or 4
    extra parameters in addition to the case dict. If the value passed
    in the 2nd argument C{val} is a column vector, it will be converted
    according to the ordering specified by the 4th argument (C{ordering},
    described below). If C{val} is an n-dimensional matrix, then the
    optional 5th argument (C{dim}, default = 0) can be used to specify
    which dimension to reorder. The 3rd argument (C{oldval}) is used to
    initialize the return value before converting C{val} to external
    indexing. In particular, any data corresponding to off-line gens
    or branches or isolated buses or any connected gens or branches
    will be taken from C{oldval}, with C[val} supplying the rest of the
    returned data.

    The C{ordering} argument is used to indicate whether the data
    corresponds to bus-, gen- or branch-ordered data. It can be one
    of the following three strings: 'bus', 'gen' or 'branch'. For
    data structures with multiple blocks of data, ordered by bus,
    gen or branch, they can be converted with a single call by
    specifying C[ordering} as a list of strings.

    Any extra elements, rows, columns, etc. beyond those indicated
    in C{ordering}, are not disturbed.

    Examples:
        A_ext = i2e_data(ppc, A_int, A_orig, ['bus','bus','gen','gen'], 1)

        Converts an A matrix for user-supplied OPF constraints from
        internal to external ordering, where the columns of the A
        matrix correspond to bus voltage angles, then voltage
        magnitudes, then generator real power injections and finally
        generator reactive power injections.

        gencost_ext = i2e_data(ppc, gencost_int, gencost_orig, ['gen','gen'], 0)

        Converts a C{gencost} matrix that has both real and reactive power
        costs (in rows 1--ng and ng+1--2*ng, respectively).

    @see: L{e2i_data}, L{i2e_field}, L{int2ext}.
    """
    from pypower.int2ext import int2ext

    if 'order' not in ppc:
        sys.stderr.write('i2e_data: ppc does not have the \'order\' field '
                'required for conversion back to external numbering.\n')
        return

    o = ppc["order"]
    if o['state'] != 'i':
        sys.stderr.write('i2e_data: ppc does not appear to be in internal '
                'order\n')
        return

    if isinstance(ordering, str):         ## single set
        if ordering == 'gen':
            v = get_reorder(val, o[ordering]["i2e"], dim)
        else:
            v = val
        val = set_reorder(oldval, v, o[ordering]["status"]["on"], dim)
    else:                                 ## multiple sets
        be = 0  ## base, external indexing
        bi = 0  ## base, internal indexing
        new_v = []
        for ordr in ordering:
            ne = o["ext"][ordr].shape[0]
            ni = ppc[ordr].shape[0]
            v = get_reorder(val, bi + arange(ni), dim)
            oldv = get_reorder(oldval, be + arange(ne), dim)
            new_v.append( int2ext(ppc, v, oldv, ordr, dim) )
            be = be + ne
            bi = bi + ni
        ni = val.shape[dim]
        if ni > bi:              ## the rest
            v = get_reorder(val, arange(bi, ni), dim)
            new_v.append(v)
        val = concatenate(new_v, dim)

    return val
