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

"""Builds the FDPF matrices, B prime and B double prime.
"""

from numpy import ones, zeros, copy

from idx_bus import BS
from idx_brch import BR_B, BR_R, TAP, SHIFT

from makeYbus import makeYbus


def makeB(baseMVA, bus, branch, alg):
    """Builds the FDPF matrices, B prime and B double prime.

    Returns the two matrices B prime and B double prime used in the fast
    decoupled power flow. Does appropriate conversions to p.u. C{alg} is the
    value of the C{PF_ALG} option specifying the power flow algorithm.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## constants
    nb = bus.shape[0]          ## number of buses
    nl = branch.shape[0]       ## number of lines

    ##-----  form Bp (B prime)  -----
    temp_branch = copy(branch)                 ## modify a copy of branch
    temp_bus = copy(bus)                       ## modify a copy of bus
    temp_bus[:, BS] = zeros(nb)                ## zero out shunts at buses
    temp_branch[:, BR_B] = zeros(nl)           ## zero out line charging shunts
    temp_branch[:, TAP] = ones(nl)             ## cancel out taps
    if alg == 2:                               ## if XB method
        temp_branch[:, BR_R] = zeros(nl)       ## zero out line resistance
    Bp = -1 * makeYbus(baseMVA, temp_bus, temp_branch)[0].imag

    ##-----  form Bpp (B double prime)  -----
    temp_branch = copy(branch)                 ## modify a copy of branch
    temp_branch[:, SHIFT] = zeros(nl)          ## zero out phase shifters
    if alg == 3:                               ## if BX method
        temp_branch[:, BR_R] = zeros(nl)    ## zero out line resistance
    Bpp = -1 * makeYbus(baseMVA, bus, temp_branch)[0].imag

    return Bp, Bpp
