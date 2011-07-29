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

"""Which OPF solver is used by alg.
"""

from numpy import remainder


def opf_slvr(alg):
    """Which OPF solver is used by alg.

    Returns a solver code given an algorithm code.
    The codes are:
        0 - 'constr' from Optimization Toolbox 1.x or 2.x
        1 - 'LPconstr', dense LP-based solver
        2 - 'LPconstr', sparse LP-based solver with relaxed constraints
        3 - 'LPconstr', sparse LP-based solver with full set of constraints
        4 - 'fmincon', from Optimization Toolbox 2.x and later
        5 - 'minopf', MINOS-based solver

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    if alg < 500:
        code = remainder(alg, 100) / 20
        if code != 0 and code != 1 and code != 2 and code != 3:
            raise ValueError, 'opf_slvr: unknown OPF algorithm (' + str(alg) + ')'
    elif alg == 520:
        code = 4
    elif alg == 500:
        code = 5
    else:
        raise ValueError, 'opf_slvr: unknown OPF algorithm (' + str(alg) + ')'

    return code
