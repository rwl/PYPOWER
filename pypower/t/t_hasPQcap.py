# Copyright (C) 2005-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
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
