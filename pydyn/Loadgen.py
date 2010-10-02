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

def Loadgen(casefile_dyn, output):
    """ Loads generator data.

    @param casefile_dyn: m-file or struct with dynamic data
    @param output: print progress info?
    @return: generator parameter matrix

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Load data
    if isinstance(casefile_dyn, dict):
        gen = casefile_dyn["gen"]
    else:
        dyn = __import__(casefile_dyn)
        gen, _, _, _, _, _ = eval("dyn.%s" % casefile_dyn)

    Pgen = copy(gen)

    genmodel = Pgen[:, 0]

    ## Define generator models
    d = range(len(genmodel))
    type1 = d[genmodel == 1]
    type2 = d[genmodel == 2]

    ## Check transient saliency
    xd_tr = Pgen[type2, 7]
    xq_tr = Pgen[type2, 8]

    if sum(xd_tr != xq_tr) >= 1:
        if output:
            print 'Warning: transient saliency not supported'
        Pgen[type2, 8] = Pgen[type2, 7]

    return Pgen
