# Copyright (C) 2009-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln
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

from numpy import array, flatnonzero, Inf, any, isnan, ones, r_, finfo, \
    zeros, dot, absolute

from numpy.linalg import norm

from scipy.sparse import csr_matrix, vstack, hstack, eye
from scipy.sparse.linalg import spsolve

EPS = finfo(float).eps

def pips(f_fcn, x0, A=None, l=None, u=None, xmin=None, xmax=None,
         gh_fcn=None, hess_fcn=None, opt=None):
    """Primal-dual interior point method for NLP (non-linear programming).
    Minimize a function F(X) beginning from a starting point M{x0}, subject to
    optional linear and non-linear constraints and variable bounds::

            min f(x)
             x

    subject to::

            g(x) = 0            (non-linear equalities)
            h(x) <= 0           (non-linear inequalities)
            l <= A*x <= u       (linear constraints)
            xmin <= x <= xmax   (variable bounds)

    Note: The calling syntax is almost identical to that of FMINCON from
    MathWorks' Optimization Toolbox. The main difference is that the linear
    constraints are specified with C{A}, C{L}, C{U} instead of C{A}, C{B},
    C{Aeq}, C{Beq}. The functions for evaluating the objective function,
    constraints and Hessian are identical.

    Example from U{http://en.wikipedia.org/wiki/Nonlinear_programming}:
        >>> from numpy import array, r_, float64, dot
        >>> from scipy.sparse import csr_matrix
        >>> def f2(x):
        ...     f = -x[0] * x[1] - x[1] * x[2]
        ...     df = -r_[x[1], x[0] + x[2], x[1]]
        ...     # actually not used since 'hess_fcn' is provided
        ...     d2f = -array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], float64)
        ...     return f, df, d2f
        >>> def gh2(x):
        ...     h = dot(array([[1, -1, 1],
        ...                    [1,  1, 1]]), x**2) + array([-2.0, -10.0])
        ...     dh = 2 * csr_matrix(array([[ x[0], x[0]],
        ...                                [-x[1], x[1]],
        ...                                [ x[2], x[2]]]))
        ...     g = array([])
        ...     dg = None
        ...     return h, g, dh, dg
        >>> def hess2(x, lam):
        ...     mu = lam["ineqnonlin"]
        ...     a = r_[dot(2 * array([1, 1]), mu), -1, 0]
        ...     b = r_[-1, dot(2 * array([-1, 1]),mu),-1]
        ...     c = r_[0, -1, dot(2 * array([1, 1]),mu)]
        ...     Lxx = csr_matrix(array([a, b, c]))
        ...     return Lxx
        >>> x0 = array([1, 1, 0], float64)
        >>> solution = pips(f2, x0, gh_fcn=gh2, hess_fcn=hess2)
        >>> round(solution["f"], 11) == -7.07106725919
        True
        >>> solution["output"]["iterations"]
        8

    Ported by Richard Lincoln from the MATLAB Interior Point Solver (MIPS)
    (v1.9) by Ray Zimmerman.  MIPS is distributed as part of the MATPOWER
    project, developed at the Power System Engineering Research Center (PSERC),
    Cornell. See U{http://www.pserc.cornell.edu/matpower/} for more info.
    MIPS was ported by Ray Zimmerman from C code written by H. Wang for his
    PhD dissertation:
      - "On the Computation and Application of Multi-period
        Security-Constrained Optimal Power Flow for Real-time
        Electricity Market Operations", Cornell University, May 2007.

    See also:
      - H. Wang, C. E. Murillo-Sanchez, R. D. Zimmerman, R. J. Thomas,
        "On Computational Issues of Market-Based Optimal Power Flow",
        IEEE Transactions on Power Systems, Vol. 22, No. 3, Aug. 2007,
        pp. 1185-1193.

    All parameters are optional except C{f_fcn} and C{x0}.
    @param f_fcn: Function that evaluates the objective function, its gradients
                  and Hessian for a given value of M{x}. If there are
                  non-linear constraints, the Hessian information is provided
                  by the 'hess_fcn' argument and is not required here.
    @type f_fcn: callable
    @param x0: Starting value of optimization vector M{x}.
    @type x0: array
    @param A: Optional linear constraints.
    @type A: csr_matrix
    @param l: Optional linear constraints. Default values are M{-Inf}.
    @type l: array
    @param u: Optional linear constraints. Default values are M{Inf}.
    @type u: array
    @param xmin: Optional lower bounds on the M{x} variables, defaults are
                 M{-Inf}.
    @type xmin: array
    @param xmax: Optional upper bounds on the M{x} variables, defaults are
                 M{Inf}.
    @type xmax: array
    @param gh_fcn: Function that evaluates the optional non-linear constraints
                   and their gradients for a given value of M{x}.
    @type gh_fcn: callable
    @param hess_fcn: Handle to function that computes the Hessian of the
                     Lagrangian for given values of M{x}, M{lambda} and M{mu},
                     where M{lambda} and M{mu} are the multipliers on the
                     equality and inequality constraints, M{g} and M{h},
                     respectively.
    @type hess_fcn: callable
    @param opt: optional options dictionary with the following keys, all of
                which are also optional (default values shown in parentheses)
                  - C{verbose} (False) - Controls level of progress output
                    displayed
                  - C{feastol} (1e-6) - termination tolerance for feasibility
                    condition
                  - C{gradtol} (1e-6) - termination tolerance for gradient
                    condition
                  - C{comptol} (1e-6) - termination tolerance for
                    complementarity condition
                  - C{costtol} (1e-6) - termination tolerance for cost
                    condition
                  - C{max_it} (150) - maximum number of iterations
                  - C{step_control} (False) - set to True to enable step-size
                    control
                  - C{max_red} (20) - maximum number of step-size reductions if
                    step-control is on
                  - C{cost_mult} (1.0) - cost multiplier used to scale the
                    objective function for improved conditioning. Note: The
                    same value must also be passed to the Hessian evaluation
                    function so that it can appropriately scale the objective
                    function term in the Hessian of the Lagrangian.
    @type opt: dict

    @rtype: dict
    @return: The solution dictionary has the following keys:
               - C{x} - solution vector
               - C{f} - final objective function value
               - C{converged} - exit status
                   - True = first order optimality conditions satisfied
                   - False = maximum number of iterations reached
                   - None = numerically failed
               - C{output} - output dictionary with keys:
                   - C{iterations} - number of iterations performed
                   - C{hist} - dictionary of arrays with trajectories of the
                     following: feascond, gradcond, compcond, costcond, gamma,
                     stepsize, obj, alphap, alphad
                   - C{message} - exit message
               - C{lmbda} - dictionary containing the Langrange and Kuhn-Tucker
                 multipliers on the constraints, with keys:
                   - C{eqnonlin} - non-linear equality constraints
                   - C{ineqnonlin} - non-linear inequality constraints
                   - C{mu_l} - lower (left-hand) limit on linear constraints
                   - C{mu_u} - upper (right-hand) limit on linear constraints
                   - C{lower} - lower bound on optimization variables
                   - C{upper} - upper bound on optimization variables

    @see: U{http://www.pserc.cornell.edu/matpower/}
    @license: Apache License version 2.0
    """
    nx = x0.shape[0]                        # number of variables
    nA = A.shape[0] if A is not None else 0 # number of original linear constr

    # default argument values
