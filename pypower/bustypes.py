# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

"""Builds index lists of each type of bus.
"""

from numpy import ones, flatnonzero as find
from scipy.sparse import csr_matrix as sparse

from pypower.idx_bus import BUS_TYPE, REF, PV, PQ
from pypower.idx_gen import GEN_BUS, GEN_STATUS


def bustypes(bus, gen):
    """Builds index lists of each type of bus (C{REF}, C{PV}, C{PQ}).

    Generators with "out-of-service" status are treated as L{PQ} buses with
    zero generation (regardless of C{Pg}/C{Qg} values in gen).

    @param bus: bus data converted to use internal consecutive bus numbering
    @param gen: generator data converted to use internal consecutive bus
    numbering
    @return: index lists of each bus type

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
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
        ref = pv[0]      # use the first PV bus
        pv = pv[1:]      # take it off PV list

    return ref, pv, pq
