# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

""" Builds lists of each type of bus (ref, pv, pq).

    Ported from:
      D. Zimmerman, "bustypes.m", MATPOWER, version 3.2,
      Power System Engineering Research Center (PSERC), 2004

    Enforcing of generator Q limits inspired by contributions from
    Mu Lin, Lincoln University, New Zealand.
"""

from cvxopt import spmatrix

from idx_bus import BUS_TYPE, REF, PV, PQ
from idx_gen import GEN_BUS, GEN_STATUS

def bustypes(bus, gen):
    """ Builds lists of each type of bus (ref, pv, pq).

        Generators with "out-of-service" status are treated as PQ buses with
        zero generation (regardless of Pg/Qg values in gen).
    """
    # get generator status
#    bus_gen_status = zeros(size(bus, 1), 1);
#    bus_gen_status(gen(:, GEN_BUS)) = gen(:, GEN_STATUS) > 0;
    nb = bus.size[0]
    ng = gen.size[0]
    # gen connection matrix
    Cg = spmatrix
#    Cg = sparse(gen(:, GEN_BUS), [1:ng].T, gen(:, GEN_STATUS) > 0, nb, ng)
    # element i, j is 1 if, generator j at bus i is ON
    bus_gen_status = Cg * ones(ng, 1)
    # number of generators at each bus that are ON


    # form index lists for slack, PV, and PQ buses
#    ref = find(bus(:, BUS_TYPE) == REF & bus_gen_status) # reference bus index
#    pv  = find(bus(:, BUS_TYPE) == PV  & bus_gen_status) # PV bus indices
#    pq  = find(bus(:, BUS_TYPE) == PQ | ~bus_gen_status) # PQ bus indices

    # pick a new reference bus if for some reason there is none (may have been
    # shut down)
#    if isempty(ref)
#        ref = pv(1);                %% use the first PV bus
#        pv = pv(2:length(pv));      %% take it off PV list
#    end