#    l = array([]) if A is None else l
#    u = array([]) if A is None else u
    l = -Inf * ones(nA) if l is None else l
    u =  Inf * ones(nA) if u is None else u
    xmin = -Inf * ones(x0.shape[0]) if xmin is None else xmin
    xmax =  Inf * ones(x0.shape[0]) if xmax is None else xmax
    if gh_fcn is None:
        nonlinear = False
        gn = array([])
        hn = array([])
    else:
        nonlinear = True

    opt = {} if opt is None else opt
    # options
    if not opt.has_key("feastol"):
        opt["feastol"] = 1e-06
    if not opt.has_key("gradtol"):
        opt["gradtol"] = 1e-06
    if not opt.has_key("comptol"):
        opt["comptol"] = 1e-06
    if not opt.has_key("costtol"):
        opt["costtol"] = 1e-06
    if not opt.has_key("max_it"):
        opt["max_it"] = 150
    if not opt.has_key("max_red"):
        opt["max_red"] = 20
    if not opt.has_key("step_control"):
        opt["step_control"] = False
    if not opt.has_key("cost_mult"):
        opt["cost_mult"] = 1
    if not opt.has_key("verbose"):
        opt["verbose"] = False

    # initialize history
    hist = {}

    # constants
    xi = 0.99995
    sigma = 0.1
    z0 = 1
    alpha_min = 1e-8
