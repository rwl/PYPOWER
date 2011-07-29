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

"""Which OPF formulation is used by alg.
"""

from numpy import fix


def opf_form(alg):
    """Which OPF formulation is used by alg.

    Returns a formulation code given an algorithm code.
    The codes are:
        1 - standard, polynomial costs handled in the objective function
        2 - CCV, piece-wise linear costs handled via constrainted cost vars
        5 - generalized, includes both of above and more

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    return fix(alg / 100)
