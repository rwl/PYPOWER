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

from scipy.sparse import csr_matrix

def dIbr_dV(branch, Yf, Yt, V):
    """Computes partial derivatives of branch currents w.r.t. voltage.

    Returns four matrices containing partial derivatives of the complex
    branch currents at "from" and "to" ends of each branch w.r.t voltage
    magnitude and voltage angle respectively (for all buses). If YF is a
    sparse matrix, the partial derivative matrices will be as well. Optionally
    returns vectors containing the currents themselves. The following
    explains the expressions used to form the matrices:

    If = Yf * V

    Partials of V, Vf & If w.r.t. voltage angles
        dV/dVa  = j * diag(V)
        dVf/dVa = sparse(1:nl, f, j * V(f)) = j * sparse(1:nl, f, V(f))
        dIf/dVa = Yf * dV/dVa = Yf * j * diag(V)

    Partials of V, Vf & If w.r.t. voltage magnitudes
        dV/dVm  = diag(V./abs(V))
        dVf/dVm = sparse(1:nl, f, V(f)./abs(V(f))
        dIf/dVm = Yf * dV/dVm = Yf * diag(V./abs(V))

    Derivations for "to" bus are similar.

    @return: The partial derivatives of branch currents w.r.t. voltage
             magnitude and voltage angle.
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    i = range(len(V))

    Vnorm = V / abs(V)
    diagV = csr_matrix((V, (i, i)))
    diagVnorm = csr_matrix((Vnorm, (i, i)))
    dIf_dVa = Yf * 1j * diagV
    dIf_dVm = Yf * diagVnorm
    dIt_dVa = Yt * 1j * diagV
    dIt_dVm = Yt * diagVnorm

    # Compute currents.
    If = Yf * V
    It = Yt * V

    return dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It
