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

from numpy import ones
from scipy.sparse import csr_matrix

def d2Ibr_dV2(Ybr, V, lam):
    """Computes 2nd derivatives of complex branch current w.r.t. voltage.
    [HAA, HAV, HVA, HVV] = D2IBR_DV2(CBR, YBR, V, LAM) returns 4 matrices
    containing the partial derivatives w.r.t. voltage angle and magnitude
    of the product of a vector LAM with the 1st partial derivatives of the
    complex branch currents. Takes sparse branch admittance matrix YBR,
    voltage vector V and nl x 1 vector of multipliers LAM. Output matrices
    are sparse.

    @return: The 2nd derivatives of complex branch current w.r.t. voltage.
    @see: http://www.pserc.cornell.edu/matpower/
    """
    nb = len(V)
    ib = range(nb)
    diaginvVm = csr_matrix((ones(nb) / abs(V), (ib, ib)))

    Haa = csr_matrix((-(Ybr.T * lam) / V, (ib, ib)))
    Hva = -1j * Haa * diaginvVm
    Hav = Hva
    Hvv = csr_matrix((nb, nb))

    return Haa, Hav, Hva, Hvv