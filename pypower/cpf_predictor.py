'''Performs the predictor step for the continuation power flow
'''

from numpy import r_, array, angle, zeros, linalg, exp

from scipy.sparse import hstack, vstack

from pypower.dSbus_dV import dSbus_dV
from pypower.cpf_p_jac import cpf_p_jac
from pypower.pplinsolve import pplinsolve


def cpf_predictor(V, lam, Ybus, Sxfr, pv, pq,
                  step, z, Vprv, lamprv, parameterization):
    # sizes
    pvpq = r_[pv, pq]
    nb = len(V)
    npv = len(pv)
    npq = len(pq)

    # compute Jacobian for the power flow equations
    dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)

    j11 = dSbus_dVa[array([pvpq]).T, pvpq].real
    j12 = dSbus_dVm[array([pvpq]).T, pq].real
    j21 = dSbus_dVa[array([pq]).T, pvpq].imag
    j22 = dSbus_dVm[array([pq]).T, pq].imag

    J = vstack([
        hstack([j11, j12]),
        hstack([j21, j22])
    ], format="csr")

    dF_dlam = -r_[Sxfr[pvpq].real, Sxfr[pq].imag].reshape((-1,1))
    dP_dV, dP_dlam = cpf_p_jac(parameterization, z, V, lam, Vprv, lamprv, pv, pq)

    # linear operator for computing the tangent predictor
    J = vstack([
        hstack([J, dF_dlam]),
        hstack([dP_dV, dP_dlam])
    ], format="csr")

    Vaprv = angle(V)
    Vmprv = abs(V)

    # compute normalized tangent predictor
    s = zeros(npv+2*npq+1)
    s[-1] = 1
    z[r_[pvpq, nb+pq, 2*nb]] = pplinsolve(J, s)
    z = z / linalg.norm(z)

    Va0 = Vaprv
    Vm0 = Vmprv
    lam0 = lam

    # prediction for next step
    Va0[pvpq] = Vaprv[pvpq] + step * z[pvpq]
    Vm0[pq] = Vmprv[pq] + step * z[nb+pq]
    lam0 = lam + step * z[2*nb]
    V0 = Vm0 * exp(1j * Va0)

    return V0, lam0, z


