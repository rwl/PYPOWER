# Copyright (C) 1996-2010 Power System Engineering Research Center
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

import logging

from numpy import array, zeros, nonzero, sin, cos, arctan2, r_
from scipy.sparse import csr_matrix

from idx_gen import PG, QG, PMIN, QMIN, QMAX

from isload import isload

logger = logging.getLogger(__name__)

def makeAvl(baseMVA, gen):
    """Construct linear constraints for constant power factor var loads.

    Constructs parameters for the following linear constraint enforcing a
    constant power factor constraint for dispatchable loads.

         LVL <= AVL * [Pg Qg] <= UVL

    IVL is the vector of indices of generators representing variable loads.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## data dimensions
    ng = gen.shape[0]      ## number of dispatchable injections
    Pg   = gen[:, PG] / baseMVA
    Qg   = gen[:, QG] / baseMVA
    Pmin = gen[:, PMIN] / baseMVA
    Qmin = gen[:, QMIN] / baseMVA
    Qmax = gen[:, QMAX] / baseMVA

    # Find out if any of these "generators" are actually dispatchable loads.
    # (see 'help isload' for details on what constitutes a dispatchable load)
    # Dispatchable loads are modeled as generators with an added constant
    # power factor constraint. The power factor is derived from the original
    # value of Pmin and either Qmin (for inductive loads) or Qmax (for
    # capacitive loads). If both Qmin and Qmax are zero, this implies a unity
    # power factor without the need for an additional constraint.

    ivl = nonzero( isload(gen) & (Qmin != 0 | Qmax != 0) )
    nvl = ivl.shape[0]  ## number of dispatchable loads

    ## at least one of the Q limits must be zero (corresponding to Pmax == 0)
    if any( Qmin[ivl] != 0 & Qmax[ivl] != 0 ):
        logger.error('makeAvl: either Qmin or Qmax must be equal to zero for '
                     'each dispatchable load.')

    # Initial values of PG and QG must be consistent with specified power
    # factor This is to prevent a user from unknowingly using a case file which
    # would have defined a different power factor constraint under a previous
    # version which used PG and QG to define the power factor.
    Qlim = (Qmin[ivl] == 0) * Qmax[ivl] + (Qmax[ivl] == 0) * Qmin[ivl]
    if any( abs( Qg[ivl] - Pg[ivl] * Qlim / Pmin[ivl] ) > 1e-6 ):
        logger.error('makeAvl: For a dispatchable load, PG and QG must be '
                     'consistent with the power factor defined by PMIN and '
                     'the Q limits.')

    # make Avl, lvl, uvl, for lvl <= Avl * [Pg Qg] <= uvl
    if nvl > 0:
        xx = Pmin[ivl]
        yy = Qlim
        pftheta = arctan2(yy, xx)
        pc = sin(pftheta)
        qc = -cos(pftheta)
        ii = r_[ range(nvl), range(nvl) ]
        jj = r_[ ivl, ivl + ng ]
        Avl = csr_matrix((r_[pc, qc], (ii, jj)), (nvl, 2 * ng))
        lvl = zeros(nvl)
        uvl = lvl
    else:
        Avl = zeros(0, 2 * ng)
        lvl = array([])
        uvl = array([])

    return Avl, lvl, uvl, ivl