#    rho_min = 0.95
#    rho_max = 1.05
    mu_threshold = 1e-5

    # initialize
    i = 0                       # iteration counter
    converged = False           # flag
    eflag = False               # exit flag

    # add var limits to linear constraints
    eyex = eye(nx, nx, format="csr")
    AA = eyex if A is None else vstack([eyex, A], "csr")
    ll = r_[xmin, l]
    uu = r_[xmax, u]

    # split up linear constraints
    ieq = flatnonzero( absolute(uu - ll) <= EPS )
    igt = flatnonzero( (uu >=  1e10) & (ll > -1e10) )
    ilt = flatnonzero( (ll <= -1e10) & (uu <  1e10) )
    ibx = flatnonzero( (absolute(uu - ll) > EPS) & (uu < 1e10) & (ll > -1e10) )
    # zero-sized sparse matrices unsupported
    Ae = AA[ieq, :] if len(ieq) else None
    if len(ilt) or len(igt) or len(ibx):
        idxs = [(1, ilt), (-1, igt), (1, ibx), (-1, ibx)]
        Ai = vstack([sig * AA[idx, :] for sig, idx in idxs if len(idx)])
    else:
        Ai = None
    be = uu[ieq, :]
    bi = r_[uu[ilt], -ll[igt], uu[ibx], -ll[ibx]]

    # evaluate cost f(x0) and constraints g(x0), h(x0)
    x = x0
    f, df, _ = f_fcn(x)                 # cost
    f = f * opt["cost_mult"]
    df = df * opt["cost_mult"]
    if nonlinear:
        hn, gn, dhn, dgn = gh_fcn(x)        # non-linear constraints
        h = hn if Ai is None else r_[hn, Ai * x - bi] # inequality constraints
        g = gn if Ae is None else r_[gn, Ae * x - be] # equality constraints

        if (dhn is None) and (Ai is None):
            dh = None
        elif dhn is None:
            dh = Ai.T
        elif Ae is None:
            dh = dhn
        else:
            dh = hstack([dhn, Ai.T])

        if (dgn is None) and (Ae is None):
            dg = None
        elif dgn is None:
            dg = Ae.T
        elif Ae is None:
            dg = dgn
        else:
            dg = hstack([dgn, Ae.T])
    else:
        h = -bi if Ai is None else Ai * x - bi        # inequality constraints
        g = -be if Ae is None else Ae * x - be        # equality constraints
        dh = None if Ai is None else Ai.T     # 1st derivative of inequalities
        dg = None if Ae is None else Ae.T     # 1st derivative of equalities

    # some dimensions
    neq = g.shape[0]           # number of equality constraints
    niq = h.shape[0]           # number of inequality constraints
    neqnln = gn.shape[0]       # number of non-linear equality constraints
    niqnln = hn.shape[0]       # number of non-linear inequality constraints
    nlt = len(ilt)             # number of upper bounded linear inequalities
    ngt = len(igt)             # number of lower bounded linear inequalities
    nbx = len(ibx)             # number of doubly bounded linear inequalities

    # initialize gamma, lam, mu, z, e
    gamma = 1                  # barrier coefficient
    lam = zeros(neq)
    z = z0 * ones(niq)
    mu = z0 * ones(niq)
    k = flatnonzero(h < -z0)
    z[k] = -h[k]
    k = flatnonzero((gamma / z) > z0)
    mu[k] = gamma / z[k]
    e = ones(niq)

    # check tolerance
    f0 = f
