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

"""Converts internal to external bus numbering.
"""

import sys

from copy import deepcopy

from numpy import arange, concatenate

from idx_bus import BUS_I
from idx_gen import GEN_BUS
from idx_brch import F_BUS, T_BUS
from idx_area import PRICE_REF_BUS

from pypower.get_reorder import get_reorder
from pypower.set_reorder import set_reorder
from pypower.run_userfcn import run_userfcn


def int2ext(ppc, val_or_field=None, oldval=None, ordering=None, dim=0):
    """Converts internal to external bus numbering.

    This function performs several different tasks, depending on the
    arguments passed.

        1.  C{ppc = int2ext(ppc)}

        If the input is a single PYPOWER case dict, then it restores all
        buses, generators and branches that were removed because of being
        isolated or off-line, and reverts to the original generator ordering
        and original bus numbering. This requires that the 'order' key
        created by L{ext2int} be in place.

        Example::
            ppc = int2ext(ppc)

        2.  C{val = int2ext(ppc, val, oldval, ordering)}

        C{val = int2ext(ppc, val, oldval, ordering, dim)}

        C{ppc = int2ext(ppc, field, ordering)}

        C{ppc = int2ext(ppc, field, ordering, dim)}

        For a case dict using internal indexing, this function can be
        used to convert other data structures as well by passing in 2 to 4
        extra parameters in addition to the case dict. If the values passed
        in the 2nd argument (C{val}) is a column vector, it will be converted
        according to the ordering specified by the 4th argument (C{ordering},
        described below). If C{val} is an n-dimensional matrix, then the
        optional 5th argument (C{dim}, default = 0) can be used to specify
        which dimension to reorder. The 3rd argument (C{oldval}) is used to
        initialize the return value before converting C{val} to external
        indexing. In particular, any data corresponding to off-line gens
        or branches or isolated buses or any connected gens or branches
        will be taken from C{oldval}, with C{val} supplying the rest of the
        returned data.

        If the 2nd argument is a string or list of strings, it
        specifies a field in the case dict whose value should be
        converted as described above. In this case, the corresponding
        C{oldval} is taken from where it was stored by L{ext2int} in
        ppc["order"]["ext"] and the updated case dict is returned.
        If C{field} is a list of strings, they specify nested fields.

        The C{ordering} argument is used to indicate whether the data
        corresponds to bus-, gen- or branch-ordered data. It can be one
        of the following three strings: 'bus', 'gen' or 'branch'. For
        data structures with multiple blocks of data, ordered by bus,
        gen or branch, they can be converted with a single call by
        specifying C{ordering} as a list of strings.

        Any extra elements, rows, columns, etc. beyond those indicated
        in C{ordering}, are not disturbed.

    @see: L{ext2int}
    """
    ppc = deepcopy(ppc)
    if val_or_field is None: # nargin == 1
        if 'order' not in ppc:
            sys.stderr.write('int2ext: ppc does not have the "order" field '
                'require for conversion back to external numbering.\n')
        o = ppc["order"]

        if o["state"] == 'i':
            ## execute userfcn callbacks for 'int2ext' stage
            if 'userfcn' in ppc:
                ppc = run_userfcn(ppc["userfcn"], 'int2ext', ppc)

            ## save data matrices with internal ordering & restore originals
            o["int"] = {}
            o["int"]["bus"]    = ppc["bus"].copy()
            o["int"]["branch"] = ppc["branch"].copy()
            o["int"]["gen"]    = ppc["gen"].copy()
            ppc["bus"]     = o["ext"]["bus"].copy()
            ppc["branch"]  = o["ext"]["branch"].copy()
            ppc["gen"]     = o["ext"]["gen"].copy()
            if 'gencost' in ppc:
                o["int"]["gencost"] = ppc["gencost"].copy()
                ppc["gencost"] = o["ext"]["gencost"].copy()
            if 'areas' in ppc:
                o["int"]["areas"] = ppc["areas"].copy()
                ppc["areas"] = o["ext"]["areas"].copy()
            if 'A' in ppc:
                o["int"]["A"] = ppc["A"].copy()
                ppc["A"] = o["ext"]["A"].copy()
            if 'N' in ppc:
                o["int"]["N"] = ppc["N"].copy()
                ppc["N"] = o["ext"]["N"].copy()

            ## update data (in bus, branch and gen only)
            ppc["bus"][o["bus"]["status"]["on"], :] = \
                o["int"]["bus"]
            ppc["branch"][o["branch"]["status"]["on"], :] = \
                o["int"]["branch"]
            ppc["gen"][o["gen"]["status"]["on"], :] = \
                o["int"]["gen"][o["gen"]["i2e"], :]
            if 'areas' in ppc:
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
            if 'areas' in ppc:
                ppc["areas"][o["areas"]["status"]["on"], PRICE_REF_BUS] = \
                    o["bus"]["i2e"][ ppc["areas"] \
                    [o["areas"]["status"]["on"], PRICE_REF_BUS].astype(int) ]

            if 'ext' in o: del o['ext']
            o["state"] = 'e'
            ppc["order"] = o
        else:
            sys.stderr.write('int2ext: ppc claims it is already using '
                         'external numbering.\n')
    else:                    ## convert extra data
        if isinstance(val_or_field, str) or isinstance(val_or_field, list):
            ## field (key)
            field = val_or_field
            if 'int' not in ppc['order']:
                ppc['order']['int'] = {}

            if isinstance(field, str):
                key = '["%s"]' % field
            else:  # nested dicts
                key = '["%s"]' % '"]["'.join(field)

                v_int = ppc["order"]["int"]
                for fld in field:
                    if fld not in v_int:
                        v_int[fld] = {}
                        v_int = v_int[fld]

            exec 'ppc["order"]["int"]%s = ppc%s.copy()' % (key, key)
            exec 'ppc%s = int2ext(ppc, ppc%s, ppc["order"]["ext"]%s, ordering, dim)' % (key, key, key)

        else:
            ## value
            val = val_or_field.copy()
            o = ppc["order"]
            if isinstance(ordering, str):         ## single set
                if ordering == 'gen':
                    v = get_reorder(val, o[ordering]["i2e"], dim)
                else:
                    v = val
                val = set_reorder(oldval, v, o[ordering]["status"]["on"], dim)
            else:                            ## multiple sets
                be = 0  ## base, external indexing
                bi = 0  ## base, internal indexing
                new_v = []
                for ord in ordering:
                    ne = o["ext"][ord].shape[0]
                    ni = ppc[ord].shape[0]
                    v = get_reorder(val, bi + arange(ni), dim)
                    oldv = get_reorder(oldval, be + arange(ne), dim)
                    new_v.append( int2ext(ppc, v, oldv, ord, dim) )
                    be = be + ne
                    bi = bi + ni
                ni = val.shape[dim]
                if ni > bi:              ## the rest
                    v = get_reorder(val, arange(bi, ni), dim)
                    new_v.append(v)
                val = concatenate(new_v, dim)
            return val

    return ppc


def int2ext1(i2e, bus, gen, branch, areas):
    """Converts from the consecutive internal bus numbers back to the originals
    using the mapping provided by the I2E vector returned from C{ext2int}.

    @see: L{ext2int}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    bus[:, BUS_I]    = i2e[ bus[:, BUS_I].astype(int) ]
    gen[:, GEN_BUS]  = i2e[ gen[:, GEN_BUS].astype(int) ]
    branch[:, F_BUS] = i2e[ branch[:, F_BUS].astype(int) ]
    branch[:, T_BUS] = i2e[ branch[:, T_BUS].astype(int) ]

    if areas != None and len(areas) > 0:
        areas[:, PRICE_REF_BUS] = i2e[ areas[:, PRICE_REF_BUS].astype(int) ]
        return bus, gen, branch, areas

    return bus, gen, branch
