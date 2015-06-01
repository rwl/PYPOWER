# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Builds the line outage distribution factor matrix.
"""

from numpy import ones, diag, eye, r_, arange
from scipy.sparse import csr_matrix as sparse

from pypower.idx_brch import F_BUS, T_BUS


def makeLODF(branch, PTDF):
    """Builds the line outage distribution factor matrix.

    Returns the DC line outage distribution factor matrix for a given PTDF.
    The matrix is C{nbr x nbr}, where C{nbr} is the number of branches.

    Example::
        H = makePTDF(baseMVA, bus, branch)
        LODF = makeLODF(branch, H)

    @see: L{makePTDF}

    @author: Ray Zimmerman (PSERC Cornell)
    """
    nl, nb = PTDF.shape
    f = branch[:, F_BUS]
    t = branch[:, T_BUS]
    Cft = sparse((r_[ones(nl), -ones(nl)],
                      (r_[f, t], r_[arange(nl), arange(nl)])), (nb, nl))

    H = PTDF * Cft
    h = diag(H, 0)
    LODF = H / (ones((nl, nl)) - ones((nl, 1)) * h.T)
    LODF = LODF - diag(diag(LODF)) - eye(nl, nl)

    return LODF
