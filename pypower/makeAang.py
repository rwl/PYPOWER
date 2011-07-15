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

"""Construct constraints for branch angle difference limits.
"""

from numpy import array, ones, zeros, r_, Inf, pi, arange
from numpy import flatnonzero as find
from scipy.sparse import csr_matrix as sparse

from idx_brch import F_BUS, T_BUS, ANGMIN, ANGMAX


def makeAang(baseMVA, branch, nb, ppopt):
    """Construct constraints for branch angle difference limits.

    Constructs the parameters for the following linear constraint limiting
    the voltage angle differences across branches, where C{Va} is the vector
    of bus voltage angles. C{nb} is the number of buses::

        lang <= Aang * Va <= uang

    C{iang} is the vector of indices of branches with angle difference limits.
    """
    ## options
    ignore_ang_lim = ppopt['OPF_IGNORE_ANG_LIM']

    if ignore_ang_lim:
        Aang  = zeros((0, nb))
        lang  = array([])
        uang  = array([])
        iang  = array([])
    else:
        iang = find(((branch[:, ANGMIN] != 0) & (branch[:, ANGMIN] > -360)) |
                    ((branch[:, ANGMAX] != 0) & (branch[:, ANGMAX] <  360)))
        iangl = find(branch[iang, ANGMIN])
        iangh = find(branch[iang, ANGMAX])
        nang = len(iang)

        if nang > 0:
            ii = r_[arange(nang), arange(nang)]
            jj = r_[branch[iang, F_BUS], branch[iang, T_BUS]]
            Aang = sparse((r_[ones(nang), -ones(nang)],
                           (ii, jj)), (nang, nb))
            uang = Inf * ones(nang)
            lang = -uang
            lang[iangl] = branch[iang[iangl], ANGMIN] * pi / 180
            uang[iangh] = branch[iang[iangh], ANGMAX] * pi / 180
        else:
            Aang  = zeros((0, nb))
            lang  = array([])
            uang  = array([])

    return Aang, lang, uang, iang
