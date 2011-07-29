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

from numpy import array, pi, r_, exp, angle
from numpy import flatnonzero as find

from pypower.pqcost import pqcost
from pypower.makeSbus import makeSbus
from pypower.ppoption import ppoption
from pypower.newtonpf import newtonpf
from pypower.pfsoln import pfsoln
from pypower.opf_form import opf_form
from pypower.totcost import totcost

from pypower.idx_bus import VM, VA
from pypower.idx_gen import GEN_STATUS, PG, QG


def LPeqslvr(x, baseMVA, bus, gen, gencost, branch, Ybus, Yf, Yt, V,
             ref, pv, pq, ppopt):
    """
    @author: Deqiang (David) Gan (PSERC Cornell & Zhejiang University)
    @author: Richard Lincoln
    """
    ## options
    alg     = ppopt['OPF_ALG_POLY']
    verbose = ppopt['VERBOSE']

    ## generator info
    on = find(gen[:, GEN_STATUS] > 0)      ## which generators are on?

    ## set up constants
    nb = bus.shape[0]
    nl = branch.shape[0]
    npv     = len(pv)
    npq     = len(pq)
    ng      = len(on)                   ## number of generators that are turned on
    pvpq    = r_[pv, pq]

    ## check for costs for Qg
    pcost, qcost = pqcost(gencost, gen.shape[0], on)

    # parse x, update bus, gen
    bus[pvpq, VA] = x[:nb - 1] * 180 / pi
    bus[:, VM] = x[nb - 1:nb + nb - 1]
    gen[on, PG] = x[2 * nb - 1 : 2 * nb - 1 + ng] * baseMVA
    gen[on, QG] = x[2 * nb + ng - 1 : 2 * nb - 1 + 2 * ng] * baseMVA


    # run load flow
    V = bus[:, VM] * exp(1j * pi/180 * bus[:, VA])

    success = 1
    Sbus = makeSbus(baseMVA, bus, gen)                                         ## build Sg-Sl

    ## turn down verbosity one level for call to power flow
    if verbose:
        ppopt = ppoption(ppopt, VERBOSE=verbose - 1)

    V, converged, iterations = newtonpf(Ybus, Sbus, V, ref, pv, pq, ppopt)   ## do NR iteration
    if converged == 0:
        success = 0
    bus, gen, branch = pfsoln(baseMVA, bus, gen, branch, Ybus, Yf, Yt, V, ref, pv, pq)   ## post-processing
    et = 1
    # printpf(baseMVA, bus, gen, branch, array([]), success, et, 1, ppopt)

    Pg = gen[on, PG] / baseMVA
    Qg = gen[on, QG] / baseMVA

    ## set up x
    if opf_form(alg) == 1:
        Cp = array([])
        Cq = array([])
    else:
        Cp = totcost(pcost, Pg * baseMVA)
        if len(qcost > 0):
            Cq = totcost(qcost, Qg * baseMVA)
        else:
            Cq = array([])  ## empty if qcost is empty

    x = r_[angle(V[pvpq]), abs(V), Pg, Qg, Cp, Cq]

    return x, success
