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

"""Builds the vector of complex bus power injections.
"""

from numpy import ones, flatnonzero as find
from scipy.sparse import csr_matrix as sparse

from idx_bus import PD, QD
from idx_gen import GEN_BUS, PG, QG, GEN_STATUS


def makeSbus(baseMVA, bus, gen):
    """Builds the vector of complex bus power injections.

    Returns the vector of complex bus power injections, that is, generation
    minus load. Power is expressed in per unit.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## generator info
    on = find(gen[:, GEN_STATUS] > 0)      ## which generators are on?
    gbus = gen[on, GEN_BUS]                   ## what buses are they at?

    ## form net complex bus power injection vector
    nb = bus.shape[0]
    ngon = on.shape[0]
    ## connection matrix, element i, j is 1 if gen on(j) at bus i is ON
    Cg = sparse((ones(ngon), (gbus, range(ngon))), (nb, ngon))

    ## power injected by gens plus power injected by loads converted to p.u.
    Sbus = ( Cg * (gen[on, PG] + 1j * gen[on, QG]) -
             (bus[:, PD] + 1j * bus[:, QD]) ) / baseMVA

    return Sbus
