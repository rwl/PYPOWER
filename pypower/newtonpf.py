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

from numpy import angle, exp, linalg, multiply, conj, r_, Inf

from scipy.sparse import hstack, vstack
from scipy.sparse.linalg import spsolve, splu

from dSbus_dV import dSbus_dV
from ppoption import ppoption

def newtonpf(Ybus, Sbus, V0, ref, pv, pq, ppopt=None):
    """Solves the power flow using a full Newton's method.

    solves for bus voltages given the full system admittance matrix (for
    all buses), the complex bus power injection vector (for all buses),
    the initial vector of complex bus voltages, and column vectors with
    the lists of bus indices for the swing bus, PV buses, and PQ buses,
    respectively. The bus voltage vector contains the set point for
    generator (including ref bus) buses, and the reference angle of the
    swing bus, as well as an initial guess for remaining magnitudes and
    angles. MPOPT is a MATPOWER options vector which can be used to
    set the termination tolerance, maximum number of iterations, and
    output options (see MPOPTION for details). Uses default options if
    this parameter is not given. Returns the final complex voltages, a
    flag which indicates whether it converged or not, and the number of
    iterations performed.

    @see: L{runpf}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## default arguments
    if ppopt is None:
        ppopt = ppoption

    ## options
    tol     = ppopt[2]
    max_it  = ppopt[3]
    verbose = ppopt[31]

    ## initialize
    converged = 0
    i = 0
    V = V0
    Va = angle(V)
    Vm = abs(V)

    ## set up indexing for updating V
    pvpq = pv + pq
    npv = len(pv)
    npq = len(pq)
    j1 = 0;         j2 = npv           ## j1:j2 - V angle of pv buses
    j3 = j2 + 1;    j4 = j2 + npq      ## j3:j4 - V angle of pq buses
    j5 = j4 + 1;    j6 = j4 + npq      ## j5:j6 - V mag of pq buses

    ## evaluate F(x0)
    mis = multiply(V, conj(Ybus * V)) - Sbus
    F = r_[  mis[pv].real,
             mis[pq].real,
             mis[pq].imag  ]

    ## check tolerance
    normF = linalg.norm(F, Inf)
    if verbose > 0:
        print '(Newton)'
    if verbose > 1:
        print ' it    max P & Q mismatch (p.u.)'
        print '----  ---------------------------'
        print '%3d        %10.3e' % (i, normF)
    if normF < tol:
        converged = 1
        if verbose > 1:
            print 'Converged!'

    ## do Newton iterations
    while (not converged and i < max_it):
        ## update iteration counter
        i = i + 1

        ## evaluate Jacobian
        dS_dVm, dS_dVa = dSbus_dV(Ybus, V)

        pq_col = [[i] for i in pq]
        pvpq_col = [[i] for i in pvpq]
        J11 = dS_dVa[pvpq_col, pvpq].real
        J12 = dS_dVm[pvpq_col, pq].real
        J21 = dS_dVa[pq_col, pvpq].imag
        J22 = dS_dVm[pq_col, pq].imag

        J = vstack([
                hstack([J11, J12]),
                hstack([J21, J22])
            ], format="csr")

        ## compute update step
        dx = -1 * spsolve(J, F)

        ## update voltage
        if npv:
            Va[pv] = Va[pv] + dx[j1:j2]
        if npq:
            Va[pq] = Va[pq] + dx[j3:j4]
            Vm[pq] = Vm[pq] + dx[j5:j6]
        V = Vm * exp(1j * Va)
        Vm = abs(V)            ## update Vm and Va again in case
        Va = angle(V)          ## we wrapped around with a negative Vm

        ## evalute F(x)
        mis = multiply(V, conj(Ybus * V)) - Sbus
        F = r_[  mis[pv].real,
                 mis[pq].real,
                 mis[pq].imag  ]

        ## check for convergence
        normF = linalg.norm(F, Inf)
        if verbose > 1:
            print '%3d        %10.3e' % (i, normF)
        if normF < tol:
            converged = 1
            if verbose:
                print "Newton's method power flow converged in %d "
                "iterations." % i

    if verbose:
        if not converged:
            print "Newton's method power did not converge in %d "
            "iterations." % i

    return V, converged, i
