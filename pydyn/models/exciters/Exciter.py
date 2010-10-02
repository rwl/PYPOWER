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

from numpy import zeros, arange, exp, r_

def Exciter(Xexc, Pexc, Vexc, exctype):
    """ Exciter model.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Init
    r, c = Xexc.shape
    F = zeros(r, c)
    d = arange(len(exctype))

    ## Define exciter types
    type1 = d[exctype == 1]
    type2 = d[exctype == 2]

    ## Exciter type 1: constant excitation
    F[type1, 0] = 0

    ## Exciter type 2: IEEE DC1A
    Efd = Xexc[type2, 0]
    Uf = Xexc[type2, 1]
    Ur = Xexc[type2, 2]

    Ka = Pexc[type2, 1]
    Ta = Pexc[type2, 2]
    Ke = Pexc[type2, 3]
    Te = Pexc[type2, 4]
    Kf = Pexc[type2, 5]
    Tf = Pexc[type2, 6]
    Aex = Pexc[type2, 7]
    Bex = Pexc[type2, 8]
    Ur_min = Pexc[type2, 9]
    Ur_max = Pexc[type2, 10]
    Uref = Pexc[type2, 11]
    Uref2 = Pexc[type2, 12]

    U = Vexc[type2, 0]

    Ux = Aex * exp(Bex * Efd)
    dUr = 1 / Ta * (Ka * (Uref - U + Uref2 - Uf) - Ur)
    dUf = 1 / Tf * (Kf / Te * (Ur - Ux - Ke * Efd) - Uf)
    if sum(Ur > Ur_max) >= 1:
        Ur2 = Ur_max
    elif sum(Ur < Ur_min) >= 1:
        Ur2 = Ur_min
    else:
        Ur2 = Ur

    dEfd = 1 / Te * (Ur2 - Ux - Ke * Efd)

    F[type2, :2] = r_[dEfd, dUf, dUr]

    ## Exciter type 3:

    ## Exciter type 4:

    return F
