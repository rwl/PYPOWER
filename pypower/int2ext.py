# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www["A"]pache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from bus_idx import PQ, PV, REF, NONE, BUS_I
from gen_idx import GEN_BUS
from brch_idx import F_BUS, T_BUS
from idx_area import AREA_I, PRICE_REF_BUS

from get_reorder import get_reorder
from set_reorder import set_reorder
from run_userfcn import run_userfcn

logger = logging.getLogger(__name__)

def int2ext(i2e, bus, gen, branch, areas):
    """Converts internal to external bus numbering.

    This function performs several different tasks, depending on the
    arguments passed.

    1.  [BUS, GEN, BRANCH, AREAS] = INT2EXT(I2E, BUS, GEN, BRANCH, AREAS)
        [BUS, GEN, BRANCH] = INT2EXT(I2E, BUS, GEN, BRANCH)

    Converts from the consecutive internal bus numbers back to the originals
    using the mapping provided by the I2E vector returned from EXT2INT,
    where EXTERNAL_BUS_NUMBER = I2E(INTERNAL_BUS_NUMBER).

    Examples:
        [bus, gen, branch, areas] = int2ext(i2e, bus, gen, branch, areas)
        [bus, gen, branch] = int2ext(i2e, bus, gen, branch)

    2.  ppc = INT2EXT(ppc)

    If the input is a single MATPOWER case struct, then it restores all
    buses, generators and branches that were removed because of being
    isolated or off-line, and reverts to the original generator ordering
    and original bus numbering. This requires that the 'order' field
    created by EXT2INT be in place.

    Example:
        ppc = int2ext(ppc)

    3.  VAL = INT2EXT(ppc, VAL, OLDVAL, ORDERING)
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
    if isinstance(i2e, dict):
        ppc = i2e
        if bus is None:#nargin == 1
            if not ppc.has_key('order'):
                logger.error('int2ext: ppc does not have the "order" field '
                    'require for conversion back to external numbering.')
            o = ppc["order"]

            if o["state"] == 'i':
                ## execute userfcn callbacks for 'int2ext' stage
                if ppc.has_key('userfcn'):
                    ppc = run_userfcn(ppc["userfcn"], 'int2ext', ppc)

                ## save data matrices with internal ordering & restore originals
                o["int"]["bus"]    = ppc["bus"]
                o["int"]["branch"] = ppc["branch"]
                o["int"]["gen"]    = ppc["gen"]
                ppc["bus"]     = o["ext"]["bus"]
                ppc["branch"]  = o["ext"]["branch"]
                ppc["gen"]     = o["ext"]["gen"]
                if ppc.has_key('gencost'):
                    o["int"]["gencost"] = ppc["gencost"]
                    ppc["gencost"] = o["ext"]["gencost"]
                if ppc.has_key('areas'):
                    o["int"]["areas"] = ppc["areas"]
                    ppc["areas"] = o["ext"]["areas"]
                if ppc.has_key('A'):
                    o["int"]["A"] = ppc["A"]
                    ppc["A"] = o["ext"]["A"]
                if ppc.has_key('N'):
                    o["int"]["N"] = ppc["N"]
                    ppc["N"] = o["ext"]["N"]

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
                        [ ppc["bus"][o["bus"]["status"]["on"], BUS_I] ]
                ppc["branch"][o["branch"]["status"]["on"], F_BUS] = \
                    o["bus"]["i2e"] \
                        [ ppc["branch"][o["branch"]["status"]["on"], F_BUS] ]
                ppc["branch"][o["branch"]["status"]["on"], T_BUS] = \
                    o["bus"]["i2e"] \
                        [ ppc["branch"][o["branch"]["status"]["on"], T_BUS] ]
                ppc["gen"][o["gen"]["status"]["on"], GEN_BUS] = \
                    o["bus"]["i2e"] \
                        [ ppc["gen"][o["gen"]["status"]["on"], GEN_BUS] ]
                if ppc.has_key('areas'):
                    ppc["areas"][o["areas"]["status"]["on"], PRICE_REF_BUS] = \
                        o["bus"]["i2e"][ ppc["areas"] \
                         [o["areas"]["status"]["on"], PRICE_REF_BUS] ]

                if o.has_key('ext'):
                    del o['ext']
                o["state"] = 'e'
                ppc["order"] = o
            else:
                logger.error('int2ext: ppc claims it is already using '
                             'external numbering.')

            bus = ppc
        else:                    ## convert extra data
            if isinstance(bus, str) or isinstance(bus, list):   ## field
                field = bus
                ordering = gen
                if branch is not None:
                    dim = branch
                else:
                    dim = 1
                if isinstance(field, str):
                    ppc["order"]["int"]["field"] = ppc["field"]
                    ppc["field"] = int2ext(ppc, ppc["field"],
                                    ppc["order"].ext["field"], ordering, dim)
                else:
                    for k in range(len(field)):
                        s[k].type = '.'
                        s[k].subs = field[k]
                    if not ppc["order"].has_key('int'):
                        ppc["order"]["int"] = array([])
                    ppc["order"]["int"] = \
                        subsasgn(ppc["order"]["int"], s, subsref(ppc, s))
                    ppc = subsasgn(ppc, s, int2ext(ppc, subsref(ppc, s),
                        subsref(ppc["order"].ext, s), ordering, dim))
                bus = ppc
            else:                            ## value
                val = bus
                oldval = gen
                ordering = branch
                o = ppc["order"]
                if areas is not None:
                    dim = areas
                else:
                    dim = 1
                if isinstance(ordering, str):         ## single set
                    if ordering == 'gen':
                        v = get_reorder(val, o["ordering"]["i2e"], dim)
                    else:
                        v = val
                    bus = set_reorder(oldval, v,
                                      o["ordering"]["status"]["on"], dim)
                else:                            ## multiple sets
                    be = 0  ## base, external indexing
                    bi = 0  ## base, internal indexing
                    for k in range(len(ordering)):
                        ne = o["ext"]["ordering"][k].shape[0]
                        ni = ppc["ordering"][k].shape[0]
                        v = get_reorder(val, bi + range(ni), dim)
                        oldv = get_reorder(oldval, be + range(ne), dim)
                        new_v[k] = int2ext(ppc, v, oldv, ordering[k], dim)
                        be = be + ne
                        bi = bi + ni
                    ni = size(val, dim)
                    if ni > bi:              ## the rest
                        v = get_reorder(val, bi + range(ni), dim)
                        new_v[len(new_v) + 1] = v
                    bus = [dim] + new_v[:]
    else:            ## old form
        bus[:, BUS_I]               = i2e[ bus[:, BUS_I]            ]
        gen[:, GEN_BUS]             = i2e[ gen[:, GEN_BUS]          ]
        branch[:, F_BUS]            = i2e[ branch[:, F_BUS]         ]
        branch[:, T_BUS]            = i2e[ branch[:, T_BUS]         ]
        if areas is not None and branch is not None and not areas.any():
            areas[:, PRICE_REF_BUS] = i2e[ areas[:, PRICE_REF_BUS]  ]

    return bus, gen, branch, areas
