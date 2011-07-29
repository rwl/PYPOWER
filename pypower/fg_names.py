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

"""Function names which evaluate objective, constraints & gradients.
"""

from pypower.opf_form import opf_form


def fg_names(alg):
    """Returns names of functions which evaluate objective, constraints & grad.

    Returns the names of two functions. The first evaluates the objective
    function and constraints for the opf algorithm specified by alg, the
    numerical ID of the opf algorithm. The second evaluates the gradient of the
    first.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    if opf_form(alg) == 1:       ## standard
        fun     = 'fun_std'
        grad    = 'grad_std'
    else:    ## 2                ## CCV
        fun     = 'fun_ccv'
        grad    = 'grad_ccv'

    return fun, grad
