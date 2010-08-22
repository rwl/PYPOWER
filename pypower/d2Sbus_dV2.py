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
