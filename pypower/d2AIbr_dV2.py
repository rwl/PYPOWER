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

from scipy.sparse import csr_matrix

from d2Ibr_dV2 import d2Ibr_dV2

def d2AIbr_dV2(dIbr_dVa, dIbr_dVm, Ibr, Ybr, V, lam):
    """Computes 2nd derivatives of |complex current|^2 w.r.t. V.

    Returns 4 matrices containing the partial derivatives w.r.t. voltage
    angle and magnitude of the product of a vector LAM with the 1st partial
    derivatives of the square of the magnitude of the branch currents.
    Takes sparse first derivative matrices of complex flow, complex flow
    vector, sparse branch admittance matrix YBR, voltage vector V and
    nl x 1 vector of multipliers LAM. Output matrices are sparse.

    @see: L{dIbr_dV}.
    @see: U{http://www.pserc.cornell.edu/matpower/}
    @return: The 2nd derivatives of |complex current|**2 w.r.t. V.
    """
    # define
    il = range(len(lam))

    diaglam = csr_matrix((lam, (il, il)))
    diagIbr_conj = csr_matrix((Ibr.conj(), (il, il)))

    Iaa, Iav, Iva, Ivv = d2Ibr_dV2(Ybr, V, diagIbr_conj * lam)

    Haa = 2 * ( Iaa + dIbr_dVa.T * diaglam * dIbr_dVa.conj() ).real
    Hva = 2 * ( Iva + dIbr_dVm.T * diaglam * dIbr_dVa.conj() ).real
    Hav = 2 * ( Iav + dIbr_dVa.T * diaglam * dIbr_dVm.conj() ).real
    Hvv = 2 * ( Ivv + dIbr_dVm.T * diaglam * dIbr_dVm.conj() ).real

    return Haa, Hav, Hva, Hvv
