'''Computes partial derivatives of CPF parameterization function.
'''

from numpy import r_, zeros, angle


def cpf_p_jac(parameterization, z, V, lam, Vprv, lamprv, pv, pq):
    if parameterization == 1:
        npv = len(pv)
        npq = len(pq)
        dP_dV = zeros(npv+2*npq)
        if lam >= lamprv:
            dP_dlam = 1.0
        else:
            dP_dlam = -1.0

    elif parameterization == 2:
        pvpq = r_[pv, pq]

        Va = angle(V)
        Vm = abs(V)
        Vaprv = angle(Vprv)
        Vmprv = abs(Vprv)
        dP_dV = 2 * (r_[Va[pvpq], Vm[pq]] -
                     r_[Vaprv[pvpq], Vmprv[pq]])
        if lam == lamprv:
            dP_dlam = 1.0
        else:
            dP_dlam = 2 * (lam - lamprv)

    elif parameterization == 3:
        nb = len(V)
        dP_dV = z[r_[pv, pq, nb+pq]]
        dP_dlam = z[2 * nb]

    return dP_dV, dP_dlam