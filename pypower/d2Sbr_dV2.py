# Copyright (C) 2008-2010 Power System Engineering Research Center
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
