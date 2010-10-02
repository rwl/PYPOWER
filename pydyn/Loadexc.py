# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
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

from numpy import copy

def Loadexc(casefile_dyn):
    """ Loads exciter data.

    @param casefile_dyn: m-file or struct with dynamic data
    @return: exciter parameter matrix

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    # Load data
    if isinstance(casefile_dyn, dict):
        exc = casefile_dyn["exc"]
    else:
        dyn = __import__(casefile_dyn)
        _, exc, _, _, _, _ = eval("dyn.%s" % casefile_dyn)

    ## Consecutive numbering or rows
    Pexc = copy(exc)

    for i in range(len(exc[0, :])):
        Pexc[exc[:, 0], i] = exc[:, i]

    return Pexc
