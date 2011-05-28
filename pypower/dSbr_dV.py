# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

from numpy import conj
from scipy.sparse import csr_matrix

from idx_brch import F_BUS, T_BUS

def dSbr_dV(branch, Yf, Yt, V):
    """Computes partial derivatives of power flows w.r.t. voltage.

    returns four matrices containing partial derivatives of the complex
    branch power flows at "from" and "to" ends of each branch w.r.t voltage
    magnitude and voltage angle respectively (for all buses). If YF is a
    sparse matrix, the partial derivative matrices will be as well. Optionally
    returns vectors containing the power flows themselves. The following
    explains the expressions used to form the matrices:

    If = Yf * V;
    Sf = diag(Vf) * conj(If) = diag(conj(If)) * Vf

    Partials of V, Vf & If w.r.t. voltage angles
        dV/dVa  = j * diag(V)
        dVf/dVa = sparse(1:nl, f, j * V(f)) = j * sparse(1:nl, f, V(f))
        dIf/dVa = Yf * dV/dVa = Yf * j * diag(V)

    Partials of V, Vf & If w.r.t. voltage magnitudes
        dV/dVm  = diag(V./abs(V))
        dVf/dVm = sparse(1:nl, f, V(f)./abs(V(f))
        dIf/dVm = Yf * dV/dVm = Yf * diag(V./abs(V))

    Partials of Sf w.r.t. voltage angles
        dSf/dVa = diag(Vf) * conj(dIf/dVa)
                        + diag(conj(If)) * dVf/dVa
                = diag(Vf) * conj(Yf * j * diag(V))
                        + conj(diag(If)) * j * sparse(1:nl, f, V(f))
                = -j * diag(Vf) * conj(Yf * diag(V))
                        + j * conj(diag(If)) * sparse(1:nl, f, V(f))
                = j * (conj(diag(If)) * sparse(1:nl, f, V(f))
                        - diag(Vf) * conj(Yf * diag(V)))

    Partials of Sf w.r.t. voltage magnitudes
        dSf/dVm = diag(Vf) * conj(dIf/dVm)
                        + diag(conj(If)) * dVf/dVm
                = diag(Vf) * conj(Yf * diag(V./abs(V)))
                        + conj(diag(If)) * sparse(1:nl, f, V(f)./abs(V(f)))

    Derivations for "to" bus are similar.

    For more details on the derivations behind the derivative code used
    in PYPOWER information, see:

    [TN2]  R. D. Zimmerman, "AC Power Flows, Generalized OPF Costs and
           their Derivatives using Complex Matrix Notation", MATPOWER
           Technical Note 2, February 2010.
              http://www.pserc.cornell.edu/matpower/TN2-OPF-Derivatives.pdf

    @return: The branch power flow vectors and the partial derivatives of
             branch power flow w.r.t voltage magnitude and voltage angle.
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## define
    f = branch[:, F_BUS]       ## list of "from" buses
    t = branch[:, T_BUS]       ## list of "to" buses
    nl = len(f)
    nb = len(V)
    il = range(nl)
    ib = range(nb)

    ## compute currents
    If = Yf * V
    It = Yt * V

    Vnorm = V / abs(V)
    diagVf = csr_matrix((V[f], (il, il)))
    diagIf = csr_matrix((If, (il, il)))
    diagVt = csr_matrix((V[t], (il, il)))
    diagIt = csr_matrix((It, (il, il)))
    diagV  = csr_matrix((V, (ib, ib)))
    diagVnorm = csr_matrix((Vnorm, (ib, ib)))

    shape = (nl, nb)
    # Partial derivative of S w.r.t voltage phase angle.
    dSf_dVa = 1j * (conj(diagIf) *
        csr_matrix((V[f], (il, f)), shape) - diagVf * conj(Yf * diagV))

    dSt_dVa = 1j * (conj(diagIt) *
        csr_matrix((V[t], (il, t)), shape) - diagVt * conj(Yt * diagV))

    # Partial derivative of S w.r.t. voltage amplitude.
    dSf_dVm = diagVf * conj(Yf * diagVnorm) + conj(diagIf) * \
        csr_matrix((Vnorm[f], (il, f)), shape)

    dSt_dVm = diagVt * conj(Yt * diagVnorm) + conj(diagIt) * \
        csr_matrix((Vnorm[t], (il, t)), shape)

    # Compute power flow vectors.
    Sf = V[f] * conj(If)
    St = V[t] * conj(It)

    return dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St
