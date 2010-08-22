# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2009-2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

from numpy import angle, exp, linalg, multiply, conj, r_, Inf
from scipy.sparse.linalg import splu

from ppoption import ppoption

def fdpf(Ybus, Sbus, V0, Bp, Bpp, ref, pv, pq, ppopt=None):
    """Solves the power flow using a fast decoupled method.

    Solves for bus voltages given the full system admittance matrix (for
    all buses), the complex bus power injection vector (for all buses),
    the initial vector of complex bus voltages, the FDPF matrices B prime
    and B double prime, and column vectors with the lists of bus indices
    for the swing bus, PV buses, and PQ buses, respectively. The bus voltage
    vector contains the set point for generator (including ref bus)
    buses, and the reference angle of the swing bus, as well as an initial
    guess for remaining magnitudes and angles. MPOPT is a MATPOWER options
    vector which can be used to set the termination tolerance, maximum
    number of iterations, and output options (see MPOPTION for details).
    Uses default options if this parameter is not given. Returns the
    final complex voltages, a flag which indicates whether it converged
    or not, and the number of iterations performed.

    @see: L{runpf}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
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

    ## evaluate initial mismatch
    mis = (multiply(V, conj(Ybus * V)) - Sbus) / Vm
    P = mis[r_[pv, pq]].real
    Q = mis[pq].imag

    ## check tolerance
    normP = linalg.norm(P, Inf)
    normQ = linalg.norm(Q, Inf)
    if verbose > 0:
        alg = ppopt[1]
        s = 'XB' if ppopt[1] == 2 else 'BX'
        print '(fast-decoupled, %s)' % s
    if verbose > 1:
        print 'iteration     max mismatch (p.u.)  '
        print 'type   #        P            Q     '
        print '---- ----  -----------  -----------'
        print '  -  %3d   %10.3e   %10.3e' % (i, normP, normQ)
    if normP < tol and normQ < tol:
        converged = 1
        if verbose > 1:
            print 'Converged!'

    ## reduce B matrices
    pq_col = [[k] for k in pq]
    pvpq_col = [[k] for k in pvpq]
    Bp = Bp[pvpq_col, pvpq].tocsc() # splu requires a CSC matrix
    Bpp = Bpp[pq_col, pq].tocsc()

    ## factor B matrices
    Bp_solver = splu(Bp)
    Bpp_solver = splu(Bpp)

    ## do P and Q iterations
    while (~converged and i < max_it):
        ## update iteration counter
        i = i + 1

        ##-----  do P iteration, update Va  -----
        dVa = -Bp_solver.solve(P)

        ## update voltage
        Va[pvpq] = Va[pvpq] + dVa
        V = Vm * exp(1j * Va)

        ## evalute mismatch
        mis = (multiply(V, conj(Ybus * V)) - Sbus) / abs(V)
        P = mis[pvpq].real
        Q = mis[pq].imag

        ## check tolerance
        normP = linalg.norm(P, Inf)
        normQ = linalg.norm(Q, Inf)
        if verbose > 1:
            print "  %s  %3d   %10.3e   %10.3e" % (type,i, normP, normQ)
        if normP < tol and normQ < tol:
            converged = 1
            if verbose:
                print 'Fast-decoupled power flow converged in %d P-iterations '
                'and %d Q-iterations.\n' % (i, i - 1)
            break

        ##-----  do Q iteration, update Vm  -----
        dVm = -Bpp_solver.solve(Q)

        ## update voltage
        Vm[pq] = Vm[pq] + dVm
        V = Vm * exp(1j * Va)

        ## evalute mismatch
        mis = (multiply(V, conj(Ybus * V)) - Sbus) / abs(V)
        P = mis[pvpq].real
        Q = mis[pq].imag

        ## check tolerance
        normP = linalg.norm(P, Inf)
        normQ = linalg.norm(Q, Inf)
        if verbose > 1:
            print '  Q  %3d   %10.3e   %10.3e' % (i, normP, normQ)
        if normP < tol and normQ < tol:
            converged = 1
            if verbose:
                print 'Fast-decoupled power flow converged in %d P-iterations '
                'and %d Q-iterations.\n' % (i, i)
            break

    if verbose:
        if ~converged:
            print 'Fast-decoupled power flow did not converge in %d '
            'iterations.' % i

    return V, converged, i
