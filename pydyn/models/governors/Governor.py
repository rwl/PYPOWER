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

def Governor(Xgov, Pgov, Vgov, govtype):
    """ Governor model.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Init
    global freq
    omegas = 2 * pi * freq

    r, c = Xgov.shape
    F = zeros(r, c)
    d = arange(len(govtype))

    ## Define governor types
    type1 = d[govtype == 1]
    type2 = d[govtype == 2]

    ## Governor type 1: constant power
    F[type1, 0] = 0

    ## Governor type 2: IEEE general speed-governing system
    Pm = Xgov[type2, 0]
    P = Xgov[type2, 1]
    x = Xgov[type2, 2]
    z = Xgov[type2, 3]

    K = Pgov[type2, 1]
    T1 = Pgov[type2, 2]
    T2 = Pgov[type2, 3]
    T3 = Pgov[type2, 4]
    Pup = Pgov[type2, 5]
    Pdown = Pgov[type2, 6]
    Pmax = Pgov[type2, 7]
    Pmin = Pgov[type2, 8]
    P0 = Pgov[type2, 9]

    omega = Vgov[type2, 0]

    dx = K * (-1 / T1 * x + (1 - T2 / T1) * (omega - omegas))
    dP = 1 / T1 * x + T2 / T1 * (omega - omegas)

    y = 1 / T3 * (P0 - P - Pm)

    y2 = copy(y)

    if sum(y > Pup) >= 1:
        y2 = (1 - (y > Pup)) * y2 + (y > Pup) * Pup

    if sum(y < Pdown) >= 1:
        y2 = (1 - (y < Pdown)) * y2 + (y < Pdown) * Pdown

    dz = copy(y2)

    dPm = copy(y2)

    if sum(z > Pmax) >= 1:
        dPm = (1 - (z > Pmax)) * dPm + (z > Pmax) * 0

    if sum(z < Pmin) >= 1:
        dPm = (1 - (z < Pmin)) * dPm + (z < Pmin) * 0

    F[type2, :3] = r_[dPm, dP, dx, dz]

    ## Governor type 3

    ## Governor type 4

    return F
