# Copyright (C) 1996-2011 Power System Engineering Research Center
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

"""Power flow data for 9 bus, 3 generator case.
"""

from numpy import array


def case9Q():
    """Power flow data for 9 bus, 3 generator case.
    Please see L{caseformat} for details on the case file format.

    Identical to L{case9}, with the addition of non-zero costs for
    reactive power.

    @return: Power flow data for 9 bus, 3 generator case.
    """

    ##-----  Power Flow Data  -----##
    ## system MVA base
    baseMVA = 100.0

    ## bus data
    # bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
    bus = array([
        [1, 3, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [2, 2, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [3, 2, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [4, 1, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [5, 1, 90,  30, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [6, 1, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [7, 1, 100, 35, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [8, 1, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [9, 1, 125, 50, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9]
    ])

    ## generator data
    # bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin
    gen = array([
        [1, 0,   0, 300, -300, 1, 100, 1, 250, 10],
        [2, 163, 0, 300, -300, 1, 100, 1, 300, 10],
        [3, 85,  0, 300, -300, 1, 100, 1, 270, 10]
    ])

    ## branch data
    # fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status
    branch = array([
        [1, 4, 0,      0.0576, 0,     250, 250, 250, 0, 0, 1],
        [4, 5, 0.017,  0.092,  0.158, 250, 250, 250, 0, 0, 1],
        [5, 6, 0.039,  0.17,   0.358, 150, 150, 150, 0, 0, 1],
        [3, 6, 0,      0.0586, 0,     300, 300, 300, 0, 0, 1],
        [6, 7, 0.0119, 0.1008, 0.209, 150, 150, 150, 0, 0, 1],
        [7, 8, 0.0085, 0.072,  0.149, 250, 250, 250, 0, 0, 1],
        [8, 2, 0,      0.0625, 0,     250, 250, 250, 0, 0, 1],
        [8, 9, 0.032,  0.161,  0.306, 250, 250, 250, 0, 0, 1],
        [9, 4, 0.01,   0.085,  0.176, 250, 250, 250, 0, 0, 1]
    ])

    ##-----  OPF Data  -----##
    ## area data
    # area refbus
    areas = array([
        [1, 5]
    ])

    ## generator cost data
    # 1 startup shutdown n x1 y1 ... xn yn
    # 2 startup shutdown n c(n-1) ... c0
    gencost = array([
        [2, 1500, 0, 3, 0.11,   5,   150],
        [2, 2000, 0, 3, 0.085,  1.2, 600],
        [2, 3000, 0, 3, 0.1225, 1,   335],
        [2,    0, 0, 3, 0.2,    0,     0],
        [2,    0, 0, 3, 0.05,   0,     0],
        [2,    0, 0, 3, 0.3,    0,     0],
    ])

    return baseMVA, bus, gen, branch, areas, gencost
