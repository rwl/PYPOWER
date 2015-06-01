# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Quadratic Program Solver based on Gurobi.
"""

from sys import stderr

from numpy import Inf, ones, zeros, shape, finfo, abs
from numpy import flatnonzero as find

from scipy.sparse import issparse, csr_matrix as sparse

from pypower.gurobi_options import gurobi_options


EPS = finfo(float).eps


def qps_gurobi(H, c, A, l, u, xmin, xmax, x0, opt):
    """Quadratic Program Solver based on GUROBI.

    A wrapper function providing a PYPOWER standardized interface for using
    gurobipy to solve the following QP (quadratic programming)
    problem:

        min 1/2 x'*H*x + c'*x
         x

    subject to

        l <= A*x <= u       (linear constraints)
        xmin <= x <= xmax   (variable bounds)

    Inputs (all optional except H, c, A and l):
        H : matrix (possibly sparse) of quadratic cost coefficients
        c : vector of linear cost coefficients
        A, l, u : define the optional linear constraints. Default
            values for the elements of l and u are -Inf and Inf,
            respectively.
        xmin, xmax : optional lower and upper bounds on the
            C{x} variables, defaults are -Inf and Inf, respectively.
        x0 : optional starting value of optimization vector C{x}
        opt : optional options structure with the following fields,
            all of which are also optional (default values shown in
            parentheses)
            verbose (0) - controls level of progress output displayed
                0 = no progress output
                1 = some progress output
                2 = verbose progress output
            grb_opt - options dict for Gurobi, value in
                verbose overrides these options
        problem : The inputs can alternatively be supplied in a single
            PROBLEM dict with fields corresponding to the input arguments
            described above: H, c, A, l, u, xmin, xmax, x0, opt

    Outputs:
        x : solution vector
        f : final objective function value
        exitflag : gurobipy exit flag
            1 = converged
            0 or negative values = negative of GUROBI_MEX exit flag
            (see gurobipy documentation for details)
        output : gurobipy output dict
            (see gurobipy documentation for details)
        lmbda : dict containing the Langrange and Kuhn-Tucker
            multipliers on the constraints, with fields:
            mu_l - lower (left-hand) limit on linear constraints
            mu_u - upper (right-hand) limit on linear constraints
            lower - lower bound on optimization variables
            upper - upper bound on optimization variables

    Note the calling syntax is almost identical to that of QUADPROG
    from MathWorks' Optimization Toolbox. The main difference is that
    the linear constraints are specified with A, l, u instead of
    A, b, Aeq, beq.

    Calling syntax options:
        x, f, exitflag, output, lmbda = ...
            qps_gurobi(H, c, A, l, u, xmin, xmax, x0, opt)

        r = qps_gurobi(H, c, A, l, u)
        r = qps_gurobi(H, c, A, l, u, xmin, xmax)
        r = qps_gurobi(H, c, A, l, u, xmin, xmax, x0)
        r = qps_gurobi(H, c, A, l, u, xmin, xmax, x0, opt)
        r = qps_gurobi(problem), where problem is a dict with fields:
                        H, c, A, l, u, xmin, xmax, x0, opt
                        all fields except 'c', 'A' and 'l' or 'u' are optional

    Example: (problem from from http://www.jmu.edu/docs/sasdoc/sashtml/iml/chap8/sect12.htm)
        H = [   1003.1  4.3     6.3     5.9;
                4.3     2.2     2.1     3.9;
                6.3     2.1     3.5     4.8;
                5.9     3.9     4.8     10  ]
        c = zeros((4, 1))
        A = [   [1       1       1       1]
                [0.17    0.11    0.10    0.18]    ]
        l = [1; 0.10]
        u = [1; Inf]
        xmin = zeros((4, 1))
        x0 = [1; 0; 0; 1]
        opt = {'verbose': 2}
        x, f, s, out, lmbda = qps_gurobi(H, c, A, l, u, xmin, [], x0, opt)

    @see: L{gurobipy}.
    """
    import gurobipy

    ##----- input argument handling  -----
    ## gather inputs
    if isinstance(H, dict):       ## problem struct
        p = H
        if 'opt' in p: opt = p['opt']
        if 'x0' in p: x0 = p['x0']
        if 'xmax' in p: xmax = p['xmax']
        if 'xmin' in p: xmin = p['xmin']
        if 'u' in p: u = p['u']
        if 'l' in p: l = p['l']
        if 'A' in p: A = p['A']
        if 'c' in p: c = p['c']
        if 'H' in p: H = p['H']
    else:                         ## individual args
        assert H is not None
        assert c is not None
        assert A is not None
        assert l is not None

    if opt is None:
        opt = {}
#    if x0 is None:
#        x0 = array([])
#    if xmax is None:
#        xmax = array([])
#    if xmin is None:
#        xmin = array([])

    ## define nx, set default values for missing optional inputs
    if len(H) == 0 or not any(any(H)):
        if len(A) == 0 and len(xmin) == 0 and len(xmax) == 0:
            stderr.write('qps_gurobi: LP problem must include constraints or variable bounds\n')
        else:
            if len(A) > 0:
                nx = shape(A)[1]
            elif len(xmin) > 0:
                nx = len(xmin)
            else:    # if len(xmax) > 0
                nx = len(xmax)
        H = sparse((nx, nx))
    else:
        nx = shape(H)[0]

    if len(c) == 0:
        c = zeros(nx)

    if  len(A) > 0 and (len(l) == 0 or all(l == -Inf)) and \
                       (len(u) == 0 or all(u ==  Inf)):
        A = None                    ## no limits => no linear constraints

    nA = shape(A)[0]                ## number of original linear constraints
    if nA:
        if len(u) == 0:             ## By default, linear inequalities are ...
            u = Inf * ones(nA)      ## ... unbounded above and ...

        if len(l) == 0:
            l = -Inf * ones(nA)     ## ... unbounded below.

    if len(x0) == 0:
        x0 = zeros(nx)

    ## default options
    if 'verbose' in opt:
        verbose = opt['verbose']
    else:
        verbose = 0

#    if 'max_it' in opt:
#        max_it = opt['max_it']
#    else:
#        max_it = 0

    ## set up options struct for Gurobi
    if 'grb_opt' in opt:
        g_opt = gurobi_options(opt['grb_opt'])
    else:
        g_opt = gurobi_options()

    g_opt['Display'] = min(verbose, 3)
    if verbose:
        g_opt['DisplayInterval'] = 1
    else:
        g_opt['DisplayInterval'] = Inf

    if not issparse(A):
        A = sparse(A)

    ## split up linear constraints
    ieq = find( abs(u-l) <= EPS )          ## equality
    igt = find( u >=  1e10 & l > -1e10 )   ## greater than, unbounded above
    ilt = find( l <= -1e10 & u <  1e10 )   ## less than, unbounded below
    ibx = find( (abs(u-l) > EPS) & (u < 1e10) & (l > -1e10) )

    ## grab some dimensions
    nlt = len(ilt)      ## number of upper bounded linear inequalities
    ngt = len(igt)      ## number of lower bounded linear inequalities
    nbx = len(ibx)      ## number of doubly bounded linear inequalities
    neq = len(ieq)      ## number of equalities
    niq = nlt + ngt + 2 * nbx    ## number of inequalities

    AA  = [ A[ieq, :], A[ilt, :], -A[igt, :], A[ibx, :], -A[ibx, :] ]
    bb  = [ u[ieq],    u[ilt],    -l[igt],    u[ibx],    -l[ibx]    ]
    contypes = '=' * neq + '<' * niq

    ## call the solver
    if len(H) == 0 or not any(any(H)):
        lpqp = 'LP'
    else:
        lpqp = 'QP'
        rr, cc, vv = find(H)
        g_opt['QP']['qrow'] = int(rr.T - 1)
        g_opt['QP']['qcol'] = int(cc.T - 1)
        g_opt['QP']['qval'] = 0.5 * vv.T

    if verbose:
        methods = [
            'primal simplex',
            'dual simplex',
            'interior point',
            'concurrent',
            'deterministic concurrent'
        ]
        print('Gurobi Version %s -- %s %s solver\n'
              '<unknown>' % (methods[g_opt['Method'] + 1], lpqp))

    x, f, eflag, output, lmbda = \
        gurobipy(c.T, 1, AA, bb, contypes, xmin, xmax, 'C', g_opt)
    pi  = lmbda['Pi']
    rc  = lmbda['RC']
    output['flag'] = eflag
    if eflag == 2:
        eflag = 1          ## optimal solution found
    else:
        eflag = -eflag     ## failed somehow

    ## check for empty results (in case optimization failed)
    lam = {}
    if len(x) == 0:
        x = NaN(nx, 1);
        lam['lower']   = NaN(nx)
        lam['upper']   = NaN(nx)
    else:
        lam['lower']   = zeros(nx)
        lam['upper']   = zeros(nx)

    if len(f) == 0:
        f = NaN

    if len(pi) == 0:
        pi  = NaN(len(bb))

    kl = find(rc > 0);   ## lower bound binding
    ku = find(rc < 0);   ## upper bound binding
    lam['lower'][kl]   =  rc[kl]
    lam['upper'][ku]   = -rc[ku]
    lam['eqlin']   = pi[:neq + 1]
    lam['ineqlin'] = pi[neq + range(niq + 1)]
    mu_l        = zeros(nA)
    mu_u        = zeros(nA)

    ## repackage lmbdas
    kl = find(lam['eqlin'] > 0)   ## lower bound binding
    ku = find(lam['eqlin'] < 0)   ## upper bound binding

    mu_l[ieq[kl]] = lam['eqlin'][kl]
    mu_l[igt] = -lam['ineqlin'][nlt + range(ngt + 1)]
    mu_l[ibx] = -lam['ineqlin'][nlt + ngt + nbx + range(nbx)]

    mu_u[ieq[ku]] = -lam['eqlin'][ku]
    mu_u[ilt] = -lam['ineqlin'][:nlt + 1]
    mu_u[ibx] = -lam['ineqlin'][nlt + ngt + range(nbx + 1)]

    lmbda = {
        'mu_l': mu_l,
        'mu_u': mu_u,
        'lower': lam['lower'],
        'upper': lam['upper']
    }

    return x, f, eflag, output, lmbda
