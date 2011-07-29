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

"""Solves a DC power flow.
"""

from numpy import copy, r_, matrix
from scipy.sparse.linalg import spsolve


def dcpf(B, Pbus, Va0, ref, pv, pq):
    """Solves a DC power flow.

    Solves for the bus voltage angles at all but the reference bus, given the
    full system C{B} matrix and the vector of bus real power injections, the
    initial vector of bus voltage angles (in radians), and column vectors with
    the lists of bus indices for the swing bus, PV buses, and PQ buses,
    respectively. Returns a vector of bus voltage angles in radians.

    @see: L{rundcpf}, L{runpf}

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    pvpq = matrix(r_[pv, pq])

    ## initialize result vector
    Va = copy(Va0)

    Va[pvpq] = spsolve(B[pvpq.T, pvpq], Pbus[pvpq] - B[pvpq.T, ref] * Va0[ref])

    return Va
