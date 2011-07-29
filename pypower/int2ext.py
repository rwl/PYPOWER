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

"""Converts internal to external bus numbering.
"""

from idx_bus import BUS_I
from idx_gen import GEN_BUS
from idx_brch import F_BUS, T_BUS
from idx_area import PRICE_REF_BUS


def int2ext(i2e, bus, gen, branch, areas=None):
    """Converts from the consecutive internal bus numbers back to the originals
    using the mapping provided by the C{i2e} vector returned from C{ext2int}.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    bus[:, BUS_I]    = i2e[ bus[:, BUS_I].astype(int) ]
    gen[:, GEN_BUS]  = i2e[ gen[:, GEN_BUS].astype(int) ]
    branch[:, F_BUS] = i2e[ branch[:, F_BUS].astype(int) ]
    branch[:, T_BUS] = i2e[ branch[:, T_BUS].astype(int) ]

    if areas != None and len(areas) > 0:
        areas[:, PRICE_REF_BUS] = i2e[ areas[:, PRICE_REF_BUS].astype(int) ]
        return bus, gen, branch, areas
    else:
        return bus, gen, branch
