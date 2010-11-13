# Copyright (C) 2008-2010 Power System Engineering Research Center (PSERC)
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

from numpy import ones, diag, eye, r_
from scipy.sparse import csr_matrix

from idx_brch import F_BUS, T_BUS

def makeLODF(branch, PTDF):
    """Builds the line outage distribution factor matrix.

    Returns the DC line outage distribution factor matrix for a given PTDF.
    The matrix is nbr x nbr, where nbr is the number of branches.

    Example:
        H = makePTDF(baseMVA, bus, branch)
        LODF = makeLODF(branch, H)

    @see: L{makePTDF}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    nl, nb = PTDF.shape
    f = branch[:, F_BUS]
    t = branch[:, T_BUS]
    Cft = csr_matrix(([ones(nl, 1) -ones(nl, 1)],
                      (r_[f, t], r_[range(nl), range(nl)])), (nb, nl))

    H = PTDF * Cft
    h = diag(H, 0)
    LODF = H / (ones((nl, nl)) - ones(nl) * h.T)
    LODF = LODF - diag(diag(LODF)) - eye(nl)

    return LODF
