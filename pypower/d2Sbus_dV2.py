# Copyright (C) 2008-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

from numpy import ones, conj
from scipy.sparse import csr_matrix

def d2Sbus_dV2(Ybus, V, lam):
    """Computes 2nd derivatives of power injection w.r.t. voltage.

    Returns 4 matrices containing the partial derivatives w.r.t. voltage angle
    and magnitude of the product of a vector LAM with the 1st partial
    derivatives of the complex bus power injections. Takes sparse bus
    admittance matrix C{Ybus}, voltage vector C{V} and C{nb} x 1 vector of
    multipliers C{lam}. Output matrices are sparse.

    @return: The 2nd derivatives of power injection w.r.t. voltage.
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    nb = len(V)
    ib = range(nb)
    Ibus = Ybus * V
    diaglam = csr_matrix((lam, (ib, ib)))
    diagV = csr_matrix((V, (ib, ib)))

    A = csr_matrix((lam * V, (ib, ib)))
    B = Ybus * diagV
    C = A * conj(B)
    D = Ybus.H * diagV
    E = diagV.conj() * (D * diaglam - csr_matrix((D * lam, (ib, ib))))
    F = C - A * csr_matrix((conj(Ibus), (ib, ib)))
    G = csr_matrix((ones(nb) / abs(V), (ib, ib)))

    Gaa = E + F
    Gva = 1j * G * (E - F)
    Gav = Gva.T
    Gvv = G * (C + C.T) * G

    return Gaa, Gav, Gva, Gvv
