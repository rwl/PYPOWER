# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Builds index lists of each type of bus.
"""

from numpy import ones, flatnonzero as find
from numpy import zeros
from scipy.sparse import csr_matrix as sparse

from pypower.idx_bus import BUS_TYPE, REF, PV, PQ
from pypower.idx_gen import GEN_BUS, GEN_STATUS


def bustypes(bus, gen):
    """Builds index lists of each type of bus (C{REF}, C{PV}, C{PQ}).

    Generators with "out-of-service" status are treated as L{PQ} buses with
    zero generation (regardless of C{Pg}/C{Qg} values in gen). Expects C{bus}
    and C{gen} have been converted to use internal consecutive bus numbering.

    @param bus: bus data
    @param gen: generator data
    @return: index lists of each bus type

    @author: Ray Zimmerman (PSERC Cornell)
    """
    # get generator status
    nb = bus.shape[0]
    ng = gen.shape[0]
    # gen connection matrix, element i, j is 1 if, generator j at bus i is ON
    Cg = sparse((gen[:, GEN_STATUS] > 0,
                 (gen[:, GEN_BUS], range(ng))), (nb, ng))
    # number of generators at each bus that are ON
    bus_gen_status = (Cg * ones(ng, int)).astype(bool)

    # form index lists for slack, PV, and PQ buses
    ref = find((bus[:, BUS_TYPE] == REF) & bus_gen_status) # ref bus index
    pv  = find((bus[:, BUS_TYPE] == PV)  & bus_gen_status) # PV bus indices
    pq  = find((bus[:, BUS_TYPE] == PQ) | ~bus_gen_status) # PQ bus indices

    # pick a new reference bus if for some reason there is none (may have been
    # shut down)
    if len(ref) == 0:
        ref = zeros(1, dtype=int)
        ref = pv[0]      # use the first PV bus
        pv = pv[1:]      # take it off PV list

    return ref, pv, pq
