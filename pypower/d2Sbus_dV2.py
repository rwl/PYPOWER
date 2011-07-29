# Copyright (C) 2008-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
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

"""Computes 2nd derivatives of power injection w.r.t. voltage.
"""

from numpy import ones, conj, arange
from scipy.sparse import csr_matrix as sparse


def d2Sbus_dV2(Ybus, V, lam):
    """Computes 2nd derivatives of power injection w.r.t. voltage.

    Returns 4 matrices containing the partial derivatives w.r.t. voltage angle
    and magnitude of the product of a vector C{lam} with the 1st partial
    derivatives of the complex bus power injections. Takes sparse bus
    admittance matrix C{Ybus}, voltage vector C{V} and C{nb x 1} vector of
    multipliers C{lam}. Output matrices are sparse.

    For more details on the derivations behind the derivative code used
    in PYPOWER information, see:

    [TN2]  R. D. Zimmerman, I{"AC Power Flows, Generalized OPF Costs and
    their Derivatives using Complex Matrix Notation"}, MATPOWER
    Technical Note 2, February 2010.
    U{http://www.pserc.cornell.edu/matpower/TN2-OPF-Derivatives.pdf}

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    nb = len(V)
    ib = arange(nb)
    Ibus = Ybus * V
    diaglam = sparse((lam, (ib, ib)))
    diagV = sparse((V, (ib, ib)))

    A = sparse((lam * V, (ib, ib)))
    B = Ybus * diagV
    C = A * conj(B)
    D = Ybus.H * diagV
    E = diagV.conj() * (D * diaglam - sparse((D * lam, (ib, ib))))
    F = C - A * sparse((conj(Ibus), (ib, ib)))
    G = sparse((ones(nb) / abs(V), (ib, ib)))

    Gaa = E + F
    Gva = 1j * G * (E - F)
    Gav = Gva.T
    Gvv = G * (C + C.T) * G

    return Gaa, Gav, Gva, Gvv