#    if opt["step_control"]:
#        L = f + lam.T * g + mu.T * (h + z) - gamma * sum(log(z))

    Lx = df
    Lx = Lx + dg * lam if dg is not None else Lx
    Lx = Lx + dh * mu  if dh is not None else Lx

    gnorm = norm(g, Inf) if len(g) else 0.0
    lam_norm = norm(lam, Inf) if len(lam) else 0.0
    mu_norm = norm(mu, Inf) if len(mu) else 0.0
    feascond = \
        max([gnorm, max(h)]) / (1 + max([norm(x, Inf), norm(z, Inf)]))
    gradcond = \
        norm(Lx, Inf) / (1 + max([lam_norm, mu_norm]))
    compcond = dot(z, mu) / (1 + norm(x, Inf))
    costcond = absolute(f - f0) / (1 + absolute(f0))

    # save history
    hist[i] = {'feascond': feascond, 'gradcond': gradcond,
        'compcond': compcond, 'costcond': costcond, 'gamma': gamma,
        'stepsize': 0, 'obj': f / opt["cost_mult"], 'alphap': 0, 'alphad': 0}

    if opt["verbose"]:
#        s = '-sc' if opt["step_control"] else ''
#        version, date = '1.0b2', '24-Mar-2010'
#        print 'Python Interior Point Solver - PIPS%s, Version %s, %s' % \
#                    (s, version, date)
        print " it    objective   step size   feascond     gradcond     " \
              "compcond     costcond  "
        print "----  ------------ --------- ------------ ------------ " \
              "------------ ------------"
        print "%3d  %12.8g %10s %12g %12g %12g %12g" % \
            (i, (f / opt["cost_mult"]), "",
             feascond, gradcond, compcond, costcond)

    if feascond < opt["feastol"] and gradcond < opt["gradtol"] and \
        compcond < opt["comptol"] and costcond < opt["costtol"]:
        converged = True
        if opt["verbose"]:
            print "Converged!"

    # do Newton iterations
    while (not converged and i < opt["max_it"]):
        # update iteration counter
        i += 1

        # compute update step
        lmbda = {"eqnonlin": lam[range(neqnln)],
                 "ineqnonlin": mu[range(niqnln)]}
        if nonlinear:
            if hess_fcn is None:
                print "pips: Hessian evaluation via finite differences " \
                      "not yet implemented.\nPlease provide " \
                      "your own hessian evaluation function."
            Lxx = hess_fcn(x, lmbda)
        else:
            _, _, d2f = f_fcn(x)      # cost
            Lxx = d2f * opt["cost_mult"]
        rz = range(len(z))
        zinvdiag = csr_matrix((1.0 / z, (rz, rz))) if len(z) else None
        rmu = range(len(mu))
        mudiag = csr_matrix((mu, (rmu, rmu))) if len(mu) else None
        dh_zinv = None if dh is None else dh * zinvdiag
        M = Lxx if dh is None else Lxx + dh_zinv * mudiag * dh.T
        N = Lx if dh is None else Lx + dh_zinv * (mudiag * h + gamma * e)

        Ab = M if dg is None else vstack([
            hstack([M, dg]),
            hstack([dg.T, csr_matrix((neq, neq))])
        ])
        bb = r_[-N, -g]

        dxdlam = spsolve(Ab.tocsr(), bb)

        dx = dxdlam[:nx]
        dlam = dxdlam[nx:nx + neq]
        dz = -h - z if dh is None else -h - z - dh.T * dx
        dmu = -mu if dh is None else -mu + zinvdiag * (gamma * e - mudiag * dz)

        # optional step-size control
#        sc = False
        if opt["step_control"]:
            raise NotImplementedError
