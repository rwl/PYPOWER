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

from numpy import ones, exp, pi
from numpy import flatnonzero as find

from pypower.idx_bus import VM, VA
from pypower.idx_gen import GEN_BUS, GEN_STATUS, VG

def getV0(bus, gen, type_initialguess, V0):
    """Get initial voltage profile for power flow calculation.

    Note: The pv bus voltage will remain at the given value even for
    flat start.

    @param type_initialguess: 1 - initial guess from case data
                              2 - flat start
                              3 - from input

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """

    ## generator info
    on = find(gen[:, GEN_STATUS] > 0)      ## which generators are on?
    gbus = gen[on, GEN_BUS]                ## what buses are they at?
    if type_initialguess == 1:  # using previous value in case data
        # NOTE: angle is in degree in case data, but in radians in pf solver,
        # so conversion from degree to radians is needed here
        V0  = bus[:, VM] * exp(1j * pi/180 * bus[:, VA])
    elif type_initialguess == 2:  # using flat start
        V0 = ones(bus.shape[0])
    elif type_initialguess == 3:  # using given initial voltage
        V0 = V0
    else:
        raise ValueError, "Error: unknow 'type_initialguess.\n"

    # set the voltages of PV bus and reference bus into the initial guess
    V0[gbus] = gen[on, VG] / abs(V0[gbus]) * V0[gbus]

    return V0