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

from numpy import array

def casestaggdyn2():
    """ PyDyn dynamic data file.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## General data

    freq = 60.0
    stepsize = 0.01
    stoptime = 0.9

    ## Generator data

    # [genmodel excmodel govmodel H D xd xq xd_tr xq_tr Td_tr Tq_tr]
    gen = array([
        [2, 2, 1, 50, 0, 1.93, 1.77, 0.25, 0.25, 5.2, 0.81],
        [2, 1, 1,  1, 0, 1.93, 1.77, 1.50, 1.50, 5.2, 0.81]
    ])

    ## Exciter data

    # [gen Ka  Ta  Ke  Te  Kf  Tf  Aex  Bex  Ur_min  Ur_max]
    exc = array([
        [1, 50, 0.05, -0.17, 0.95, 0.04, 1, 0.014, 1.55, -1.7, 1.7],
        [2,  0,    0,     0,    0,    0, 0,     0,    0,    0,   0]
    ])

    ## Governor data

    # [gen K  T1  T2  T3  Pup  Pdown  Pmax  Pmin]
    gov = array([
        [1.0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2.0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])

    return gen, exc, gov, freq, stepsize, stoptime
