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

from numpy import ones, nonzero
from scipy.sparse import csr_matrix

from idx_bus import PD, QD
from idx_gen import GEN_BUS, PG, QG, GEN_STATUS

def makeSbus(baseMVA, bus, gen):
    """Builds the vector of complex bus power injections.

    Returns the vector of complex bus
    power injections, that is, generation minus load. Power is expressed
    in per unit.

    @see: L{makeYbus}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## generator info
    on = nonzero(gen[:, GEN_STATUS] > 0)      ## which generators are on?
    gbus = gen[on, GEN_BUS]                   ## what buses are they at?

    ## form net complex bus power injection vector
    nb = bus.shape[0]
    ngon = on.shape[0]
    ## connection matrix, element i, j is 1 if gen on(j) at bus i is ON
    Cg = csr_matrix((ones(ngon), (gbus, range(ngon))), (nb, ngon))

    ## power injected by gens plus power injected by loads converted to p.u.
    Sbus = ( Cg * (gen[on, PG] + 1j * gen[on, QG]) -
             (bus[:, PD] + 1j * bus[:, QD]) ) / baseMVA

    return Sbus
