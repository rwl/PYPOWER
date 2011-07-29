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

"""Computes partial derivatives of branch currents w.r.t. voltage.
"""

from numpy import diag, asmatrix, asarray, arange
from scipy.sparse import issparse, csr_matrix as sparse


def dIbr_dV(branch, Yf, Yt, V):
    """Computes partial derivatives of branch currents w.r.t. voltage.

    Returns four matrices containing partial derivatives of the complex
    branch currents at "from" and "to" ends of each branch w.r.t voltage
    magnitude and voltage angle respectively (for all buses). If C{Yf} is a
    sparse matrix, the partial derivative matrices will be as well. Optionally
    returns vectors containing the currents themselves. The following
    explains the expressions used to form the matrices::

        If = Yf * V

    Partials of V, Vf & If w.r.t. voltage angles::
        dV/dVa  = j * diag(V)
        dVf/dVa = sparse(range(nl), f, j*V(f)) = j * sparse(range(nl), f, V(f))
        dIf/dVa = Yf * dV/dVa = Yf * j * diag(V)

    Partials of V, Vf & If w.r.t. voltage magnitudes::
        dV/dVm  = diag(V / abs(V))
        dVf/dVm = sparse(range(nl), f, V(f) / abs(V(f))
        dIf/dVm = Yf * dV/dVm = Yf * diag(V / abs(V))

    Derivations for "to" bus are similar.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    nb = len(V)

    Vnorm = V / abs(V)
    if issparse(Yf):             ## sparse version (if Yf is sparse)
        i = arange(nb)
        diagV       = sparse((V, (i, i)))
        diagVnorm   = sparse((Vnorm, (i, i)))
    else:                        ## dense version
        diagV       = asmatrix( diag(V) )
        diagVnorm   = asmatrix( diag(Vnorm) )

    dIf_dVa = Yf * 1j * diagV
    dIf_dVm = Yf * diagVnorm
    dIt_dVa = Yt * 1j * diagV
    dIt_dVm = Yt * diagVnorm

    ## compute currents
    if issparse(Yf):
        If = Yf * V
        It = Yt * V
    else:
        If = asarray( Yf * asmatrix(V).T ).flatten()
        It = asarray( Yt * asmatrix(V).T ).flatten()

    return dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It
