# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
#
# PYDYN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYDYN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYDYN. If not, see <http://www.gnu.org/licenses/>.

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
