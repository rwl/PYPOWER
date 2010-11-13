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

from numpy import ones, flatnonzero as find
from scipy.sparse import csr_matrix as sparse

from idx_bus import BUS_TYPE, REF, PV, PQ
from idx_gen import GEN_BUS, GEN_STATUS

def bustypes(bus, gen):
    """Builds index lists of each type of bus (REF, PV, PQ).

    Generators with "out-of-service" status are treated as PQ buses with
    zero generation (regardless of Pg/Qg values in gen). Expects BUS and
    GEN have been converted to use internal consecutive bus numbering.

    @type bus: array
    @param bus: Bus data.
    @type gen: array
    @param gen: Generator data.
    @rtype: tuple
    @return: Index lists of each type of bus.
    @see: U{http://www.pserc.cornell.edu/matpower/}
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
