# Copyright (C) 2008-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

    @see: http://www.pserc.cornell.edu/matpower/
    @return: The 2nd derivatives of complex branch current w.r.t. voltage.
    """
    nb = len(V)
    ib = range(nb)
    diaginvVm = csr_matrix((ones(nb) / abs(V), (ib, ib)))

    Haa = csr_matrix((-(Ybr.T * lam) / V, (ib, ib)))
    Hva = -1j * Haa * diaginvVm
    Hav = Hva
    Hvv = csr_matrix((nb, nb))

    return Haa, Hav, Hva, Hvv