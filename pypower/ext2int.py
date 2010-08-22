# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2009-2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from numpy import array, ones, nonzero, sort
from scipy.sparse import csr_matrix

from idx_bus import PQ, PV, REF, NONE, BUS_I, BUS_TYPE
from idx_gen import GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS
from idx_brch import F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, TAP, SHIFT, BR_STATUS
from idx_area import AREA_I, PRICE_REF_BUS

from get_reorder import get_reorder

logger = logging.getLogger(__name__)

def ext2int(bus, gen, branch, areas):
    """Converts external to internal indexing.

    This function performs several different tasks, depending on the
    arguments passed.

    1.  [I2E, BUS, GEN, BRANCH, AREAS] = EXT2INT(BUS, GEN, BRANCH, AREAS)
        [I2E, BUS, GEN, BRANCH] = EXT2INT(BUS, GEN, BRANCH)

    If the first argument is a matrix, it simply converts from (possibly
    non-consecutive) external bus numbers to consecutive internal bus
    numbers which start at 1. Changes are made to BUS, GEN, BRANCH and
    optionally AREAS matrices, which are returned along with a vector of
    indices I2E that can be passed to INT2EXT to perform the reverse
    conversion, where EXTERNAL_BUS_NUMBER = I2E(INTERNAL_BUS_NUMBER)

    Examples:
        [i2e, bus, gen, branch, areas] = ext2int(bus, gen, branch, areas);
        [i2e, bus, gen, branch] = ext2int(bus, gen, branch);

    2.  MPC = EXT2INT(MPC)

    If the input is a single MATPOWER case struct, then all isolated
    buses, off-line generators and branches are removed along with any
    generators, branches or areas connected to isolated buses. Then the
    buses are renumbered consecutively, beginning at 1, and the
    generators are sorted by increasing bus number. All of the related
    indexing information and the original data matrices are stored in
    an 'order' field in the struct to be used by INT2EXT to perform
    the reverse conversions. If the case is already using internal
    numbering it is returned unchanged.

    Example:
        mpc = ext2int(mpc);

    3.  VAL = EXT2INT(MPC, VAL, ORDERING)
        VAL = EXT2INT(MPC, VAL, ORDERING, DIM)
        MPC = EXT2INT(MPC, FIELD, ORDERING)
        MPC = EXT2INT(MPC, FIELD, ORDERING, DIM)

    When given a case struct that has already been converted to
    internal indexing, this function can be used to convert other data
    structures as well by passing in 2 or 3 extra parameters in
    addition to the case struct. If the value passed in the 2nd
    argument is a column vector, it will be converted according to the
    ORDERING specified by the 3rd argument (described below). If VAL
    is an n-dimensional matrix, then the optional 4th argument (DIM,
    default = 1) can be used to specify which dimension to reorder.
    The return value in this case is the value passed in, converted
    to internal indexing.

    If the 2nd argument is a string or cell array of strings, it
    specifies a field in the case struct whose value should be
    converted as described above. In this case, the converted value
    is stored back in the specified field, the original value is
    saved for later use and the updated case struct is returned.
    If FIELD is a cell array of strings, they specify nested fields.

    The 3rd argument, ORDERING, is used to indicate whether the data
    corresponds to bus-, gen- or branch-ordered data. It can be one
    of the following three strings: 'bus', 'gen' or 'branch'. For
    data structures with multiple blocks of data, ordered by bus,
    gen or branch, they can be converted with a single call by
    specifying ORDERING as a cell array of strings.

    Any extra elements, rows, columns, etc. beyond those indicated
    in ORDERING, are not disturbed.

    @see: L{int2ext}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if isinstance(bus, dict):
        mpc = bus # FIXME: copy
        if branch is None:#nargin == 1
            first = not mpc.has_key('order')
            if first or mpc["order"]["state"] == 'e':
                ## initialize order
                if first:
                    status = {
                            'on':  array([]),
                            'off': array([])
                        }
                    tmp = {
                            'e2i':      array([]),
                            'i2e':      array([]),
                            'status':   status
                        }
                    o = {
                            'ext':      {
                                    'bus':      array([]),
                                    'branch':   array([]),
                                    'gen':      array([])
                                },
                            'bus':      tmp,
                            'gen':      tmp,
                            'branch':   {'status': status}
                        }
                else:
                    o = mpc["order"]

                ## sizes
                nb = mpc.bus.shape[0]
                ng = mpc.gen.shape[0]
                ng0 = ng
                if mpc.has_key('A') & mpc["A"].shape[1] < 2 * nb + 2 * ng:
                    dc = 1
                elif mpc.has_key('N') & mpc["N"].shape[1] < 2 * nb + 2 * ng:
                    dc = 1
                else:
                    dc = 0

                ## save data matrices with external ordering
                o["ext"]["bus"]    = mpc["bus"]
                o["ext"]["branch"] = mpc["branch"]
                o["ext"]["gen"]    = mpc["gen"]
                if mpc.has_key('areas'):
                    if not mpc["areas"].any(): ## if areas field is empty
                        del mpc['areas']       ## delete it (so it's ignored)
                    else:                      ## otherwise
                        o["ext"]["areas"] = mpc["areas"] ## save it

                ## check that all buses have a valid BUS_TYPE
                bt = mpc["bus"][:, BUS_TYPE]
                err = nonzero(~(bt == PQ | bt == PV | bt == REF | bt == NONE))
                if err.any():
                    logger.error('ext2int: bus %d has an invalid BUS_TYPE',err)

                ## determine which buses, branches, gens are connected and
                ## in-service
                n2i = csr_matrix((range(nb), (mpc["bus"][:, BUS_I], ones(nb))),
                                 (max(mpc["bus"][:, BUS_I]), 1))
                bs = (bt != NONE)                               ## bus status
                o["bus"]["status"]["on"]  = nonzero(  bs )      ## connected
                o["bus"]["status"]["off"] = nonzero( ~bs )      ## isolated
                gs = ( mpc["gen"][:, GEN_STATUS] > 0 &          ## gen status
                        bs[n2i[mpc["gen"][:, GEN_BUS]]] )
                o["gen"]["status"]["on"]  = nonzero(  gs )  ## on and connected
                o["gen"]["status"]["off"] = nonzero( ~gs )  ## off or isolated
                brs = ( mpc["branch"][:, BR_STATUS] &      ## branch status
                        bs[n2i[mpc["branch"][:, F_BUS]]] &
                        bs[n2i[mpc["branch"][:, T_BUS]]] )
                o["branch"]["status"]["on"]  = nonzero(  brs ) ## on and conn
                o["branch"]["status"]["off"] = nonzero( ~brs )
                if mpc.has_key('areas'):
                    ar = bs[n2i[mpc["areas"][:, PRICE_REF_BUS]]]
                    o["areas"]["status"]["on"]   = nonzero(  ar )
                    o["areas"]["status"]["off"]  = nonzero( ~ar )

                ## delete stuff that is "out"
                if o["bus"]["status"]["off"].any():
                    mpc["bus"][o["bus"]["status"]["off"], :] = array([])
                if o["branch"]["status"]["off"].any():
                    mpc["branch"][o["branch"]["status"]["off"], :] = array([])
                if o["gen"]["status"]["off"].any():
                    mpc["gen"][o["gen"]["status"]["off"], :] = array([])
                if mpc.has_key('areas') and o["areas"]["status"]["off"].any():
                    mpc["areas"][o["areas"]["status"]["off"], :] = array([])

                ## update size
                nb = mpc["bus"].shape[0]

                ## apply consecutive bus numbering
                o["bus"]["i2e"] = mpc["bus"][:, BUS_I]
                o["bus"]["e2i"] = csr_matrix((max(o["bus"]["i2e"]), 1))
                o["bus"]["e2i"][o["bus"]["i2e"]] = range(nb)
                mpc["bus"][:, BUS_I] = \
                    o["bus"]["e2i"][ mpc["bus"][:, BUS_I] ]
                mpc["gen"][:, GEN_BUS] = \
                    o["bus"]["e2i"][ mpc["gen"][:, GEN_BUS] ]
                mpc["branch"][:, F_BUS] = \
                    o["bus"]["e2i"][ mpc["branch"][:, F_BUS] ]
                mpc["branch"][:, T_BUS] = \
                    o["bus"]["e2i"][ mpc["branch"][:, T_BUS] ]
                if mpc.has_key('areas'):
                    mpc["areas"][:, PRICE_REF_BUS] = \
                        o["bus"]["e2i"][ mpc["areas"][:, PRICE_REF_BUS] ]

                ## reorder gens in order of increasing bus number
                tmp, o["gen"]["e2i"] = sort(mpc["gen"][:, GEN_BUS])
                tmp, o.gen.i2e = sort(o["gen"]["e2i"])
                mpc["gen"] = mpc["gen"][o["gen"]["e2i"], :]

                if o.has_key('int'):
                    del o['int']
                o["state"] = 'i'
                mpc["order"] = o

                ## update gencost, A and N
                if mpc.has_key('gencost'):
                    ordering = ['gen']            ## Pg cost only
                    if mpc["gencost"].shape[0] == 2 * ng0:
                        ordering.append('gen')    ## include Qg cost
                    mpc = ext2int(mpc, 'gencost', ordering)
                if mpc.has_key('A') or mpc.has_key('N'):
                    if dc:
                        ordering = ['bus', 'gen']
                    else:
                        ordering = ['bus', 'bus', 'gen', 'gen']
                if mpc.has_key('A'):
                    mpc = ext2int(mpc, 'A', ordering, 2)
                if mpc.has_key('N'):
                    mpc = ext2int(mpc, 'N', ordering, 2)

                ## execute userfcn callbacks for 'ext2int' stage
                if mpc.has_key('userfcn'):
                    mpc = run_userfcn(mpc.userfcn, 'ext2int', mpc)

            i2e = mpc
        else:                    ## convert extra data
            # FIXME: copy
            ordering = branch              ## rename argument
            if areas is None:#nargin < 4
                dim = 1
            else:
                # FIXME: copy
                dim = areas                ## rename argument
            if isinstance(gen, str) or isinstance(gen, list): ## field
                # FIXME: copy
                field = gen                ## rename argument
                if isinstance(field, str):
                    mpc["order"]["ext"]["field"] = mpc["field"]
                    mpc["field"] = ext2int(mpc, mpc["field"], ordering, dim)
                else:
                    for k in range(len(field)):
                        s[k]["type"] = '.'
                        s[k]["subs"] = field[k]
                    mpc["order"]["ext"] = \
                        subsasgn(mpc["order"]["ext"], s, subsref(mpc, s))
                    mpc = subsasgn(mpc, s,
                        ext2int(mpc, subsref(mpc, s), ordering, dim))
                # FIXME: copy
                i2e = mpc
            else:                           ## value
                val = gen                   ## rename argument
                o = mpc["order"]
                if isinstance(ordering, str):        ## single set
                    if ordering == 'gen':
                        idx = o[ordering]["status"]["on"][o[ordering]["e2i"]]
                    else:
                        idx = o[ordering]["status"]["on"]
                    i2e = get_reorder(val, idx, dim)
                else:                            ## multiple: sets
                    b = 0  ## base
                    for k in range(len(ordering)):
                        n = o["ext"][ordering[k]].shape[0]
                        v = get_reorder(val, b + range(n), dim)
                        new_v[k] = ext2int(mpc, v, ordering[k], dim)
                        b = b + n
                    n = val.shape[dim - 1]
                    if n > b:                ## the rest
                        v = get_reorder(val, b + range(n), dim)
                        new_v[len(new_v) + 1] = v
                    i2e = [dim] + new_v[:]
    else:            ## old form
        i2e = bus[:, BUS_I]
        e2i = csr_matrix((max(i2e), 1))
        e2i[i2e] = range(bus.shape[0])

        bus[:, BUS_I]               = e2i[ bus[:, BUS_I]            ]
        gen[:, GEN_BUS]             = e2i[ gen[:, GEN_BUS]          ]
        branch[:, F_BUS]            = e2i[ branch[:, F_BUS]         ]
        branch[:, T_BUS]            = e2i[ branch[:, T_BUS]         ]
        if areas is not None & areas.any():
            areas[:, PRICE_REF_BUS] = e2i[ areas[:, PRICE_REF_BUS]  ]

    return i2e, bus, gen, branch, areas
