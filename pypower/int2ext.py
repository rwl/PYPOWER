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

import logging

from numpy import copy

from idx_bus import BUS_I
from idx_gen import GEN_BUS
from idx_brch import F_BUS, T_BUS
from idx_area import PRICE_REF_BUS

from get_reorder import get_reorder
from set_reorder import set_reorder
from run_userfcn import run_userfcn

logger = logging.getLogger(__name__)

def int2ext(ppc, val_or_field=None, oldval=None, ordering=None, dim=1):
    """Converts internal to external bus numbering.

    This function performs several different tasks, depending on the
    arguments passed.

    1.  ppc = INT2EXT(ppc)

    If the input is a single MATPOWER case struct, then it restores all
    buses, generators and branches that were removed because of being
    isolated or off-line, and reverts to the original generator ordering
    and original bus numbering. This requires that the 'order' field
    created by EXT2INT be in place.

    Example:
        ppc = int2ext(ppc)

    2.  VAL = INT2EXT(ppc, VAL, OLDVAL, ORDERING)
        VAL = INT2EXT(ppc, VAL, OLDVAL, ORDERING, DIM)
        ppc = INT2EXT(ppc, FIELD, ORDERING)
        ppc = INT2EXT(ppc, FIELD, ORDERING, DIM)

    For a case struct using internal indexing, this function can be
    used to convert other data structures as well by passing in 2 to 4
    extra parameters in addition to the case struct. If the values passed
    in the 2nd argument (VAL) is a column vector, it will be converted
    according to the ordering specified by the 4th argument (ORDERING,
    described below). If VAL is an n-dimensional matrix, then the
    optional 5th argument (DIM, default = 1) can be used to specify
    which dimension to reorder. The 3rd argument (OLDVAL) is used to
    initialize the return value before converting VAL to external
    indexing. In particular, any data corresponding to off-line gens
    or branches or isolated buses or any connected gens or branches
    will be taken from OLDVAL, with VAL supplying the rest of the
    returned data.

    If the 2nd argument is a string or cell array of strings, it
    specifies a field in the case struct whose value should be
    converted as described above. In this case, the corresponding
    OLDVAL is taken from where it was stored by EXT2INT in
    ppc["order"].EXT and the updated case struct is returned.
    If FIELD is a cell array of strings, they specify nested fields.

    The ORDERING argument is used to indicate whether the data
    corresponds to bus-, gen- or branch-ordered data. It can be one
    of the following three strings: 'bus', 'gen' or 'branch'. For
    data structures with multiple blocks of data, ordered by bus,
    gen or branch, they can be converted with a single call by
    specifying ORDERING as a cell array of strings.

    Any extra elements, rows, columns, etc. beyond those indicated
    in ORDERING, are not disturbed.

    @see: ext2int
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if ordering is None: # nargin == 1
        if 'order' not in ppc:
            logger.error('int2ext: ppc does not have the "order" field '
                'require for conversion back to external numbering.')
        o = ppc["order"]

        if o["state"] == 'i':
            ## execute userfcn callbacks for 'int2ext' stage
            if 'userfcn' in ppc:
                ppc = run_userfcn(ppc["userfcn"], 'int2ext', ppc)

            ## save data matrices with internal ordering & restore originals
            o["int"] = {}
            o["int"]["bus"]    = copy(ppc["bus"])
            o["int"]["branch"] = copy(ppc["branch"])
            o["int"]["gen"]    = copy(ppc["gen"])
            ppc["bus"]     = copy(o["ext"]["bus"])
            ppc["branch"]  = copy(o["ext"]["branch"])
            ppc["gen"]     = copy(o["ext"]["gen"])
            if 'gencost' in ppc:
                o["int"]["gencost"] = copy(ppc["gencost"])
                ppc["gencost"] = copy(o["ext"]["gencost"])
            if 'areas' in ppc:
                o["int"]["areas"] = copy(ppc["areas"])
                ppc["areas"] = copy(o["ext"]["areas"])
            if 'A' in ppc:
                o["int"]["A"] = copy(ppc["A"])
                ppc["A"] = copy(o["ext"]["A"])
            if 'N' in ppc:
                o["int"]["N"] = copy(ppc["N"])
                ppc["N"] = copy(o["ext"]["N"])

            ## update data (in bus, branch and gen only)
            ppc["bus"][o["bus"]["status"]["on"], :] = \
                o["int"]["bus"]
            ppc["branch"][o["branch"]["status"]["on"], :] = \
                o["int"]["branch"]
            ppc["gen"][o["gen"]["status"]["on"], :] = \
                o["int"]["gen"][o["gen"]["i2e"], :]
            if ppc.has_key('areas'):
                ppc["areas"][o["areas"]["status"]["on"], :] = \
                    o["int"]["areas"]

            ## revert to original bus numbers
            ppc["bus"][o["bus"]["status"]["on"], BUS_I] = \
                o["bus"]["i2e"] \
                    [ ppc["bus"][o["bus"]["status"]["on"], BUS_I].astype(int) ]
            ppc["branch"][o["branch"]["status"]["on"], F_BUS] = \
                o["bus"]["i2e"][ ppc["branch"] \
                    [o["branch"]["status"]["on"], F_BUS].astype(int) ]
            ppc["branch"][o["branch"]["status"]["on"], T_BUS] = \
                o["bus"]["i2e"][ ppc["branch"] \
                    [o["branch"]["status"]["on"], T_BUS].astype(int) ]
            ppc["gen"][o["gen"]["status"]["on"], GEN_BUS] = \
                o["bus"]["i2e"][ ppc["gen"] \
                    [o["gen"]["status"]["on"], GEN_BUS].astype(int) ]
            if ppc.has_key('areas'):
                ppc["areas"][o["areas"]["status"]["on"], PRICE_REF_BUS] = \
                    o["bus"]["i2e"][ ppc["areas"] \
                    [o["areas"]["status"]["on"], PRICE_REF_BUS].astype(int) ]

            if 'ext' in o: del o['ext']
            o["state"] = 'e'
            ppc["order"] = o
        else:
            logger.error('int2ext: ppc claims it is already using '
                         'external numbering.')
    else:                    ## convert extra data
        if isinstance(val_or_field, str) or isinstance(val_or_field, list):
            ## field (key)
            field = val_or_field
            if isinstance(field, str):
                ppc["order"]["int"][field] = ppc[field]
                ppc[field] = int2ext(ppc, ppc[field],
                                     ppc["order"]["ext"][field], ordering, dim)
            else:
                pass
#                for k in range(len(field)):
#                    s[k].type = '.'
#                    s[k].subs = field[k]
#                if not ppc["order"].has_key('int'):
#                    ppc["order"]["int"] = array([])
#                ppc["order"]["int"] = \
#                    subsasgn(ppc["order"]["int"], s, subsref(ppc, s))
#                ppc = subsasgn(ppc, s, int2ext(ppc, subsref(ppc, s),
#                    subsref(ppc["order"].ext, s), ordering, dim))
        else:
            ## value
            val = val_or_field
            o = ppc["order"]
            if isinstance(ordering, str):         ## single set
                if ordering == 'gen':
                    v = get_reorder(val, o["ordering"]["i2e"], dim)
                else:
                    v = val
                ppc = set_reorder(oldval, v,
                                  o["ordering"]["status"]["on"], dim)
            else:                            ## multiple sets
                be = 0  ## base, external indexing
                bi = 0  ## base, internal indexing
                for k in range(len(ordering)):
                    ne = o["ext"]["ordering"][k].shape[0]
                    ni = ppc["ordering"][k].shape[0]
                    v = get_reorder(val, bi + range(ni), dim)
                    oldv = get_reorder(oldval, be + range(ne), dim)
#                    new_v[k] = int2ext(ppc, v, oldv, ordering[k], dim)
                    be = be + ne
                    bi = bi + ni
                ni = val.shape[dim]
                if ni > bi:              ## the rest
                    v = get_reorder(val, bi + range(ni), dim)
#                    new_v[len(new_v) + 1] = v
#                ppc = [dim] + new_v[:]

    return ppc
