# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

from numpy import real, imag, exp, angle, zeros, r_, conj, linalg, Inf
from numpy import flatnonzero as find

from scipy.sparse import hstack, vstack
from scipy.sparse.linalg import spsolve, splu

from pypower.dSbus_dV import dSbus_dV
from pypower.makeSbus import makeSbus
from pypower.idx_bus import PD, QD


def cpf_correctlmbda(baseMVA, bus, gen, Ybus, Vm_assigned, V_predicted,
                      lmbda_predicted, initQPratio, loadvarloc, ref, pv, pq):
    """ Correct lmbda in correction step near load point.

    Corrects lmbda(ie, real power of load) in cpf correction step
    near the nose point. Use NR's method to solve the nonlinear equations.

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """

    ## options
    tol     = 1e-5 # mpopt(2)
    max_it  = 100  # mpopt(3)
    verbose = 0    # mpopt(31)

    ## initialize
    j = 1j
    converged = 0
    i = 0
    V = V_predicted
    lmbda = lmbda_predicted
    Va = angle(V)
    Vm = abs(V)

    ## set up indexing for updating V
    npv = len(pv)
    npq = len(pq)
    j1 = 0;        j2 = npv           ## j1:j2 - V angle of pv buses
    j3 = j2 + 1;   j4 = j2 + npq      ## j3:j4 - V angle of pq buses
    j5 = j4 + 1;   j6 = j4 + npq      ## j5:j6 - V mag of pq buses
    j7 = j6 + 1                        ## j7 - lmbda

    pv_bus = len(find(pv == loadvarloc)) > 0

    ## set load as lmbda indicates
    bus[loadvarloc, PD] = lmbda * baseMVA
    bus[loadvarloc, QD] = lmbda * baseMVA * initQPratio

    ## compute complex bus power injections (generation - load)
    SbusInj = makeSbus(baseMVA, bus, gen)

    ## evalute F(x0)
    mis = V * conj(Ybus * V) - SbusInj
    mis = -mis # NOTE: use reverse mismatch and correspondingly use '(-)Jacobian" obtained from dSbus_dV
    F = r_[ real(mis(pv)),
            real(mis(pq)),
            imag(mis(pq)),
            abs(V(loadvarloc)) - Vm_assigned(loadvarloc)   ]

    ## do Newton iterations
    while (not converged & i < max_it):
        ## update iteration counter
        i = i + 1

        ## evaluate Jacobian
        dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)

        j11 = real(dSbus_dVa[[pv, pq], [pv, pq]])
        j12 = real(dSbus_dVm[[pv, pq], pq])
        j21 = imag(dSbus_dVa[pq, [pv, pq]])
        j22 = imag(dSbus_dVm[pq, pq])

        J = vstack([
                hstack([j11, j12]),
                hstack([j21, j22])
            ], format="csr")

        ## evaluate dDeltaP/dlmbda, dDeltaQ/dlmbda, dDeltaVm/dlmbda,
        ## dDeltaVm/dVa, dDeltaVm/dVm
        dDeltaP_dlmbda = zeros(npv+npq)
        dDeltaQ_dlmbda = zeros(npq)
        if pv_bus: # pv bus
            dDeltaP_dlmbda[find(pv == loadvarloc)] = -1         # corresponding to deltaP
        else: # pq bus
            dDeltaP_dlmbda[npv + find(pq == loadvarloc)] = -1   # corresponding to deltaP
            dDeltaQ_dlmbda[find(pq == loadvarloc)] = -initQPratio   # corresponding to deltaQ

        dDeltaVm_dlmbda = zeros((1, 1))
        dDeltaVm_dVa = zeros((1, npv+npq))
        dDeltaVm_dVm = zeros((1, npq))
        dDeltaVm_dVm[0, find(pq == loadvarloc)] = -1

        ## form augmented Jacobian
        J12 = vstack([dDeltaP_dlmbda,
                      dDeltaQ_dlmbda])
        J21 = hstack([dDeltaVm_dVa, dDeltaVm_dVm])
        J22 = dDeltaVm_dlmbda
        augJ = vstack([
                hstack([-J,  J12]),
                hstack([J21, J22])
            ], format="csr")

        ## compute update step
        dx = -1 * spsolve(augJ, F)

        ## update voltage.
        # NOTE: voltage magnitude of pv buses, voltage magnitude
        # and angle of reference bus are not updated, so they keep as constants
        # (ie, the value as in the initial guess)
        if npv:
            Va[pv] = Va[pv] + dx[j1:j2]
        if npq:
            Va[pq] = Va[pq] + dx[j3:j4]
            Vm[pq] = Vm[pq] + dx[j5:j6]

        lmbda = lmbda + dx[j7]

        V = Vm * exp(j * Va) # NOTE: angle is in radians in pf solver, but in degree in case data
        Vm = abs(V)            ## update Vm and Va again in case
        Va = angle(V)          ## we wrapped around with a negative Vm

        ## set load as lmbda indicates
        bus[loadvarloc, PD] = lmbda * baseMVA
        bus[loadvarloc, QD] = lmbda * baseMVA * initQPratio

        ## compute complex bus power injections (generation - load)
        SbusInj = makeSbus(baseMVA, bus, gen)

        ## evalute F(x)
        mis = V * conj(Ybus * V) - SbusInj
        mis = -mis
        F = r_[   real(mis(pv)),
                  real(mis(pq)),
                  imag(mis(pq)),
                  abs(V(loadvarloc)) - Vm_assigned(loadvarloc)   ]

        ## check for convergence
        normF = linalg.norm(F, Inf)
        if verbose > 1:
            print '\niteration [%3d]\t\tnorm of mismatch: %10.3e' % (i, normF)

        if normF < tol:
            converged = True

    iterNum = i

    return V, lmbda, converged, iterNum
