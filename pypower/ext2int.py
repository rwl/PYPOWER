# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

import logging

from numpy import array, copy, zeros, argsort, flatnonzero as find
from scipy.sparse import csr_matrix as sparse

from idx_bus import PQ, PV, REF, NONE, BUS_I, BUS_TYPE
from idx_gen import GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS
from idx_brch import F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, TAP, SHIFT, BR_STATUS
from idx_area import AREA_I, PRICE_REF_BUS

from get_reorder import get_reorder
from run_userfcn import run_userfcn

logger = logging.getLogger(__name__)

def ext2int(ppc, val_or_field=None, ordering=None, dim=1):
    """Converts external to internal indexing.

    This function performs several different tasks, depending on the
    arguments passed.

    1.  ppc = EXT2INT(ppc)

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
        ppc = ext2int(ppc);

    2.  VAL = EXT2INT(ppc, VAL, ORDERING)
        VAL = EXT2INT(ppc, VAL, ORDERING, DIM)
        ppc = EXT2INT(ppc, FIELD, ORDERING)
        ppc = EXT2INT(ppc, FIELD, ORDERING, DIM)

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
#    if isinstance(bus, dict):
#        ppc = bus # FIXME: copy
    if ordering is None: # nargin == 1
        first = not ppc.has_key('order')
        if first or ppc["order"]["state"] == 'e':
            ## initialize order
            if first:
                o = {'ext': {},
                     'bus': {'status': {}},
                     'gen': {'status': {}},
                     'branch': {'status': {}}}
            else:
                o = ppc["order"]

            ## sizes
            nb = ppc["bus"].shape[0]
            ng = ppc["gen"].shape[0]
            ng0 = ng
            if ppc.has_key('A'):
                dc = True if ppc["A"].shape[1] < (2 * nb + 2 * ng) else False
            elif ppc.has_key('N'):
                dc = True if ppc["N"].shape[1] < (2 * nb + 2 * ng) else False
            else:
                dc = False

            ## save data matrices with external ordering
            o["ext"]["bus"]    = copy(ppc["bus"])
            o["ext"]["branch"] = copy(ppc["branch"])
            o["ext"]["gen"]    = copy(ppc["gen"])
            if ppc.has_key('areas'):
                if len(ppc["areas"]) == 0: ## if areas field is empty
                    del ppc['areas']       ## delete it (so it's ignored)
                else:                      ## otherwise
                    o["ext"]["areas"] = copy(ppc["areas"]) ## save it

            ## check that all buses have a valid BUS_TYPE
            bt = ppc["bus"][:, BUS_TYPE]
            err = find(~((bt == PQ) | (bt == PV) | (bt == REF) |
                            (bt == NONE)))
            if len(err) > 0:
                logger.error('ext2int: bus %d has an invalid BUS_TYPE',err)

            ## determine which buses, branches, gens are connected and
            ## in-service
            n2i = sparse((range(nb), (ppc["bus"][:, BUS_I], zeros(nb))),
                         shape=(max(ppc["bus"][:, BUS_I]) + 1, 1))
            n2i = array( n2i.todense().flatten() )[0, :] # as 1D array
            bs = (bt != NONE)                               ## bus status
            o["bus"]["status"]["on"]  = find(  bs )         ## connected
            o["bus"]["status"]["off"] = find( ~bs )         ## isolated
            gs = ( ppc["gen"][:, GEN_STATUS] > 0 &          ## gen status
                    bs[ n2i[ppc["gen"][:, GEN_BUS].astype(int)] ] )
            o["gen"]["status"]["on"]  = find(  gs )    ## on and connected
            o["gen"]["status"]["off"] = find( ~gs )    ## off or isolated
            brs = ( ppc["branch"][:, BR_STATUS].astype(int) &  ## branch status
                    bs[n2i[ppc["branch"][:, F_BUS].astype(int)]] &
                    bs[n2i[ppc["branch"][:, T_BUS].astype(int)]] ).astype(bool)
            o["branch"]["status"]["on"]  = find(  brs ) ## on and conn
            o["branch"]["status"]["off"] = find( ~brs )
            if ppc.has_key('areas'):
                ar = bs[n2i[ppc["areas"][:, PRICE_REF_BUS].astype(int)]]
                o["areas"]["status"]["on"]   = find(  ar )
                o["areas"]["status"]["off"]  = find( ~ar )

            ## delete stuff that is "out"
            if len(o["bus"]["status"]["off"]) > 0:
                ppc["bus"][o["bus"]["status"]["off"], :] = array([])
            if len(o["branch"]["status"]["off"]) > 0:
                ppc["branch"][o["branch"]["status"]["off"], :] = array([])
            if len(o["gen"]["status"]["off"]) > 0:
                ppc["gen"][o["gen"]["status"]["off"], :] = array([])
            if ppc.has_key('areas') and (len(o["areas"]["status"]["off"]) > 0):
                ppc["areas"][o["areas"]["status"]["off"], :] = array([])

            ## update size
            nb = ppc["bus"].shape[0]

            ## apply consecutive bus numbering
            o["bus"]["i2e"] = ppc["bus"][:, BUS_I]
            o["bus"]["e2i"] = zeros(max(o["bus"]["i2e"]) + 1)
            o["bus"]["e2i"][o["bus"]["i2e"].astype(int)] = range(nb)
            ppc["bus"][:, BUS_I] = \
                o["bus"]["e2i"][ ppc["bus"][:, BUS_I].astype(int) ]
            ppc["gen"][:, GEN_BUS] = \
                o["bus"]["e2i"][ ppc["gen"][:, GEN_BUS].astype(int) ]
            ppc["branch"][:, F_BUS] = \
                o["bus"]["e2i"][ ppc["branch"][:, F_BUS].astype(int) ]
            ppc["branch"][:, T_BUS] = \
                o["bus"]["e2i"][ ppc["branch"][:, T_BUS].astype(int) ]
            if ppc.has_key('areas'):
                ppc["areas"][:, PRICE_REF_BUS] = \
                    o["bus"]["e2i"][ppc["areas"][:, PRICE_REF_BUS].astype(int)]

            ## reorder gens in order of increasing bus number
            o["gen"]["e2i"] = argsort(ppc["gen"][:, GEN_BUS])
            o["gen"]["i2e"] = argsort(o["gen"]["e2i"])

            ppc["gen"] = ppc["gen"][o["gen"]["e2i"].astype(int), :]

            if o.has_key('int'):
                del o['int']
            o["state"] = 'i'
            ppc["order"] = o

            ## update gencost, A and N
            if ppc.has_key('gencost'):
                ordering = ['gen']            ## Pg cost only
                if ppc["gencost"].shape[0] == (2 * ng0):
                    ordering.append('gen')    ## include Qg cost
                ppc = ext2int(ppc, 'gencost', ordering)
            if ppc.has_key('A') or ppc.has_key('N'):
                if dc:
                    ordering = ['bus', 'gen']
                else:
                    ordering = ['bus', 'bus', 'gen', 'gen']
            if ppc.has_key('A'):
                ppc = ext2int(ppc, 'A', ordering, 2)
            if ppc.has_key('N'):
                ppc = ext2int(ppc, 'N', ordering, 2)

            ## execute userfcn callbacks for 'ext2int' stage
            if ppc.has_key('userfcn'):
                ppc = run_userfcn(ppc.userfcn, 'ext2int', ppc)
    else:                    ## convert extra data
        if isinstance(val_or_field, str) or isinstance(val_or_field, list):
            ## field
            field = val_or_field                ## rename argument
            if isinstance(field, str):
                ppc["order"]["ext"]["field"] = ppc["field"]
                ppc["field"] = ext2int(ppc, ppc["field"], ordering, dim)
#            else:
#                for k in range(len(field)):
#                    s[k]["type"] = '.'
#                    s[k]["subs"] = field[k]
#                ppc["order"]["ext"] = \
#                    subsasgn(ppc["order"]["ext"], s, subsref(ppc, s))
#                ppc = subsasgn(ppc, s,
#                    ext2int(ppc, subsref(ppc, s), ordering, dim))
        else:
            ## value
            val = val_or_field                   ## rename argument
            o = ppc["order"]
            if isinstance(ordering, str):        ## single set
                if ordering == 'gen':
                    idx = o[ordering]["status"]["on"][o[ordering]["e2i"]]
                else:
                    idx = o[ordering]["status"]["on"]
                i2e = get_reorder(val, idx, dim)
#            else:                            ## multiple: sets
#                b = 0  ## base
#                for k in range(len(ordering)):
#                    n = o["ext"][ordering[k]].shape[0]
#                    v = get_reorder(val, b + range(n), dim)
#                    new_v[k] = ext2int(ppc, v, ordering[k], dim)
#                    b = b + n
#                n = val.shape[dim - 1]
#                if n > b:                ## the rest
#                    v = get_reorder(val, b + range(n), dim)
#                    new_v[len(new_v) + 1] = v
#                i2e = [dim] + new_v[:]

#    else:            ## old form
#        i2e = bus[:, BUS_I]
#        e2i = csr_matrix((max(i2e), 1))
#        e2i[i2e] = range(bus.shape[0])
#
#        bus[:, BUS_I]               = e2i[ bus[:, BUS_I]            ]
#        gen[:, GEN_BUS]             = e2i[ gen[:, GEN_BUS]          ]
#        branch[:, F_BUS]            = e2i[ branch[:, F_BUS]         ]
#        branch[:, T_BUS]            = e2i[ branch[:, T_BUS]         ]
#        if areas is not None & areas.any():
#            areas[:, PRICE_REF_BUS] = e2i[ areas[:, PRICE_REF_BUS]  ]

    return ppc