#            x1 = x + dx
#
#            # evaluate cost, constraints, derivatives at x1
#            f1, df1 = ipm_f(x1)          # cost
#            f1 = f1 * opt["cost_mult"]
#            df1 = df1 * opt["cost_mult"]
#            gn1, hn1, dgn1, dhn1 = ipm_gh(x1) # non-linear constraints
#            g1 = gn1 if Ai is None else r_[gn1, Ai * x1 - bi] # ieq constraints
#            h1 = hn1 if Ae is None else r_[hn1, Ae * x1 - be] # eq constraints
#            dg1 = dgn1 if Ai is None else r_[dgn1, Ai.T]      # 1st der of ieq
#            dh1 = dhn1 if Ae is None else r_[dhn1, Ae.T]      # 1st der of eqs
#
#            # check tolerance
#            Lx1 = df1 + dh1 * lam + dg1 * mu
#            feascond1 = max([ norm(h1, Inf), max(g1) ]) / \
#                (1 + max([ norm(x1, Inf), norm(z, Inf) ]))
#            gradcond1 = norm(Lx1, Inf) / \
#                (1 + max([ norm(lam, Inf), norm(mu, Inf) ]))
#
#            if feascond1 > feascond and gradcond1 > gradcond:
#                sc = True
#        if sc:
#            alpha = 1.0
#            for j in range(opt["max_red"]):
#                dx1 = alpha * dx
#                x1 = x + dx1
#                f1 = ipm_f(x1)             # cost
#                f1 = f1 * opt["cost_mult"]
#                gn1, hn1 = ipm_gh(x1)              # non-linear constraints
#                g1 = r_[gn1, Ai * x1 - bi]         # inequality constraints
#                h1 = r_[hn1, Ae * x1 - be]         # equality constraints
#                L1 = f1 + lam.H * h1 + mu.H * (g1 + z) - gamma * sum(log(z))
#                if opt["verbose"]:
#                    logger.info("\n   %3d            %10.f" % (-j, norm(dx1)))
#                rho = (L1 - L) / (Lx.H * dx1 + 0.5 * dx1.H * Lxx * dx1)
#                if rho > rho_min and rho < rho_max:
#                    break
#                else:
#                    alpha = alpha / 2.0
#            dx = alpha * dx
#            dz = alpha * dz
#            dlam = alpha * dlam
#            dmu = alpha * dmu

        # do the update
        k = flatnonzero(dz < 0.0)
        alphap = min([xi * min(z[k] / -dz[k]), 1]) if len(k) else 1.0
        k = flatnonzero(dmu < 0.0)
        alphad = min([xi * min(mu[k] / -dmu[k]), 1]) if len(k) else 1.0
        x = x + alphap * dx
        z = z + alphap * dz
        lam = lam + alphad * dlam
        mu = mu + alphad * dmu
        if niq > 0:
            gamma = sigma * dot(z, mu) / niq

        # evaluate cost, constraints, derivatives
        f, df, _ = f_fcn(x)             # cost
        f = f * opt["cost_mult"]
        df = df * opt["cost_mult"]
        if nonlinear:
            hn, gn, dhn, dgn = gh_fcn(x)                   # nln constraints
