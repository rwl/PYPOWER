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

from numpy import zeros, sin, cos, angle

def MachineCurrents(Xgen, Pgen, U, gentype):
    """ Calculates currents and electric power of generators.

    @param Xgen: state variables of generators
    @param Pgen: parameters of generators
    @param U: generator voltages
    @param gentype: generator models
    @return: triple of the form (Id = d-axis stator current,
        Iq = q-axis stator current,
        Pe = generator electric power)

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Init
    ngen, _ = Xgen.shape
    Id = zeros(ngen)
    Iq = zeros(ngen)
    Pe = zeros(ngen)
    d = range(len(gentype))

    ## Define types
    type1 = d[gentype == 1]
    type2 = d[gentype == 2]

    ## Generator type 1: classical model
    delta = Xgen[type1, 0]
    Eq_tr = Xgen[type1, 2]

    xd = Pgen[type1, 5]

    Pe[type1] = \
        1 / xd * abs(U[type1, 0]) * abs(Eq_tr) * sin(delta - angle(U[type1, 0]))

    ## Generator type 2: 4th order model

    delta = Xgen[type2, 0]
    Eq_tr = Xgen[type2, 2]
    Ed_tr = Xgen[type2, 3]

    xd_tr = Pgen[type2, 7]
    xq_tr = Pgen[type2, 8]

    theta = angle(U)

    # Tranform U to rotor frame of reference
    vd = -abs(U[type2, 0]) * sin(delta - theta[type2, 0])
    vq =  abs(U[type2, 0]) * cos(delta - theta[type2, 0])

    Id[type2] =  (vq - Eq_tr) / xd_tr
    Iq[type2] = -(vd - Ed_tr) / xq_tr

    Pe[type2] = Eq_tr * Iq[type2, 0] + Ed_tr * Id[type2, 0] + (xd_tr - xq_tr) * Id[type2,0] * Iq[type2, 0]

    return Id, Iq, Pe
