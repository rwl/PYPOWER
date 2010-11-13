# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

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
