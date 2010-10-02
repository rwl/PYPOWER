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

from numpy import zeros, arange, pi, copy, r_

def GovernorInit(Xgov, Pgov, Vgov, govtype):
    """ Calculate initial conditions governors.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Init
    global freq

    ngen, c = Xgov.shape
    Xgov0 = zeros(ngen, c)
    ngen, c = Pgov.shape
    Pgov0 = zeros(ngen, c + 2)
    d = arange(len(govtype))

    ## Define types
    type1 = d[govtype == 1]
    type2 = d[govtype == 2]

    ## Governor type 1: constant power
    Pm0 = Xgov[type1, 0]
    Xgov0[type1, 0] = Pm0

    ## Governor type 2: IEEE general speed-governing system
    Pm0 = Xgov[type2, 0]

    K = Pgov[type2, 1]
    T1 = Pgov[type2, 2]
    T2 = Pgov[type2, 3]
    T3 = Pgov[type2, 4]
    Pup = Pgov[type2, 5]
    Pdown = Pgov[type2, 6]
    Pmax = Pgov[type2, 7]
    Pmin = Pgov[type2, 8]

    omega0 = Vgov[type2, 0]

    zz0 = copy(Pm0)
    PP0 = copy(Pm0)


    P0 = K * (2 * pi * freq - omega0)
    xx0 = T1 * (1 - T2 / T1) * (2 * pi * freq - omega0)

    Xgov0[type2, :3] = r_[Pm0, P0, xx0, zz0]
    Pgov0[type2, :10] = r_[Pgov[type2, 0], K, T1, T2, T3, Pup, Pdown, Pmax, Pmin, PP0]

    ## Governor type 3:

    ## Governor type 4:

    return Xgov0, Pgov0
