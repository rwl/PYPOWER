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

"""Partial derivatives of apparent power flows w.r.t voltage.
"""

from numpy import ones, diag, flatnonzero as find

from scipy.sparse import issparse, spdiags


def dAbr_dV(dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St):
    """Partial derivatives of apparent power flows w.r.t voltage.

    Returns four matrices containing partial derivatives of apparent power
    flows at "from" & "to" ends of each branch w.r.t
    voltage magnitude and voltage angle respectively (for all buses), given
    the flows and flow sensitivities. Flows could be complex current or
    complex or real power. Notation below is based on complex power. The
    following explains the expressions used to form the matrices:

    Let Af refer to the apparent power at the "from" end of each line,
    i.e. Af = abs(Sf), then ...

    Partial w.r.t real power::
        dAf/dPf = diag(real(Sf) ./ Af)

    Partial w.r.t reactive power::
        dAf/dQf = diag(imag(Sf) ./ Af)

    Partial w.r.t Vm & Va::
        dAf/dVm = dAf/dPf * dPf/dVm + dAf/dQf * dQf/dVm
        dAf/dVa = dAf/dPf * dPf/dVa + dAf/dQf * dQf/dVa

    Derivations for "to" bus are similar.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## dimensions
    nl = len(Sf)

    ##----- compute apparent powers -----
    Af = abs(Sf)
    At = abs(St)

    ##----- partials w.r.t. real and reactive power flows -----
    ## Careful!  Need to make partial equal to 1 for lines w/ zero flow
    ##           to avoid division by zero errors (1 comes from L'Hopital)
    ## initialize to all ones
    nPf = ones(nl)
    nQf = ones(nl)
    nPt = ones(nl)
    nQt = ones(nl)
    ## use actual partials for non-zero flows
    i = find(Af)                       ## find non-zeros of "from" flows
    nPf[i] = Sf[i].real / Af[i]
    nQf[i] = Sf[i].imag / Af[i]
    i = find(At)                       ## find non-zeros of "to" flows
    nPt[i] = St[i].real / At[i]
    nQt[i] = St[i].imag / At[i]
    ## put into diagonal matrices
    if issparse(dSf_dVa):        ## sparse version (if dSf_dVa is sparse)
        dAf_dPf = spdiags(nPf, 0, nl, nl, 'csc')
        dAf_dQf = spdiags(nQf, 0, nl, nl, 'csc')
        dAt_dPt = spdiags(nPt, 0, nl, nl, 'csc')
        dAt_dQt = spdiags(nQt, 0, nl, nl, 'csc')
    else:                        ## dense version
        dAf_dPf = diag(nPf)
        dAf_dQf = diag(nQf)
        dAt_dPt = diag(nPt)
        dAt_dQt = diag(nQt)

    ## partials w.r.t. voltage magnitudes and angles
    dAf_dVm = dAf_dPf * dSf_dVm.real + dAf_dQf * dSf_dVm.imag
    dAf_dVa = dAf_dPf * dSf_dVa.real + dAf_dQf * dSf_dVa.imag
    dAt_dVm = dAt_dPt * dSt_dVm.real + dAt_dQt * dSt_dVm.imag
    dAt_dVa = dAt_dPt * dSt_dVa.real + dAt_dQt * dSt_dVa.imag

    return dAf_dVa, dAf_dVm, dAt_dVa, dAt_dVm
