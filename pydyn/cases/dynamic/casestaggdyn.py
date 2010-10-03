# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0, (the "License")
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

from numpy import array

def casestaggdyn():
    """ PyDyn dynamic data file.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## General data

    freq = 60.0
    stepsize = 0.02
    stoptime = 0.9

    ## Generator data

    # [genmodel excmodel govmodel H D xd xq xd_tr xq_tr Td_tr Tq_tr]
    gen = array([
        [1, 1, 1, 50, 0, 0.25, 0.25, 0, 0, 0, 0]
        [1, 1, 1, 1,  0, 1.50, 1.50, 0, 0, 0, 0]
    ])

    ## Exciter data

    # [gen Ka  Ta  Ke  Te  Kf  Tf  Aex  Bex  Ur_min  Ur_max]
    exc = array([
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])

    ## Governor data

    # [gen K  T1  T2  T3  Pup  Pdown  Pmax  Pmin]
    gov = array([
        [1.0, 0, 0, 0, 0, 0, 0, 0, 0]
        [2.0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])

    return gen, exc, gov, freq, stepsize, stoptime
