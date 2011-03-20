# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
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

def dSbus_dV(Ybus, V):
    """Computes partial derivatives of power injection w.r.t. voltage.

    Returns two matrices containing partial derivatives of the complex bus
    power injections w.r.t voltage magnitude and voltage angle respectively
    (for all buses). If YBUS is a sparse matrix, the return values will be
    also. The following explains the expressions used to form the matrices:

    S = diag(V) * conj(Ibus) = diag(conj(Ibus)) * V

    Partials of V & Ibus w.r.t. voltage magnitudes
        dV/dVm = diag(V./abs(V))
        dI/dVm = Ybus * dV/dVm = Ybus * diag(V./abs(V))

    Partials of V & Ibus w.r.t. voltage angles
        dV/dVa = j * diag(V)
        dI/dVa = Ybus * dV/dVa = Ybus * j * diag(V)

    Partials of S w.r.t. voltage magnitudes
        dS/dVm = diag(V) * conj(dI/dVm) + diag(conj(Ibus)) * dV/dVm
               = diag(V) * conj(Ybus * diag(V./abs(V)))
                                        + conj(diag(Ibus)) * diag(V./abs(V))

    Partials of S w.r.t. voltage angles
        dS/dVa = diag(V) * conj(dI/dVa) + diag(conj(Ibus)) * dV/dVa
               = diag(V) * conj(Ybus * j * diag(V))
                                        + conj(diag(Ibus)) * j * diag(V)
               = -j * diag(V) * conj(Ybus * diag(V))
                                        + conj(diag(Ibus)) * j * diag(V)
               = j * diag(V) * conj(diag(Ibus) - Ybus * diag(V))

    @see: U{http://www.pserc.cornell.edu/matpower/}
    @return: The partial derivatives of power injection w.r.t. voltage
             magnitude and voltage angle.
    """
    ib = range(len(V))
    I = Ybus * V

    diagV = csr_matrix((V, (ib, ib)))
    diagIbus = csr_matrix((I, (ib, ib)))
    diagVnorm = csr_matrix((V / abs(V), (ib, ib)))

    dS_dVm = diagV * conj(Ybus * diagVnorm) + conj(diagIbus) * diagVnorm
    dS_dVa = 1j * diagV * conj(diagIbus - Ybus * diagV)

    return dS_dVm, dS_dVa
