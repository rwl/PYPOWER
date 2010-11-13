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

def d2Sbr_dV2(Cbr, Ybr, V, lam):
    """Computes 2nd derivatives of complex power flow w.r.t. voltage.

    Returns 4 matrices containing the partial derivatives w.r.t. voltage angle
    and magnitude of the product of a vector LAM with the 1st partial
    derivatives of the complex branch power flows. Takes sparse connection
    matrix CBR, sparse branch admittance matrix YBR, voltage vector V and
    nl x 1 vector of multipliers LAM. Output matrices are sparse.

    @return: The 2nd derivatives of complex power flow w.r.t. voltage.
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    nb = len(V)
    nl = len(lam)
    ib = range(nb)
    il = range(nl)

    diaglam = csr_matrix((lam, (il, il)))
    diagV = csr_matrix((V, (ib, ib)))

    A = Ybr.H * diaglam * Cbr
    B = conj(diagV) * A * diagV
    D = csr_matrix( ((A * V) * conj(V), (ib, ib)) )
    E = csr_matrix( ((A.T * conj(V) * V), (ib, ib)) )
    F = B + B.T
    G = csr_matrix((ones(nb) / abs(V), (ib, ib)))

    Haa = F - D - E
    Hva = 1j * G * (B - B.T - D + E)
    Hav = Hva.T
    Hvv = G * F * G

    return Haa, Hav, Hva, Hvv
