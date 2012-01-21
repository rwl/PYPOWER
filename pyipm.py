# Copyright (C) 2012 Richard Lincoln
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

"""Python Interior Point Method.
"""

from math import log

from numpy import r_, dot

from scipy.sparse import spdiags, hstack, vstack, csr_matrix as sparse
from scipy.sparse.linalg import splu, spsolve


NEWTON = 'newton'
MEHROTRA = 'mehrotra'


def pyipm(f, z0, A, b, Aeq, beq, l, u, g, opts=None):
    """Python Interior Point Method.

    @see: Federico Milano, "Power System Modelling and Scripting",
    Springer, 2010, http://www.uclm.es/area/gsee/web/Federico/book.htm
    """
    ## setup dimensions, variables, vectors and matrices
    ng = len(beq)  # num equality constraints
    nh = len(b)    # num inequality constraints
    nz = len(z0)
    Zz = sparse((ng, ng))
    Oz = None
    Gz = None
    Hz = None
    Hes = None

    ## parameters
    opts = opts or {}
    sigma = opts.get('sigma', 0.2)        # centering parameter
    method = opts.get('method', NEWTON)   # method for variable directions
    eps_mu = opts.get('eps_mu', 1e-10)    # barrier parameter threshold
    eps1 = opts.get('eps1', 0.0001)       # equality constraint tolerance
    eps2 = opts.get('eps2', eps1 * 0.01)  # variable increment tolerance
    max_iter = opts.get('max_iter', 20)
    gamma = 0.95                          # safety factor for step length
    iteration = 1
    mui = sigma / nh
    msg = "Iter. = %3d,  mui = %s,  |dz| = %s,  |g(z)| = %s,  |dOF| = %s\n"

    ## initial guess of primal, dual and slack variables
    s = None  # slack variables
    s = s + 1e-6  # avoid zero slack variables
    pi = mui / s  # dual variables associated with inequality constraints
    rho = None  # dual variables associated with equality constraints
    rho[:nb] = 1.0

    ## primal dual interior point method
    while True:
        ## compute g(z), h(z, s) and Jacobian and Hessian matrices
        f(z)
        g(z, s)
        h = h + s

        s = (pi * s) - mui
        Lz = Oz + Gz.T * rho + Hz.T * pi
        Hp = spdiags(pi / s)

        ## reduced system
        Lr = vstack(
            hstack(Hes + Hz.T * (Hp * Hz), Gz),
            hstack(Gz.T, Zz)
        )
        if iteration <= 2:
            F = splu(Lr)
        try:
            C = F.solve(Lr)
        except:
            C = spsolve(Lr, F)

        if method == NEWTON:
            Hs = spdiags(1 / s)
            Dz = -1 * r_[Lz + Hz.T * (Hp * h - Hs * s), g]

            C.solve(Lr, Dz)
            spsolve(Lr, Dz)

            Ds = -1 * h - Hz * Dz[:nz]
            Dp = -Hs * s - Hp * Ds
        elif method == MEHROTRA:
            ## predictor step
            Dz = -1 * r_[Lz + Hz.T * (Hp * h - pi), g]

            C.solve(Lr, Dz)
            spsolve(Lr, Dz)

            Ds = -1 * h - Hz * Dz[:nz]
            Dp = -1 * pi - Hp * Ds

            ## centering correction
            alpha_P, alpha_D = step_length(Ds, Dp, s, pi, gamma)
            cgap_p = dot(s + alpha_P * Ds, pi + alpha_D * Ds)
            cgap = dot(s, pi)
            mui = min((cgap_p / cgap)**2, 0.2) * cgap_p / nh
            s = pi + (((Ds * Dp) - mui) / s)

            ## corrector step
            Dz = -1 * r_[Lz + Hz.T * (Hp * h - s), g]

            C.solve(Lr, Dz)
            spsolve(Lr, Dz)

            Ds = -1 * h - Hz * Dz[:nz]
            Dp = -1 * s - Hp * Dp
        else:
            raise ValueError, 'invalid method'

        ## update primal and dual variables
        alpha_P, alpha_D = step_length(Ds, Dp, s, pi, gamma)
        z = z + alpha_P * Dz[:nz]
        s = alpha_P * Ds
        rho = alpha_D * Dz[nz:]
        pi = alpha_D * Dp

        ## objective function
        obj_old = obj
        obj = f()
        obj = obj - mui * sum(log(s + eps_mu))

        ## centering parameter, complementarity gap and barrier parameter
        sigma = max(0.99 * sigma, 0.1)
        cgap = dot(s, pi)
        mui = min(abs(sigma * cgap / nh), 1.0)

        ## convergence tests
        test1 = mui <= eps_mu
        norma2 = max(abs(Dz))
        test2 = norma2 <- eps2
        norma3 = error = max(abs(g))
        test3 = norma3 <= eps1
        norma4 = abs(obj - old_obj) / (1 + abs(obj))
        test4 = norma4 <= eps2
        print msg % (iteration, mui, norma2, norma3, norma4)
        if test1 and test2 and test3 and test4:
            break

        iteration += 1
        if iteration > max_iter:
            break


def step_length(Ds, Dp, ss, pi, gamma):
    ratio1 = [1.0 / gamma] + [-s / d for s, d in zip(ss, Ds) if d < 0]
    ratio2 = [1.0 / gamma] + [-s / d for s, d in zip(pi, Dp) if d < 0]

    alpha_P = gamma * min(ratio1)
    alpha_D = gamma * min(ratio2)

    return alpha_P, alpha_D
