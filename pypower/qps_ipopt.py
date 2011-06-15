# Copyright (C) 2010-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY], without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

from sys import stderr

from numpy import Inf, ones, zeros, shape, tril
from numpy import flatnonzero as find

from scipy.sparse import issparse, csr_matrix as sparse

try:
    import pyipopt
except ImportError:
#    print 'IPOPT not available'
    pass

from pypower.ipopt_options import ipopt_options

def qps_ipopt(H, c, A, l, u, xmin, xmax, x0, opt):
    """Quadratic Program Solver based on IPOPT.

    Uses IPOPT to solve the following QP (quadratic programming) problem:

        min 1/2 X'*H*X + C'*X
         X

    subject to

        L <= A*X <= U       (linear constraints)
        XMIN <= X <= XMAX   (variable bounds)

    Inputs (all optional except H, C, A and L):
        H : matrix (possibly sparse) of quadratic cost coefficients
        C : vector of linear cost coefficients
        A, L, U : define the optional linear constraints. Default
            values for the elements of L and U are -Inf and Inf,
            respectively.
        XMIN, XMAX : optional lower and upper bounds on the
            X variables, defaults are -Inf and Inf, respectively.
        X0 : optional starting value of optimization vector X
        OPT : optional options structure with the following fields,
            all of which are also optional (default values shown in
            parentheses)
            verbose (0) - controls level of progress output displayed
                0 = no progress output
                1 = some progress output
                2 = verbose progress output
            max_it (0) - maximum number of iterations allowed
                0 = use algorithm default
            ipopt_opt - options struct for IPOPT, values in
                verbose and max_it override these options
        PROBLEM : The inputs can alternatively be supplied in a single
            PROBLEM struct with fields corresponding to the input arguments
            described above: H, c, A, l, u, xmin, xmax, x0, opt

    Outputs:
        X : solution vector
        F : final objective function value
        EXITFLAG : exit flag
            1 = first order optimality conditions satisfied
            0 = maximum number of iterations reached
            -1 = numerically failed
        OUTPUT : output struct with the following fields:
            iterations - number of iterations performed
            hist - struct array with trajectories of the following:
                    feascond, gradcond, compcond, costcond, gamma,
                    stepsize, obj, alphap, alphad
            message - exit message
        lmbda : struct containing the Langrange and Kuhn-Tucker
            multipliers on the constraints, with fields:
            mu_l - lower (left-hand) limit on linear constraints
            mu_u - upper (right-hand) limit on linear constraints
            lower - lower bound on optimization variables
            upper - upper bound on optimization variables

    Note the calling syntax is almost identical to that of QUADPROG
    from MathWorks' Optimization Toolbox. The main difference is that
    the linear constraints are specified with A, L, U instead of
    A, B, Aeq, Beq.

    Calling syntax options:
        [x, f, exitflag, output, lmbda] = ...
            qps_ipopt(H, c, A, l, u, xmin, xmax, x0, opt)

        x = qps_ipopt(H, c, A, l, u)
        x = qps_ipopt(H, c, A, l, u, xmin, xmax)
        x = qps_ipopt(H, c, A, l, u, xmin, xmax, x0)
        x = qps_ipopt(H, c, A, l, u, xmin, xmax, x0, opt)
        x = qps_ipopt(problem), where problem is a struct with fields:
                        H, c, A, l, u, xmin, xmax, x0, opt
                        all fields except 'c', 'A' and 'l' or 'u' are optional
        x = qps_ipopt(...)
        [x, f] = qps_ipopt(...)
        [x, f, exitflag] = qps_ipopt(...)
        [x, f, exitflag, output] = qps_ipopt(...)
        [x, f, exitflag, output, lmbda] = qps_ipopt(...)

    Example: (problem from from http://www.jmu.edu/docs/sasdoc/sashtml/iml/chap8/sect12.htm)
        H = [   1003.1  4.3     6.3     5.9;
                4.3     2.2     2.1     3.9;
                6.3     2.1     3.5     4.8;
                5.9     3.9     4.8     10  ];
        c = zeros(4,1);
        A = [   1       1       1       1;
                0.17    0.11    0.10    0.18    ];
        l = [1; 0.10];
        u = [1; Inf];
        xmin = zeros(4,1);
        x0 = [1; 0; 0; 1];
        opt = struct('verbose', 2);
        [x, f, s, out, lam] = qps_ipopt(H, c, A, l, u, xmin, [], x0, opt);

    @see: C{pyipopt}, C{pyipopt_options}

    @see: U{https://projects.coin-or.org/Ipopt/}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
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
            stderr.write('qps_ipopt: LP problem must include constraints or variable bounds\n')
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

    if 'max_it' in opt:
        max_it = opt['max_it']
    else:
        max_it = 0

    ## make sure args are sparse/full as expected by IPOPT
    if len(H) > 0:
        if not issparse(H):
            H = sparse(H)

    if not issparse(A):
        A = sparse(A)

    ##-----  run optimization  -----
    ## set options dict for IPOPT
    options = {}
    if 'ipopt_opt' in opt:
        options['ipopt'] = ipopt_options(opt['ipopt_opt'])
    else:
        options['ipopt'] = ipopt_options()

    options['ipopt']['jac_c_constant']    = 'yes'
    options['ipopt']['jac_d_constant']    = 'yes'
    options['ipopt']['hessian_constant']  = 'yes'
    options['ipopt']['least_square_init_primal']  = 'yes'
    options['ipopt']['least_square_init_duals']   = 'yes'
    # options['ipopt']['mehrotra_algorithm']        = 'yes'     ## default 'no'
    if verbose:
        options['ipopt']['print_level'] = min(12, verbose * 2 + 1)
    else:
        options['ipopt']['print_level = 0']

    if max_it:
        options['ipopt']['max_iter'] = max_it

    ## define variable and constraint bounds, if given
    if nA:
        options['cu'] = u
        options['cl'] = l

    if len(xmin) > 0:
        options['lb'] = xmin

    if len(xmax) > 0:
        options['ub'] = xmax

    ## assign function handles
    funcs = {}
    funcs['objective']         = lambda x: 0.5 * x.T * H * x + c.T * x
    funcs['gradient']          = lambda x: H * x + c
    funcs['constraints']       = lambda x: A * x
    funcs['jacobian']          = lambda x: A
    funcs['jacobianstructure'] = lambda : A
    funcs['hessian']           = lambda x, sigma, lmbda: tril(H)
    funcs['hessianstructure']  = lambda : tril(H)

    ## run the optimization
    x, info = pyipopt(x0, funcs, options)

    if info['status'] == 0 | info['status'] == 1:
        eflag = 1
    else:
        eflag = 0

    output = {}
    if 'iter' in info:
        output['iterations'] = info['iter']

    output['info']       = info['status']
    f = funcs['objective'](x)

    ## repackage lmbdas
    kl = find(info['lmbda'] < 0)                     ## lower bound binding
    ku = find(info['lmbda'] > 0)                     ## upper bound binding
    mu_l = zeros(nA)
    mu_l[kl] = -info['lmbda'][kl]
    mu_u = zeros(nA)
    mu_u[ku] = info['lmbda'][ku]

    lmbda = {
        'mu_l': mu_l,
        'mu_u': mu_u,
        'lower': info['zl'],
        'upper': info['zu']
    }

    return x, f, eflag, output, lmbda
