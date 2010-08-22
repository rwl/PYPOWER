# Copyright (C) 2008-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
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
