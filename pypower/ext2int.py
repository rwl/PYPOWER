# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2009-2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

""" Converts external to internal bus numbering.

@see: U{http://www.pserc.cornell.edu/matpower/}
"""

from numpy import array

from idx_bus import BUS_I
from idx_gen import GEN_BUS
from idx_brch import F_BUS, T_BUS
from idx_area import PRICE_REF_BUS

def ext2int(bus, gen, branch, areas):
    """ Converts external to internal bus numbering.

    Converts external bus numbers (possibly non-consecutive) to consecutive
    internal bus numbers which start at 1.
    """
    i2e = bus[:, BUS_I]
    e2i = array(0.0, (max(i2e), 1))
    e2i[i2e] = array(range(1, bus.size[0])).T

    bus[:, BUS_I]    = e2i[bus[:, BUS_I]]
    gen[:, GEN_BUS]  = e2i[gen[:, GEN_BUS]]
    branch[:, F_BUS] = e2i[branch[:, F_BUS]]
    branch[:, T_BUS] = e2i[branch[:, T_BUS]]

    areas[:, PRICE_REF_BUS] = e2i[areas[:, PRICE_REF_BUS]]
