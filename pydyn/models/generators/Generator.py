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

from numpy import zeros, arange, pi, r_

def Generator(Xgen, Xexc, Xgov, Pgen, Vgen, gentype):
    """ Generator model.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Init
    global freq
    omegas = 2 * pi * freq

    r, c = Xgen.shape
    F = zeros(r, c)
    d = arange(len(gentype))

    ## Define generator types
    type1 = d[gentype == 1]
    type2 = d[gentype == 2]

    ## Generator type 1: classical model
    omega = Xgen[type1, 1]
    Pm0 = Xgov[type1, 0]

    H = Pgen[type1, 3]
    D = Pgen[type1, 4]

    Pe = Vgen[type1, 2]

    ddelta = omega - omegas
    domega = pi * freq / H * (-D * (omega - omegas) + Pm0 - Pe)
    dEq = zeros(len(type1))

    F[type1, :2] = r_[ddelta, domega, dEq]

    ## Generator type 2: 4th order model
    omega = Xgen[type2, 1]
    Eq_tr = Xgen[type2, 2]
    Ed_tr = Xgen[type2, 3]

    H = Pgen[type2, 3]
    D = Pgen[type2, 4]
    xd = Pgen[type2, 5]
    xq = Pgen[type2, 6]
    xd_tr = Pgen[type2, 7]
    xq_tr = Pgen[type2, 8]
    Td0_tr = Pgen[type2, 9]
    Tq0_tr = Pgen[type2, 10]

    Id = Vgen[type2, 0]
    Iq = Vgen[type2, 1]
    Pe = Vgen[type2, 2]

    Efd = Xexc[type2, 0]
    Pm = Xgov[type2, 0]

    ddelta = omega - omegas
    domega = pi * freq / H * (-D * (omega - omegas) + Pm - Pe)
    dEq = 1 / Td0_tr * (Efd - Eq_tr + (xd - xd_tr) * Id)
    dEd = 1 / Tq0_tr * (-Ed_tr - (xq - xq_tr) * Iq)

    F[type2, :3] = r_[ddelta, domega, dEq, dEd]

    ## Generator type 3:

    ## Generator type 4:

    return F
