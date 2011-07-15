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

"""Power flow data for 4 bus, 2 gen case from Grainger & Stevenson.
"""

from numpy import array


def case4gs():
    """Power flow data for 4 bus, 2 gen case from Grainger & Stevenson.
    Please see L{caseformat} for details on the case file format.

    This is the 4 bus example from pp. 337-338 of I{"Power System Analysis"},
    by John Grainger, Jr., William Stevenson, McGraw-Hill, 1994.

    @return: Power flow data for 4 bus, 2 gen case from Grainger & Stevenson.
    """

    ##-----  Power Flow Data  -----##
    ## system MVA base
    baseMVA = 100.0

    ## bus data
    # bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
    bus = array([
        [0, 3, 50,  30.99,  0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [1, 1, 170, 105.35, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [2, 1, 200, 123.94, 0, 0, 1, 1, 0, 230, 1, 1.1, 0.9],
        [3, 2, 80,  49.58,  0, 0, 1, 1, 0, 230, 1, 1.1, 0.9]
    ])

    ## generator data
    # bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin
    gen = array([
        [3, 318, 0, 100, -100, 1.02, 100, 1, 318, 0],
        [0, 0,   0, 100, -100, 1,    100, 1, 0,   0]
    ])

    ## branch data
    # fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status
    branch = array([
        [0, 1, 0.01008, 0.0504, 0.1025, 250, 250, 250, 0, 0, 1],
        [0, 2, 0.00744, 0.0372, 0.0775, 250, 250, 250, 0, 0, 1],
        [1, 3, 0.00744, 0.0372, 0.0775, 250, 250, 250, 0, 0, 1],
        [2, 3, 0.01272, 0.0636, 0.1275, 250, 250, 250, 0, 0, 1]
    ])

    return baseMVA, bus, gen, branch
