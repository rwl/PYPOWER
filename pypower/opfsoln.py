# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

"""Updates bus, gen, branch data structures to match opf soln.
"""

from numpy import angle, pi, conj, zeros, c_, ix_
from numpy import flatnonzero as find

from idx_bus import VM, VA, LAM_P, LAM_Q, MU_VMIN, MU_VMAX

from idx_gen import \
    GEN_BUS, GEN_STATUS, PG, QG, MU_PMIN, MU_PMAX, MU_QMIN, MU_QMAX, VG

from idx_brch import F_BUS, T_BUS, BR_STATUS, PF, PT, QF, QT, MU_SF, MU_ST


def opfsoln(baseMVA, bus0, gen0, branch0,
            Ybus, Yf, Yt, V, Sg, lmbda, ref, pv, pq, mpopt):
    """Updates bus, gen, branch data structures to match opf soln.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## initialize return values
    bus     = bus0.copy()
    gen     = gen0.copy()
    branch  = branch0.copy()

    ##----- update bus voltages -----
    bus[:, VM] = abs(V)
    bus[:, VA] = angle(V) * 180 / pi

    ##----- update Pg and Qg for all gens -----
    ## generator info
    on = find(gen[:, GEN_STATUS] > 0)      ## which generators are on?
    gbus = gen[on, GEN_BUS]                ## what buses are they at?

    ## copy back Pg & Vg
    gen[:, PG] = zeros(gen.shape[0])
    gen[on, PG] = Sg.real * baseMVA
    gen[on, VG] = bus[gbus, VM]

    ## compute Qg if not passed in with Sg
    if not any(Sg.imag):
        ## This is slow in Matlab 5 ...
        Sg = V[gbus] * conj(Ybus[gbus, :] * V)
    else:
        Qg = Sg.imag

    ## update Qg for all generators
    gen[:, QG] = zeros(gen.shape[0])        ## zero out all Qg
    gen[on, QG] = Qg * baseMVA              ## except for on-line generators

    ##----- update/compute branch power flows -----
    out = find(branch[:, BR_STATUS] == 0)      ## out-of-service branches
    br = find(branch[:, BR_STATUS])            ## in-service branches
    Sf = V[branch[br, F_BUS].astype(int)] * conj(Yf[br, :] * V) * baseMVA  ## complex power at "from" bus
    St = V[branch[br, T_BUS].astype(int)] * conj(Yt[br, :] * V) * baseMVA  ## complex power injected at "to" bus
    branch[ix_(br, [PF, QF, PT, QT])] = c_[Sf.real, Sf.imag, St.real, St.imag]
    branch[ix_(out, [PF, QF, PT, QT])] = zeros((len(out), 4))

    ##----- update lambda's and mu's -----
    ## sizes of things
    nb = bus.shape[0]
    nl = branch.shape[0]
    npv = len(pv)
    npq = len(pq)
    ng = len(on)                        ## number of generators that are turned on
    nbr = len(br)                       ## number of branches in service

    ## initialize with all zeros
    bus[:, [LAM_P, LAM_Q, MU_VMIN, MU_VMAX]] = zeros((nb, 4))
    gen[:, [MU_PMIN, MU_PMAX, MU_QMIN, MU_QMAX]] = zeros((gen.shape[0], 4))
    branch[:, [MU_SF, MU_ST]] = zeros((nl, 2))

    ## set up indexing for lambda
    i1 = 0;         i2 = nb        ## i1:i2 - P mismatch, all buses
    i3 = i2;    i4 = i2 + nb       ## i3:i4 - Q mismatch, all buses
    i5 = i4;    i6 = i4 + nb       ## i5:i6 - Vmin, all buses
    i7 = i6;    i8 = i6 + nb       ## i7:i8 - Vmax, all buses
    i9 = i8;    i10 = i8 + ng      ## i9:i10 - Pmin, gen buses
    i11 = i10;  i12 = i10 + ng     ## i11:i12 - Pmax, gen buses
    i13 = i12;  i14 = i12 + ng     ## i13:i14 - Qmin, gen buses
    i15 = i14;  i16 = i14 + ng     ## i15:i16 - Qmax, gen buses
    i17 = i16;  i18 = i16 + nbr    ## i17:i18 - |Sf| line limit
    i19 = i18;  i20 = i18 + nbr    ## i19:i20 - |St| line limit

    ## copy multipiers to bus, gen, branch
    bus[:, LAM_P]       = lmbda[i1:i2] / baseMVA
    bus[:, LAM_Q]       = lmbda[i3:i4] / baseMVA
    bus[:, MU_VMIN]     = lmbda[i5:i6]
    bus[:, MU_VMAX]     = lmbda[i7:i8]

    gen[on, MU_PMIN]    = lmbda[i9:i10] / baseMVA
    gen[on, MU_PMAX]    = lmbda[i11:i12] / baseMVA
    gen[on, MU_QMIN]    = lmbda[i13:i14] / baseMVA
    gen[on, MU_QMAX]    = lmbda[i15:i16] / baseMVA

    branch[br, MU_SF]   = lmbda[i17:i18] / baseMVA
    branch[br, MU_ST]   = lmbda[i19:i20] / baseMVA

    return bus, gen, branch
