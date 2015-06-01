# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Converts internal to external bus numbering.
"""

import sys

from warnings import warn

from copy import deepcopy

from pypower.idx_bus import BUS_I
from pypower.idx_gen import GEN_BUS
from pypower.idx_brch import F_BUS, T_BUS
from pypower.idx_area import PRICE_REF_BUS

from pypower.run_userfcn import run_userfcn

from pypower.i2e_field import i2e_field
from pypower.i2e_data import i2e_data


def int2ext(ppc, val_or_field=None, oldval=None, ordering=None, dim=0):
    """Converts internal to external bus numbering.

    C{ppc = int2ext(ppc)}

    If the input is a single PYPOWER case dict, then it restores all
    buses, generators and branches that were removed because of being
    isolated or off-line, and reverts to the original generator ordering
    and original bus numbering. This requires that the 'order' key
    created by L{ext2int} be in place.

    Example::
        ppc = int2ext(ppc)

    @see: L{ext2int}, L{i2e_field}, L{i2e_data}

    @author: Ray Zimmerman (PSERC Cornell)
    """
    ppc = deepcopy(ppc)
    if val_or_field is None: # nargin == 1
        if 'order' not in ppc:
            sys.stderr.write('int2ext: ppc does not have the "order" field '
                'required for conversion back to external numbering.\n')
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
            warn('Calls of the form MPC = INT2EXT(MPC, ''FIELD_NAME'', ...) have been deprecated. Please replace INT2EXT with I2E_FIELD.')
            bus, gen = val_or_field, oldval
            if ordering is not None:
                dim = ordering
            ppc = i2e_field(ppc, bus, gen, dim)
        else:
            ## value
            warn('Calls of the form VAL = INT2EXT(MPC, VAL, ...) have been deprecated. Please replace INT2EXT with I2E_DATA.')
            bus, gen, branch = val_or_field, oldval, ordering
            ppc = i2e_data(ppc, bus, gen, branch, dim)

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
