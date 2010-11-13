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
