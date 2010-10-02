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

def ExciterInit(Xexc, Pexc, Vexc, exctype):
    """ Calculate initial conditions exciters

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Init
    ngen, c = Xexc.shape
    Xexc0 = zeros(ngen, c)
    ngen, c = Pexc.shape
    Pexc0 = zeros(ngen, c + 2)
    d = arange(len(exctype))

    ## Define types
    type1 = d[exctype==1]
    type2 = d[exctype==2]

    ## Exciter type 1: constant excitation
    Efd0 = Xexc[type1, 0]
    Xexc0[type1, 0] = Efd0

    ## Exciter type 2: IEEE DC1A
    Efd0 = Xexc[type2, 0]
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

    U = Vexc[type2, 0]

    Uf = zeros(len(type2))
    Ux = Aex * exp(Bex * Efd0)
    Ur = Ux + Ke * Efd0
    Uref2 = U + (Ux + Ke * Efd0) / Ka - U
    Uref = U

    Xexc0[type2, :2] = r_[Efd0, Uf, Ur]
    Pexc0[type2, :12] = r_[Pexc[type2, 0], Ka, Ta, Ke, Te, Kf, Tf, Aex, Bex, Ur_min, Ur_max, Uref, Uref2]

    ## Exciter type 3

    ## Exciter type 4

    return Xexc0, Pexc0
