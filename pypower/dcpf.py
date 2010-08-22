# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

from numpy import r_
from scipy.sparse.linalg import spsolve

def dcpf(B, Pbus, Va0, ref, pv, pq):
    """ Solves a DC power flow.

    Solves for the bus voltage angles at all but the reference bus, given the
    full system B matrix and the vector of bus real power injections, the
    initial vector of bus voltage angles (in radians), and column vectors with
    the lists of bus indices for the swing bus, PV buses, and PQ buses,
    respectively. Returns a vector of bus voltage angles in radians.

    @see: L{rundcpf}, L{runpf}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## initialize result vector
    Va = Va0

    ## update angles for non-reference buses
    Va[r_[pv, pq]] = spsolve(B[r_[pv, pq], r_[pv, pq]],
                             Pbus[r_[pv, pq]] - B[r_[pv, pq], ref] * Va0[ref])

    return Va
