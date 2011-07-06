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

"""Converts external to internal indexing.
"""

import sys

from copy import deepcopy

from numpy import array, zeros, argsort, arange, concatenate
from numpy import flatnonzero as find

from scipy.sparse import issparse, vstack, hstack, csr_matrix as sparse

from idx_bus import PQ, PV, REF, NONE, BUS_I, BUS_TYPE
from idx_gen import GEN_BUS, GEN_STATUS
from idx_brch import F_BUS, T_BUS, BR_STATUS
from idx_area import PRICE_REF_BUS

from get_reorder import get_reorder
from run_userfcn import run_userfcn


def ext2int(ppc, val_or_field=None, ordering=None, dim=0):
    """Converts external to internal indexing.

    This function performs several different tasks, depending on the
    arguments passed.

      1.  C{ppc = ext2int(ppc)}

      If the input is a single PYPOWER case dict, then all isolated
      buses, off-line generators and branches are removed along with any
      generators, branches or areas connected to isolated buses. Then the
      buses are renumbered consecutively, beginning at 0, and the
      generators are sorted by increasing bus number. All of the related
      indexing information and the original data matrices are stored under
      the 'order' key of the dict to be used by C{int2ext} to perform
      the reverse conversions. If the case is already using internal
      numbering it is returned unchanged.

      Example::
          ppc = ext2int(ppc);

      2.  C{val = ext2int(ppc, val, ordering)}

      C{val = ext2int(ppc, val, ordering, dim)}

      C{ppc = ext2int(ppc, field, ordering)}

      C{ppc = ext2int(ppc, field, ordering, dim)}

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

      If the 2nd argument is a string or list of strings, it
      specifies a field in the case dict whose value should be
      converted as described above. In this case, the converted value
      is stored back in the specified field, the original value is
      saved for later use and the updated case dict is returned.
      If C{field} is a list of strings, they specify nested fields.

      The 3rd argument, C{ordering}, is used to indicate whether the data
      corresponds to bus-, gen- or branch-ordered data. It can be one
      of the following three strings: 'bus', 'gen' or 'branch'. For
      data structures with multiple blocks of data, ordered by bus,
      gen or branch, they can be converted with a single call by
      specifying C{ordering} as a list of strings.

      Any extra elements, rows, columns, etc. beyond those indicated
      in C{ordering}, are not disturbed.

    @see: L{int2ext}
    """
    ppc = deepcopy(ppc)
    if val_or_field is None:  # nargin == 1
        first = 'order' not in ppc
        if first or ppc["order"]["state"] == 'e':
            ## initialize order
            if first:
                o = {
                        'ext':      {
                                'bus':      None,
                                'branch':   None,
                                'gen':      None
                            },
                        'bus':      { 'e2i':      None,
                                      'i2e':      None,
                                      'status':   {} },
                        'gen':      { 'e2i':      None,
                                      'i2e':      None,
                                      'status':   {} },
                        'branch':   { 'status': {} }
                    }
            else:
                o = ppc["order"]

            ## sizes
            nb = ppc["bus"].shape[0]
            ng = ppc["gen"].shape[0]
            ng0 = ng
            if 'A' in ppc:
                dc = True if ppc["A"].shape[1] < (2 * nb + 2 * ng) else False
            elif 'N' in ppc:
                dc = True if ppc["N"].shape[1] < (2 * nb + 2 * ng) else False
            else:
                dc = False

            ## save data matrices with external ordering
            if 'ext' not in o: o['ext'] = {}
            o["ext"]["bus"]    = ppc["bus"].copy()
            o["ext"]["branch"] = ppc["branch"].copy()
            o["ext"]["gen"]    = ppc["gen"].copy()
            if 'areas' in ppc:
                if len(ppc["areas"]) == 0: ## if areas field is empty
                    del ppc['areas']       ## delete it (so it's ignored)
                else:                      ## otherwise
                    o["ext"]["areas"] = ppc["areas"].copy()  ## save it

            ## check that all buses have a valid BUS_TYPE
            bt = ppc["bus"][:, BUS_TYPE]
            err = find(~((bt == PQ) | (bt == PV) | (bt == REF) | (bt == NONE)))
            if len(err) > 0:
                sys.stderr.write('ext2int: bus %d has an invalid BUS_TYPE\n' % err)

            ## determine which buses, branches, gens are connected and
            ## in-service
            n2i = sparse((range(nb), (ppc["bus"][:, BUS_I], zeros(nb))),
                         shape=(max(ppc["bus"][:, BUS_I]) + 1, 1))
            n2i = array( n2i.todense().flatten() )[0, :] # as 1D array
            bs = (bt != NONE)                               ## bus status
            o["bus"]["status"]["on"]  = find(  bs )         ## connected
            o["bus"]["status"]["off"] = find( ~bs )         ## isolated
            gs = ( (ppc["gen"][:, GEN_STATUS] > 0) &          ## gen status
                    bs[ n2i[ppc["gen"][:, GEN_BUS].astype(int)] ] )
            o["gen"]["status"]["on"]  = find(  gs )    ## on and connected
            o["gen"]["status"]["off"] = find( ~gs )    ## off or isolated
            brs = ( ppc["branch"][:, BR_STATUS].astype(int) &  ## branch status
                    bs[n2i[ppc["branch"][:, F_BUS].astype(int)]] &
                    bs[n2i[ppc["branch"][:, T_BUS].astype(int)]] ).astype(bool)
            o["branch"]["status"]["on"]  = find(  brs ) ## on and conn
            o["branch"]["status"]["off"] = find( ~brs )
            if 'areas' in ppc:
                ar = bs[ n2i[ppc["areas"][:, PRICE_REF_BUS].astype(int)] ]
                o["areas"] = {"status": {}}
                o["areas"]["status"]["on"]  = find(  ar )
                o["areas"]["status"]["off"] = find( ~ar )

            ## delete stuff that is "out"
            if len(o["bus"]["status"]["off"]) > 0:
#                ppc["bus"][o["bus"]["status"]["off"], :] = array([])
                ppc["bus"] = ppc["bus"][o["bus"]["status"]["on"], :]
            if len(o["branch"]["status"]["off"]) > 0:
#                ppc["branch"][o["branch"]["status"]["off"], :] = array([])
                ppc["branch"] = ppc["branch"][o["branch"]["status"]["on"], :]
            if len(o["gen"]["status"]["off"]) > 0:
#                ppc["gen"][o["gen"]["status"]["off"], :] = array([])
                ppc["gen"] = ppc["gen"][o["gen"]["status"]["on"], :]
            if 'areas' in ppc and (len(o["areas"]["status"]["off"]) > 0):
#                ppc["areas"][o["areas"]["status"]["off"], :] = array([])
                ppc["areas"] = ppc["areas"][o["areas"]["status"]["on"], :]

            ## update size
            nb = ppc["bus"].shape[0]

            ## apply consecutive bus numbering
            o["bus"]["i2e"] = ppc["bus"][:, BUS_I].copy()
            o["bus"]["e2i"] = zeros(max(o["bus"]["i2e"]) + 1)
            o["bus"]["e2i"][o["bus"]["i2e"].astype(int)] = arange(nb)
            ppc["bus"][:, BUS_I] = \
                o["bus"]["e2i"][ ppc["bus"][:, BUS_I].astype(int) ].copy()
            ppc["gen"][:, GEN_BUS] = \
                o["bus"]["e2i"][ ppc["gen"][:, GEN_BUS].astype(int) ].copy()
            ppc["branch"][:, F_BUS] = \
                o["bus"]["e2i"][ ppc["branch"][:, F_BUS].astype(int) ].copy()
            ppc["branch"][:, T_BUS] = \
                o["bus"]["e2i"][ ppc["branch"][:, T_BUS].astype(int) ].copy()
            if 'areas' in ppc:
                ppc["areas"][:, PRICE_REF_BUS] = \
                    o["bus"]["e2i"][ ppc["areas"][:,
                        PRICE_REF_BUS].astype(int) ].copy()

            ## reorder gens in order of increasing bus number
            o["gen"]["e2i"] = argsort(ppc["gen"][:, GEN_BUS])
            o["gen"]["i2e"] = argsort(o["gen"]["e2i"])

            ppc["gen"] = ppc["gen"][o["gen"]["e2i"].astype(int), :]

            if 'int' in o:
                del o['int']
            o["state"] = 'i'
            ppc["order"] = o

            ## update gencost, A and N
            if 'gencost' in ppc:
                ordering = ['gen']            ## Pg cost only
                if ppc["gencost"].shape[0] == (2 * ng0):
                    ordering.append('gen')    ## include Qg cost
                ppc = ext2int(ppc, 'gencost', ordering)
            if 'A' in ppc or 'N' in ppc:
                if dc:
                    ordering = ['bus', 'gen']
                else:
                    ordering = ['bus', 'bus', 'gen', 'gen']
            if 'A' in ppc:
                ppc = ext2int(ppc, 'A', ordering, 1)
            if 'N' in ppc:
                ppc = ext2int(ppc, 'N', ordering, 1)

            ## execute userfcn callbacks for 'ext2int' stage
            if 'userfcn' in ppc:
                ppc = run_userfcn(ppc['userfcn'], 'ext2int', ppc)
    else:                    ## convert extra data
        if isinstance(val_or_field, str) or isinstance(val_or_field, list):
            ## field
            field = val_or_field                ## rename argument

            if isinstance(field, str):
                key = '["%s"]' % field
            else:
                key = '["%s"]' % '"]["'.join(field)

                v_ext = ppc["order"]["ext"]
                for fld in field:
                    if fld not in v_ext:
                        v_ext[fld] = {}
                        v_ext = v_ext[fld]

            exec 'ppc["order"]["ext"]%s = ppc%s.copy()' % (key, key)
            exec 'ppc%s = ext2int(ppc, ppc%s, ordering, dim)' % (key, key)

        else:
            ## value
            val = val_or_field.copy()                   ## rename argument

            o = ppc["order"]
            if isinstance(ordering, str):        ## single set
                if ordering == 'gen':
                    idx = o[ordering]["status"]["on"][ o[ordering]["e2i"] ]
                else:
                    idx = o[ordering]["status"]["on"]
                val = get_reorder(val, idx, dim)
            else:                            ## multiple: sets
                b = 0  ## base
                new_v = []
                for ord in ordering:
                    n = o["ext"][ord].shape[0]
                    v = get_reorder(val, b + arange(n), dim)
                    new_v.append( ext2int(ppc, v, ord, dim) )
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
                        raise ValueError, 'dim (%d) may be 0 or 1' % dim
                else:
                    val = concatenate(new_v, dim)
            return val

    return ppc


def ext2int1(bus, gen, branch, areas=None):
    """Converts from (possibly non-consecutive) external bus numbers to
    consecutive internal bus numbers which start at 1. Changes are made
    to BUS, GEN, BRANCH and optionally AREAS matrices, which are returned
    along with a vector of indices I2E that can be passed to INT2EXT to
    perform the reverse conversion.

    @see: L{int2ext}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    i2e = bus[:, BUS_I].astype(int)
    e2i = zeros(max(i2e) + 1)
    e2i[i2e] = arange(bus.shape[0])

    bus[:, BUS_I]    = e2i[ bus[:, BUS_I].astype(int)    ]
    gen[:, GEN_BUS]  = e2i[ gen[:, GEN_BUS].astype(int)  ]
    branch[:, F_BUS] = e2i[ branch[:, F_BUS].astype(int) ]
    branch[:, T_BUS] = e2i[ branch[:, T_BUS].astype(int) ]
    if areas is not None and len(areas) > 0:
        areas[:, PRICE_REF_BUS] = e2i[ areas[:, PRICE_REF_BUS].astype(int) ]

        return i2e, bus, gen, branch, areas

    return i2e, bus, gen, branch
