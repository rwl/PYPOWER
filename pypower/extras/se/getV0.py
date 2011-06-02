# Copyright (C) 2009-2011 Rui Bo <eeborui@hotmail.com>
# Copyright (C) 2010-2011 Richard Lincoln
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