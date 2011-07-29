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

"""Computes 2nd derivatives of complex branch current w.r.t. voltage.
"""

from numpy import ones, arange
from scipy.sparse import csr_matrix as sparse


def d2Ibr_dV2(Ybr, V, lam):
    """Computes 2nd derivatives of complex branch current w.r.t. voltage.

    Returns 4 matrices containing the partial derivatives w.r.t. voltage
    angle and magnitude of the product of a vector LAM with the 1st partial
    derivatives of the complex branch currents. Takes sparse branch admittance
    matrix C{Ybr}, voltage vector C{V} and C{nl x 1} vector of multipliers
    C{lam}. Output matrices are sparse.

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
    diaginvVm = sparse((ones(nb) / abs(V), (ib, ib)))

    Haa = sparse((-(Ybr.T * lam) * V, (ib, ib)))
    Hva = -1j * Haa * diaginvVm
    Hav = Hva.copy()
    Hvv = sparse((nb, nb))

    return Haa, Hav, Hva, Hvv
