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

"""Builds the bus admittance matrix and branch admittance matrices.
"""

from sys import stderr

from numpy import ones, conj, nonzero, any, exp, pi, r_, arange
from scipy.sparse import spdiags, csc_matrix as sparse

from idx_bus import BUS_I, GS, BS
from idx_brch import F_BUS, T_BUS, BR_R, BR_X, BR_B, BR_STATUS, SHIFT, TAP


def makeYbus(baseMVA, bus, branch):
    """Builds the bus admittance matrix and branch admittance matrices.

    Returns the full bus admittance matrix (i.e. for all buses) and the
    matrices C{Yf} and C{Yt} which, when multiplied by a complex voltage
    vector, yield the vector currents injected into each line from the
    "from" and "to" buses respectively of each line. Does appropriate
    conversions to p.u.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## constants
    nb = bus.shape[0]          ## number of buses
    nl = branch.shape[0]       ## number of lines

    ## check that bus numbers are equal to indices to bus (one set of bus nums)
    if any(bus[:, BUS_I] != range(nb)):
        stderr.write('buses must appear in order by bus number\n')

    ## for each branch, compute the elements of the branch admittance matrix where
    ##
    ##      | If |   | Yff  Yft |   | Vf |
    ##      |    | = |          | * |    |
    ##      | It |   | Ytf  Ytt |   | Vt |
    ##
    stat = branch[:, BR_STATUS]              ## ones at in-service branches
    Ys = stat / (branch[:, BR_R] + 1j * branch[:, BR_X])  ## series admittance
    Bc = stat * branch[:, BR_B]              ## line charging susceptance
    tap = ones(nl)                           ## default tap ratio = 1
    i = nonzero(branch[:, TAP])              ## indices of non-zero tap ratios
    tap[i] = branch[i, TAP]                  ## assign non-zero tap ratios
    tap = tap * exp(1j * pi / 180 * branch[:, SHIFT]) ## add phase shifters

    Ytt = Ys + 1j * Bc / 2
    Yff = Ytt / (tap * conj(tap))
    Yft = - Ys / conj(tap)
    Ytf = - Ys / tap

    ## compute shunt admittance
    ## if Psh is the real power consumed by the shunt at V = 1.0 p.u.
    ## and Qsh is the reactive power injected by the shunt at V = 1.0 p.u.
    ## then Psh - j Qsh = V * conj(Ysh * V) = conj(Ysh) = Gs - j Bs,
    ## i.e. Ysh = Psh + j Qsh, so ...
    ## vector of shunt admittances
    Ysh = (bus[:, GS] + 1j * bus[:, BS]) / baseMVA

    ## build connection matrices
    f = branch[:, F_BUS]                           ## list of "from" buses
    t = branch[:, T_BUS]                           ## list of "to" buses
    ## connection matrix for line & from buses
    Cf = sparse((ones(nl), (f, arange(nl))), (nb, nl))
    ## connection matrix for line & to buses
    Ct = sparse((ones(nl), (t, arange(nl))), (nb, nl))

    Ybus = spdiags(Ysh, 0, nb, nb) + \
        Cf * spdiags(Yff, 0, nl, nl) * Cf.T + \
        Cf * spdiags(Yft, 0, nl, nl) * Ct.T + \
        Ct * spdiags(Ytf, 0, nl, nl) * Cf.T + \
        Ct * spdiags(Ytt, 0, nl, nl) * Ct.T

    ## build Yf and Yt such that Yf * V is the vector of complex branch currents injected
    ## at each branch's "from" bus, and Yt is the same for the "to" bus end
    i = r_[range(nl), range(nl)]                   ## double set of row indices

    Yf = sparse((r_[Yff, Yft], (i, r_[f, t])), (nl, nb))
    Yt = sparse((r_[Ytf, Ytt], (i, r_[f, t])), (nl, nb))

    return Ybus, Yf, Yt