#            g = gn if Ai is None else r_[gn, Ai * x - bi] # ieq constraints
#            h = hn if Ae is None else r_[hn, Ae * x - be] # eq constraints
            h = hn if Ai is None else r_[hn, Ai * x - bi] # ieq constr
            g = gn if Ae is None else r_[gn, Ae * x - be]  # eq constr

            if (dhn is None) and (Ai is None):
                dh = None
            elif dhn is None:
                dh = Ai.T
            elif Ae is None:
                dh = dhn
            else:
                dh = hstack([dhn, Ai.T])

            if (dgn is None) and (Ae is None):
                dg = None
            elif dgn is None:
                dg = Ae.T
            elif Ae is None:
                dg = dgn
            else:
                dg = hstack([dgn, Ae.T])
        else:
            h = -bi if Ai is None else Ai * x - bi    # inequality constraints
            g = -be if Ae is None else Ae * x - be    # equality constraints
            # 1st derivatives are constant, still dh = Ai.T, dg = Ae.T

        Lx = df
        Lx = Lx + dg * lam if dg is not None else Lx
        Lx = Lx + dh * mu  if dh is not None else Lx

        gnorm = norm(g, Inf) if len(g) else 0.0
        lam_norm = norm(lam, Inf) if len(lam) else 0.0
        mu_norm = norm(mu, Inf) if len(mu) else 0.0
        feascond = \
            max([gnorm, max(h)]) / (1+max([norm(x, Inf), norm(z, Inf)]))
        gradcond = \
            norm(Lx, Inf) / (1 + max([lam_norm, mu_norm]))
        compcond = dot(z, mu) / (1 + norm(x, Inf))
        costcond = float(absolute(f - f0) / (1 + absolute(f0)))

        hist[i] = {'feascond': feascond, 'gradcond': gradcond,
            'compcond': compcond, 'costcond': costcond, 'gamma': gamma,
            'stepsize': norm(dx), 'obj': f / opt["cost_mult"],
            'alphap': alphap, 'alphad': alphad}

        if opt["verbose"]:
            print "%3d  %12.8g %10.5g %12g %12g %12g %12g" % \
                (i, (f / opt["cost_mult"]), norm(dx), feascond, gradcond,
                 compcond, costcond)

        if feascond < opt["feastol"] and gradcond < opt["gradtol"] and \
            compcond < opt["comptol"] and costcond < opt["costtol"]:
            converged = True
            if opt["verbose"]:
                print "Converged!"
        else:
            if any(isnan(x)) or (alphap < alpha_min) or \
                (alphad < alpha_min) or (gamma < EPS) or (gamma > 1.0 / EPS):
                if opt["verbose"]:
                    print "Numerically failed."
                eflag = -1
                break
            f0 = f

#            if opt["step_control"]:
#                L = f + dot(lam, g) + dot(mu * (h + z)) - gamma * sum(log(z))

    if opt["verbose"]:
        if not converged:
            print "Did not converge in %d iterations." % i

    # package results
    if eflag != -1:
        eflag = converged

    if eflag == 0:
        message = 'Did not converge'
    elif eflag == 1:
        message = 'Converged'
    elif eflag == -1:
        message = 'Numerically failed'
    else:
        raise

    output = {"iterations": i, "history": hist, "message": message}

    # zero out multipliers on non-binding constraints
    mu[flatnonzero( (h < -opt["feastol"]) & (mu < mu_threshold) )] = 0.0

    # un-scale cost and prices
    f = f / opt["cost_mult"]
    lam = lam / opt["cost_mult"]
    mu = mu / opt["cost_mult"]

    # re-package multipliers into struct
    lam_lin = lam[neqnln:neq]           # lambda for linear constraints
    mu_lin = mu[niqnln:niq]             # mu for linear constraints
    kl = flatnonzero(lam_lin < 0.0)     # lower bound binding
    ku = flatnonzero(lam_lin > 0.0)     # upper bound binding

    mu_l = zeros(nx + nA)
    mu_l[ieq[kl]] = -lam_lin[kl]
    mu_l[igt] = mu_lin[nlt:nlt + ngt]
    mu_l[ibx] = mu_lin[nlt + ngt + nbx:nlt + ngt + nbx + nbx]

    mu_u = zeros(nx + nA)
    mu_u[ieq[ku]] = lam_lin[ku]
    mu_u[ilt] = mu_lin[:nlt]
    mu_u[ibx] = mu_lin[nlt + ngt:nlt + ngt + nbx]

    lmbda = {'mu_l': mu_l[nx:], 'mu_u': mu_u[nx:],
             'lower': mu_l[:nx], 'upper': mu_u[:nx]}

    if niqnln > 0:
        lmbda['ineqnonlin'] = mu[:niqnln]
    if neqnln > 0:
        lmbda['eqnonlin'] = lam[:neqnln]

#    lmbda = {"eqnonlin": lam[:neqnln], 'ineqnonlin': mu[:niqnln],
#             "mu_l": mu_l[nx:], "mu_u": mu_u[nx:],
#             "lower": mu_l[:nx], "upper": mu_u[:nx]}

    solution =  {"x": x, "f": f, "converged": converged,
                 "lmbda": lmbda, "output": output}

    return solution

if __name__ == "__main__":
    import doctest
    doctest.testmod()
