# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

from numpy import array

def case3bus_P6_6():
    """Case of 3 bus system.
    From Problem 6.6 in book 'Computational
    Methods for Electric Power Systems' by Mariesa Crow

    @author: Rui Bo
    @author: Richard Lincoln
    """
    ppc = {}
    ##-----  Power Flow Data  -----##
    ## system MVA base
    ppc["baseMVA"] = 1000.0;

    ## bus data
    #, bus_i, type, Pd, Qd, Gs, Bs, area, Vm, Va, baseKV, zone, Vmax, Vmin
    ppc["bus"] = array([
        [1, 3, 350, 100, 0, 0, 1, 1, 0, 230, 1, 1.00, 1.00],
        [2, 2, 400, 250, 0, 0, 1, 1, 0, 230, 1, 1.02, 1.02]
        [3, 2, 250, 100, 0, 0, 1, 1, 0, 230, 1, 1.02, 1.02]
    ])

    ## generator data
    # Note:
    # 1)It's better of gen to be in number order, otherwise gen and genbid
    # should be sorted to make the lp solution output clearly(in number order as well)
    # 2)set Pmax to nonzero. set to 999 if no limit
    # 3)If change the order of gen, then must change the order in genbid
    # accordingly
    #, bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin
    ppc["gen"] = array([
        [1, 182.18, 0, 999, -999, 1.00, 100, 1, 600, 0],
        [2, 272.77, 0, 999, -999, 1.02, 100, 1, 400, 0],
        [3, 545.05, 0, 999, -999, 1.02, 100, 1, 100, 0]
    ])
    #gen(:, 9) = 999; # inactive the Pmax constraints

    ## branch data
    #, fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status
    ppc["branch"] = array([
        [1, 2, 0.01, 0.1, 0.050, 999, 100, 100, 0, 0, 1],
        [1, 3, 0.05, 0.1, 0.025, 999, 100, 100, 0, 0, 1],
        [2, 3, 0.05, 0.1, 0.025, 999, 100, 100, 0, 0, 1]
    ])

    ##-----  OPF Data  -----##
    ## area data
    ppc["areas"] = array([
        [1, 1]
    ])

    ## generator cost data
    #, 2, startup, shutdown, n, c(n-1), ..., c0
    ppc["gencost"] = array([
        [2, 0, 0, 3, 1.5, 1, 0],
        [2, 0, 0, 3, 1  , 2, 0],
        [2, 0, 0, 3, 0.5, 2.5, 0]
    ])

    return ppc