# Copyright (C) 2010-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

from numpy import array

from pypower.totcost import totcost
from pypower.modcost import modcost

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end


def t_modcost(quiet=False):
    """Tests for code in C{modcost}.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    n_tests = 80,

    t_begin(n_tests, quiet)

    ## generator cost data
    #    1    startup    shutdown    n    x1    y1    ...    xn    yn
    #    2    startup    shutdown    n    c(n-1)    ...    c0
    gencost0 = array([
        [2, 0, 0, 3, 0.01,   0.1,   1,    0,    0,  0,      0,    0],
        [2, 0, 0, 5, 0.0006, 0.005, 0.04, 0.3,  2,  0,      0,    0],
        [1, 0, 0, 4, 0,      0,     10,   200,  20, 600,   30, 1200],
        [1, 0, 0, 4, -30,   -2400, -20, -1800, -10, -1000,  0,    0]
    ])

    gencost = modcost(gencost0, 5, 'SCALE_F')

    t = 'modcost SCALE_F - quadratic',
    t_is(totcost(gencost, array([0, 0, 0, 0])) / 5, array([1, 2, 0, 0]), 8, t)
    t_is(totcost(gencost, array([1, 0, 0, 0])) / 5, array([1.11, 2, 0, 0]), 8, t)
    t_is(totcost(gencost, array([2, 0, 0, 0])) / 5, array([1.24, 2, 0, 0]), 8, t)

    t = 'modcost SCALE_F - 4th order polynomial',
    t_is(totcost(gencost, array([0, 0, 0, 0])) / 5, array([1, 2,      0, 0]), 8, t)
    t_is(totcost(gencost, array([0, 1, 0, 0])) / 5, array([1, 2.3456, 0, 0]), 8, t)
    t_is(totcost(gencost, array([0, 2, 0, 0])) / 5, array([1, 2.8096, 0, 0]), 8, t)

    t = 'modcost SCALE_F - pwl (gen)',
    t_is(totcost(gencost, array([0, 0, 5, 0 ])) / 5, array([1, 2, 100, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 10, 0])) / 5, array([1, 2, 200, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 15, 0])) / 5, array([1, 2, 400, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 20, 0])) / 5, array([1, 2, 600, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 25, 0])) / 5, array([1, 2, 900, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 30, 0])) / 5, array([1, 2, 1200, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 35, 0])) / 5, array([1, 2, 1500, 0]), 8, t)

    t = 'modcost SCALE_F - pwl (load)',
    t_is(totcost(gencost, array([0, 0, 0, -5 ])) / 5, array([1, 2, 0, -500]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -10])) / 5, array([1, 2, 0, -1000]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -15])) / 5, array([1, 2, 0, -1400]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -20])) / 5, array([1, 2, 0, -1800]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -25])) / 5, array([1, 2, 0, -2100]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -30])) / 5, array([1, 2, 0, -2400]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -35])) / 5, array([1, 2, 0, -2700]), 8, t)


    gencost = modcost(gencost0, 2, 'SCALE_X')

    t = 'modcost SCALE_X - quadratic',
    t_is(totcost(gencost, array([0, 0, 0, 0]) * 2), array([1, 2, 0, 0]), 8, t)
    t_is(totcost(gencost, array([1, 0, 0, 0]) * 2), array([1.11, 2, 0, 0]), 8, t)
    t_is(totcost(gencost, array([2, 0, 0, 0]) * 2), array([1.24, 2, 0, 0]), 8, t)

    t = 'modcost SCALE_X - 4th order polynomial',
    t_is(totcost(gencost, array([0, 0, 0, 0]) * 2), array([1, 2,      0, 0]), 8, t)
    t_is(totcost(gencost, array([0, 1, 0, 0]) * 2), array([1, 2.3456, 0, 0]), 8, t)
    t_is(totcost(gencost, array([0, 2, 0, 0]) * 2), array([1, 2.8096, 0, 0]), 8, t)

    t = 'modcost SCALE_X - pwl (gen)',
    t_is(totcost(gencost, array([0, 0, 5, 0 ]) * 2), array([1, 2, 100, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 10, 0]) * 2), array([1, 2, 200, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 15, 0]) * 2), array([1, 2, 400, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 20, 0]) * 2), array([1, 2, 600, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 25, 0]) * 2), array([1, 2, 900, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 30, 0]) * 2), array([1, 2, 1200, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 35, 0]) * 2), array([1, 2, 1500, 0]), 8, t)

    t = 'modcost SCALE_X - pwl (load)',
    t_is(totcost(gencost, array([0, 0, 0, -5 ]) * 2), array([1, 2, 0, -500]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -10]) * 2), array([1, 2, 0, -1000]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -15]) * 2), array([1, 2, 0, -1400]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -20]) * 2), array([1, 2, 0, -1800]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -25]) * 2), array([1, 2, 0, -2100]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -30]) * 2), array([1, 2, 0, -2400]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -35]) * 2), array([1, 2, 0, -2700]), 8, t)


    gencost = modcost(gencost0, 3, 'SHIFT_F')

    t = 'modcost SHIFT_F - quadratic',
    t_is(totcost(gencost, array([0, 0, 0, 0])) - 3, array([1,    2, 0, 0]), 8, t)
    t_is(totcost(gencost, array([1, 0, 0, 0])) - 3, array([1.11, 2, 0, 0]), 8, t)
    t_is(totcost(gencost, array([2, 0, 0, 0])) - 3, array([1.24, 2, 0, 0]), 8, t)

    t = 'modcost SHIFT_F - 4th order polynomial',
    t_is(totcost(gencost, array([0, 0, 0, 0])) - 3, array([1, 2,      0, 0]), 8, t)
    t_is(totcost(gencost, array([0, 1, 0, 0])) - 3, array([1, 2.3456, 0, 0]), 8, t)
    t_is(totcost(gencost, array([0, 2, 0, 0])) - 3, array([1, 2.8096, 0, 0]), 8, t)

    t = 'modcost SHIFT_F - pwl (gen)',
    t_is(totcost(gencost, array([0, 0, 5, 0 ])) - 3, array([1, 2, 100, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 10, 0])) - 3, array([1, 2, 200, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 15, 0])) - 3, array([1, 2, 400, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 20, 0])) - 3, array([1, 2, 600, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 25, 0])) - 3, array([1, 2, 900, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 30, 0])) - 3, array([1, 2, 1200, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 35, 0])) - 3, array([1, 2, 1500, 0]), 8, t)

    t = 'modcost SHIFT_F - pwl (load)',
    t_is(totcost(gencost, array([0, 0, 0, -5 ])) - 3, array([1, 2, 0, -500]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -10])) - 3, array([1, 2, 0, -1000]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -15])) - 3, array([1, 2, 0, -1400]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -20])) - 3, array([1, 2, 0, -1800]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -25])) - 3, array([1, 2, 0, -2100]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -30])) - 3, array([1, 2, 0, -2400]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -35])) - 3, array([1, 2, 0, -2700]), 8, t)


    gencost = modcost(gencost0, -4, 'SHIFT_X')

    t = 'modcost SHIFT_X - quadratic',
    t_is(totcost(gencost, array([0, 0, 0, 0]) - 4), array([1,    2, 0, 0]), 8, t)
    t_is(totcost(gencost, array([1, 0, 0, 0]) - 4), array([1.11, 2, 0, 0]), 8, t)
    t_is(totcost(gencost, array([2, 0, 0, 0]) - 4), array([1.24, 2, 0, 0]), 8, t)

    t = 'modcost SHIFT_X - 4th order polynomial',
    t_is(totcost(gencost, array([0, 0, 0, 0]) - 4), array([1, 2,      0, 0]), 8, t)
    t_is(totcost(gencost, array([0, 1, 0, 0]) - 4), array([1, 2.3456, 0, 0]), 8, t)
    t_is(totcost(gencost, array([0, 2, 0, 0]) - 4), array([1, 2.8096, 0, 0]), 8, t)

    t = 'modcost SHIFT_X - pwl (gen)',
    t_is(totcost(gencost, array([0, 0, 5, 0 ]) - 4), array([1, 2, 100, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 10, 0]) - 4), array([1, 2, 200, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 15, 0]) - 4), array([1, 2, 400, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 20, 0]) - 4), array([1, 2, 600, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 25, 0]) - 4), array([1, 2, 900, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 30, 0]) - 4), array([1, 2, 1200, 0]), 8, t)
    t_is(totcost(gencost, array([0, 0, 35, 0]) - 4), array([1, 2, 1500, 0]), 8, t)

    t = 'modcost SHIFT_X - pwl (load)',
    t_is(totcost(gencost, array([0, 0, 0, -5 ]) - 4), array([1, 2, 0, -500]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -10]) - 4), array([1, 2, 0, -1000]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -15]) - 4), array([1, 2, 0, -1400]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -20]) - 4), array([1, 2, 0, -1800]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -25]) - 4), array([1, 2, 0, -2100]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -30]) - 4), array([1, 2, 0, -2400]), 8, t)
    t_is(totcost(gencost, array([0, 0, 0, -35]) - 4), array([1, 2, 0, -2700]), 8, t)

    t_end