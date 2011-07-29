# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

"""Power flow data for 9 bus, 3 generator case.
"""

from numpy import array


def t_case9_pf():
    """Power flow data for 9 bus, 3 generator case.
    Please see L{caseformat} for details on the case file format.

    @return: Power flow data for 9 bus, 3 generator case, no OPF data.
    """
    ##-----  Power Flow Data  -----##
    ## system MVA base
    baseMVA = 100.0

    ## bus data
    # bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
    bus = array([
        [1,  3, 0,   0,  0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [2,  2, 0,   0,  0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [30, 2, 0,   0,  0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [4,  1, 0,   0,  0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [5,  1, 90,  30, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [6,  1, 0,   0,  0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [7,  1, 100, 35, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [8,  1, 0,   0,  0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [9,  1, 125, 50, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9]
    ])

    ## generator data
    # bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin, Pc1, Pc2,
    # Qc1min, Qc1max, Qc2min, Qc2max, ramp_agc, ramp_10, ramp_30, ramp_q, apf
    gen = array([
        [1,  0,   0, 300, -300, 1, 100, 1, 250, 90],
        [2,  163, 0, 300, -300, 1, 100, 1, 300, 10],
        [30, 85,  0, 300, -300, 1, 100, 1, 270, 10]
    ], float)

    ## branch data
    # fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax
    branch = array([
        [1,  4, 0,      0.0576, 0,     250, 250, 250, 0, 0, 1],
        [4,  5, 0.017,  0.092,  0.158, 250, 250, 250, 0, 0, 1],
        [5,  6, 0.039,  0.17,   0.358, 150, 150, 150, 0, 0, 1],
        [30, 6, 0,      0.0586, 0,     300, 300, 300, 0, 0, 1],
        [6,  7, 0.0119, 0.1008, 0.209, 40,  150, 150, 0, 0, 1],
        [7,  8, 0.0085, 0.072,  0.149, 250, 250, 250, 0, 0, 1],
        [8,  2, 0,      0.0625, 0,     250, 250, 250, 0, 0, 1],
        [8,  9, 0.032,  0.161,  0.306, 250, 250, 250, 0, 0, 1],
        [9,  4, 0.01,   0.085,  0.176, 250, 250, 250, 0, 0, 1]
    ])

    return baseMVA, bus, gen, branch
