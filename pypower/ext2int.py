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

"""Converts external to internal indexing.
"""

from numpy import arange, zeros

from idx_bus import BUS_I
from idx_gen import GEN_BUS
from idx_brch import F_BUS, T_BUS
from idx_area import PRICE_REF_BUS


def ext2int(bus, gen, branch, areas=None):
    """Converts external to internal indexing.

    Converts from (possibly non-consecutive) external bus numbers to
    consecutive internal bus numbers which start at 1. Changes are made
    to BUS, GEN, BRANCH and optionally AREAS matrices, which are returned
    along with a vector of indices I2E that can be passed to INT2EXT to
    perform the reverse conversion.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    i2e = bus[:, BUS_I].astype(int)
    e2i = zeros(max(i2e) + 1)
    e2i[i2e] = arange(bus.shape[0])

    bus[:, BUS_I]    = e2i[ bus[:, BUS_I].astype(int)    ]
    gen[:, GEN_BUS]  = e2i[ gen[:, GEN_BUS].astype(int)  ]
    branch[:, F_BUS] = e2i[ branch[:, F_BUS].astype(int) ]
    branch[:, T_BUS] = e2i[ branch[:, T_BUS].astype(int) ]
    if areas is not None and len(areas) > 0:
        areas[:, PRICE_REF_BUS] = e2i[ areas[:, PRICE_REF_BUS].astype(int) ]

        return i2e, bus, gen, branch, areas
    else:
        return i2e, bus, gen, branch
