'''Computes the value of the CPF parameterization function.
'''

from numpy import r_, angle, square, dot, array


def cpf_p(parameterization, step, z, V, lam, Vprv, lamprv, pv, pq):
    # evaluate P(x0, lambda0)
    if parameterization == 1:
        if lam >= lamprv:
            P = lam - lamprv - step
        else:
            P = lamprv - lam - step

    elif parameterization == 2:
        pvpq = r_[pv, pq]

        Va = angle(V)
        Vm = abs(V)
        Vaprv = angle(Vprv)
        Vmprv = abs(Vprv)
        P = sum(square(r_[Va[pvpq], Vm[pq], lam] -
                       r_[Vaprv[pvpq], Vmprv[pq], lamprv])) - square(step)

    elif parameterization == 3:
        pvpq = r_[pv, pq]

        nb = len(V)
        Va = angle(V)
        Vm = abs(V)
        Vaprv = angle(Vprv)
        Vmprv = abs(Vprv)
        P = dot(z[r_[pvpq, nb+pq, 2*nb]].reshape((1, -1)), array(r_[Va[pvpq],
                                                                      Vm[pq], lam] - r_[Vaprv[pvpq], Vmprv[pq], lamprv]).T) - step

    return P
