# Copyright (C) 1996-2010 Power System Engineering Research Center
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

from numpy import angle, linalg, multiply, conj, r_, Inf

from ppoption import ppoption

def gausspf(Ybus, Sbus, V0, ref, pv, pq, ppopt=None):
    """Solves the power flow using a Gauss-Seidel method.

    solves for bus voltages given the full system admittance matrix (for
    all buses), the complex bus power injection vector (for all buses),
    the initial vector of complex bus voltages, and column vectors with
    the lists of bus indices for the swing bus, PV buses, and PQ buses,
    respectively. The bus voltage vector contains the set point for
    generator (including ref bus) buses, and the reference angle of the
    swing bus, as well as an initial guess for remaining magnitudes and
    angles. MPOPT is a MATPOWER options vector which can be used to
    set the termination tolerance, maximum number of iterations, and
    output options (see MPOPTION for details). Uses default options
    if this parameter is not given. Returns the final complex voltages,
    a flag which indicates whether it converged or not, and the number
    of iterations performed.

    @see: l{runpf}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## default arguments
    if ppopt is None:
        ppopt = ppoption()

    ## options
    tol     = ppopt[2]
    max_it  = ppopt[4]
    verbose = ppopt[31]

    ## initialize
    converged = 0
    i = 0
    V = V0
    Va = angle(V)
    Vm = abs(V)

    ## set up indexing for updating V
    npv = len(pv)
    npq = len(pq)
    pvpq = pv + pq

    ## evaluate F(x0)
    mis = multiply(V, conj(Ybus * V)) - Sbus
    F = r_[  mis[pvpq].real,
             mis[pq].imag   ]

    ## check tolerance
    normF = linalg.norm(F, Inf)
    if verbose > 0:
        print '(Gauss-Seidel)'
    if verbose > 1:
        print ' it    max P & Q mismatch (p.u.)'
        print '----  ---------------------------'
        print '%3d        %10.3e' % (i, normF)
    if normF < tol:
        converged = 1
        if verbose > 1:
            print 'Converged!'

    ## do Gauss-Seidel iterations
    while (~converged and i < max_it):
        ## update iteration counter
        i = i + 1;

        ## update voltage
        ## at PQ buses
        for k in pq[range(npq)]:
            V[k] = V[k] + (conj(Sbus[k] / V[k]) - Ybus[k, :] * V ) / Ybus[k, k]

        ## at PV buses
        if npv:
            for k in pv[range(npv)]:
                Sbus[k] = Sbus[k].real + 1j * (V[k] * conj(Ybus[k,:] * V)).imag
                V[k] = V[k] + (conj(Sbus[k] / V[k]) - Ybus[k,:]*V) / Ybus[k,k]
#               V[k] = Vm[k] * V[k] / abs(V[k])
            V[pv] = Vm[pv] * V[pv] / abs(V[pv])

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
                print 'Gauss-Seidel power flow converged in %d iterations.' % i

    if verbose:
        if ~converged:
            print 'Gauss-Seidel power did not converge in %d iterations.' % i

    return V, converged, i
