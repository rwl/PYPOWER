# Copyright (C) 2005-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY], without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

"""Tests for C{hasPQcap}.
"""

from numpy import array

from pypower.hasPQcap import hasPQcap

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end


def t_hasPQcap(quiet=False):
    """Tests for C{hasPQcap}.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    t_begin(4, quiet)

    ## generator data
    #	bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin	Pc1	Pc2	Qc1min	Qc1max	Qc2min	Qc2max	ramp_agc	ramp_10	ramp_30	ramp_q	apf
    gen = array([
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 0,   0,  0,   0,  0,  0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20,  0,  12,  0,  2,  0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20, -15, 12, -15, 2,  0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20, -12, 0,  -2,  0,  0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20, -12, 15, -2,  15, 0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20, -12, 12, -2,  2,  0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20,  0,  12,  0,  8,  0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20, -15, 12, -15, 8,  0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20, -12, 0,  -8,  0,  0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20, -12, 15, -8,  15, 0, 0, 0, 0, 0],
        [1, 10, 0, 10, -10, 1, 100, 1, 10, 2, 0, 20, -12, 12, -8,  8,  0, 0, 0, 0, 0]
    ])

    t = 'hasPQcap(gen)'
    t_is(hasPQcap(gen), [0,1,1,1,1,1,1,0,1,0,0], 12, t)

    t = 'hasPQcap(gen, \'B\')'
    t_is(hasPQcap(gen, 'B'), [0,1,1,1,1,1,1,0,1,0,0], 12, t)

    t = 'hasPQcap(gen, \'U\')'
    t_is(hasPQcap(gen, 'U'), [0,1,1,1,0,1,0,0,1,0,0], 12, t)

    t = 'hasPQcap(gen, \'L\')'
    t_is(hasPQcap(gen, 'L'), [0,1,0,1,1,1,1,0,0,0,0], 12, t)

    t_end()


if __name__ == '__main__':
    t_hasPQcap(quiet=False)
