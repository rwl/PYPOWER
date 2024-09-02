''' Solves the corrector step of a continuation power flow using a
full Newton method with selected parameterization scheme.
'''

from numpy import r_, angle, conj, linalg, inf, array, exp

from scipy.sparse import vstack, hstack

from pypower.ppoption import ppoption
from pypower.cpf_p import cpf_p
from pypower.dSbus_dV import dSbus_dV
from pypower.cpf_p_jac import cpf_p_jac
from pypower.pplinsolve import pplinsolve

def cpf_corrector(Ybus, Sbus, V0, ref, pv, pq,
                  lam0, Sxfr, Vprv, lamprv, z, step, parameterization, ppopt):

    # default arguments
    if ppopt is None:
        ppopt = ppoption(ppopt)

    # options
    verbose = ppopt["VERBOSE"]
    tol = ppopt["PF_TOL"]
    max_it = ppopt["PF_MAX_IT"]

    # initialize
    converged = 0
    i = 0
    V = V0
    Va = angle(V)
    Vm = abs(V)
    lam = lam0

    # set up indexing for updating V
    pvpq = r_[pv, pq]
    npv = len(pv)
    npq = len(pq)
    nb = len(V)
    j1 = 0
    j2 = npv    # j1:j2 - V angle of pv buses
    j3 = j2
    j4 = j2 + npq   # j1:j2 - V angle of pv buses
    j5 = j4
    j6 = j4 + npq   # j5:j6 - V mag of pq buses
    j7 = j6
    j8 = j6 + 1    # j7:j8 - lambda

    # evaluate F(x0, lam0), including Sxfr transfer/loading

    mis = V * conj(Ybus.dot(V)) - Sbus - lam*Sxfr
    F = r_[mis[pvpq].real, mis[pq].imag]

    # evaluate P(x0, lambda0)
    P = cpf_p(parameterization, step, z, V, lam, Vprv, lamprv, pv, pq)

    # augment F(x, lambda) with P(x, lambda)
    F = r_[F, P]

    # check tolerance
    normF = linalg.norm(F, inf)
    if verbose > 1:
        print('\n it    max P & Q mismatch (p.u.)')
        print('\n----  ---------------------------')
        print('\n%3d        %10.3e' % (i, normF))
    if normF < tol:
        converged = 1
        if verbose > 1:
            print('\nConverged!\n')
    
    # do Newton iterations
    while not converged and i < max_it:
        # update iteration counter
        i = i + 1

        # evaluate Jacobian
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

        # augment J with real/imag -Sxfr and z^T
        J = vstack([
            hstack([J, dF_dlam]),
            hstack([dP_dV, dP_dlam])
        ], format="csr")

        # compute update step
        dx = -1 * pplinsolve(J, F)

        # update voltage
        if npv:
            Va[pv] = Va[pv] + dx[j1:j2]
        if npq:
            Va[pq] = Va[pq] + dx[j3:j4]
            Vm[pq] = Vm[pq] + dx[j5:j6]
        V = Vm * exp(1j * Va)
        Vm = abs(V)
        Va = angle(V)

        # update lambda
        lam = lam + dx[j7:j8]

        # evalute F(x, lam)
        mis = V * conj(Ybus.dot(V)) - Sbus - lam*Sxfr
        F = r_[mis[pv].real, mis[pq].real, mis[pq].imag]

        # evaluate P(x, lambda)
        P = cpf_p(parameterization, step, z, V, lam, Vprv, lamprv, pv, pq)

        # augment F(x, lambda) with P(x, lambda)
        F = r_[F, P]

        # check for convergence
        normF = linalg.norm(F, inf)
        if verbose > 1:
            print('\n%3d        %10.3e' % (i, normF))
        if normF < tol:
            converged = 1
            if verbose:
                print('\nNewton''s method corrector converged in %d iterations.\n' % i)
    
    if verbose:
        if not converged:
            print('\nNewton''s method corrector did not converge in %d iterations.\n' % i)

    return V, converged, i, lam



        






