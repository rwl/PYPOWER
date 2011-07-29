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

"""Power flow data for 6 bus, 3 gen case from Wood & Wollenberg.
"""

from numpy import array

def case6ww():
    """Power flow data for 6 bus, 3 gen case from Wood & Wollenberg.
    Please see L{caseformat} for details on the case file format.

    This is the 6 bus example from pp. 104, 112, 119, 123-124, 549 of
    I{"Power Generation, Operation, and Control, 2nd Edition"},
    by Allen. J. Wood and Bruce F. Wollenberg, John Wiley & Sons, NY, Jan 1996.

    @return: Power flow data for 6 bus, 3 gen case from Wood & Wollenberg.
    """
    ppc = {"version": '2'}

    ##-----  Power Flow Data  -----##
    ## system MVA base
    ppc["baseMVA"] = 100.0

    ## bus data
    # bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
    ppc["bus"] = array([
        [1, 3,  0,  0, 0, 0, 1, 1.05, 0, 230, 1, 1.05, 1.05],
        [2, 2,  0,  0, 0, 0, 1, 1.05, 0, 230, 1, 1.05, 1.05],
        [3, 2,  0,  0, 0, 0, 1, 1.07, 0, 230, 1, 1.07, 1.07],
        [4, 1, 70, 70, 0, 0, 1, 1,    0, 230, 1, 1.05, 0.95],
        [5, 1, 70, 70, 0, 0, 1, 1,    0, 230, 1, 1.05, 0.95],
        [6, 1, 70, 70, 0, 0, 1, 1,    0, 230, 1, 1.05, 0.95]
    ])

    ## generator data
    # bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin, Pc1, Pc2,
    # Qc1min, Qc1max, Qc2min, Qc2max, ramp_agc, ramp_10, ramp_30, ramp_q, apf
    ppc["gen"] = array([
        [1, 0,  0, 100, -100, 1.05, 100, 1, 200, 50,   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 50, 0, 100, -100, 1.05, 100, 1, 150, 37.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 60, 0, 100, -100, 1.07, 100, 1, 180, 45,   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])

    ## branch data
    # fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax
    ppc["branch"] = array([
        [1, 2, 0.1,  0.2,  0.04, 40, 40, 40, 0, 0, 1, -360, 360],
        [1, 4, 0.05, 0.2,  0.04, 60, 60, 60, 0, 0, 1, -360, 360],
        [1, 5, 0.08, 0.3,  0.06, 40, 40, 40, 0, 0, 1, -360, 360],
        [2, 3, 0.05, 0.25, 0.06, 40, 40, 40, 0, 0, 1, -360, 360],
        [2, 4, 0.05, 0.1,  0.02, 60, 60, 60, 0, 0, 1, -360, 360],
        [2, 5, 0.1,  0.3,  0.04, 30, 30, 30, 0, 0, 1, -360, 360],
        [2, 6, 0.07, 0.2,  0.05, 90, 90, 90, 0, 0, 1, -360, 360],
        [3, 5, 0.12, 0.26, 0.05, 70, 70, 70, 0, 0, 1, -360, 360],
        [3, 6, 0.02, 0.1,  0.02, 80, 80, 80, 0, 0, 1, -360, 360],
        [4, 5, 0.2,  0.4,  0.08, 20, 20, 20, 0, 0, 1, -360, 360],
        [5, 6, 0.1,  0.3,  0.06, 40, 40, 40, 0, 0, 1, -360, 360]
    ])

    ##-----  OPF Data  -----##
    ## generator cost data
    # 1 startup shutdown n x1 y1 ... xn yn
    # 2 startup shutdown n c(n-1) ... c0
    ppc["gencost"] = array([
        [2, 0, 0, 3, 0.00533, 11.669, 213.1],
        [2, 0, 0, 3, 0.00889, 10.333, 200],
        [2, 0, 0, 3, 0.00741, 10.833, 240]
    ])

    return ppc
