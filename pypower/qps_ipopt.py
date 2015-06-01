# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Quadratic Program Solver based on IPOPT.
"""

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

    Uses IPOPT to solve the following QP (quadratic programming) problem::

        min 1/2 x'*H*x + c'*x
         x

    subject to::

        l <= A*x <= u       (linear constraints)
        xmin <= x <= xmax   (variable bounds)

    Inputs (all optional except C{H}, C{C}, C{A} and C{L}):
        - C{H} : matrix (possibly sparse) of quadratic cost coefficients
        - C{C} : vector of linear cost coefficients
        - C{A, l, u} : define the optional linear constraints. Default
        values for the elements of C{l} and C{u} are -Inf and Inf,
        respectively.
        - C{xmin, xmax} : optional lower and upper bounds on the
        C{x} variables, defaults are -Inf and Inf, respectively.
        - C{x0} : optional starting value of optimization vector C{x}
        - C{opt} : optional options structure with the following fields,
        all of which are also optional (default values shown in parentheses)
            - C{verbose} (0) - controls level of progress output displayed
                - 0 = no progress output
                - 1 = some progress output
                - 2 = verbose progress output
            - C{max_it} (0) - maximum number of iterations allowed
                - 0 = use algorithm default
            - C{ipopt_opt} - options struct for IPOPT, values in
            C{verbose} and C{max_it} override these options
        - C{problem} : The inputs can alternatively be supplied in a single
        C{problem} dict with fields corresponding to the input arguments
        described above: C{H, c, A, l, u, xmin, xmax, x0, opt}

    Outputs:
        - C{x} : solution vector
        - C{f} : final objective function value
        - C{exitflag} : exit flag
            - 1 = first order optimality conditions satisfied
            - 0 = maximum number of iterations reached
            - -1 = numerically failed
        - C{output} : output struct with the following fields:
            - C{iterations} - number of iterations performed
            - C{hist} - dict list with trajectories of the following:
            C{feascond}, C{gradcond}, C{compcond}, C{costcond}, C{gamma},
            C{stepsize}, C{obj}, C{alphap}, C{alphad}
            - message - exit message
        - C{lmbda} : dict containing the Langrange and Kuhn-Tucker
        multipliers on the constraints, with fields:
            - C{mu_l} - lower (left-hand) limit on linear constraints
            - C{mu_u} - upper (right-hand) limit on linear constraints
            - C{lower} - lower bound on optimization variables
            - C{upper} - upper bound on optimization variables

    Calling syntax options::
        x, f, exitflag, output, lmbda = \
            qps_ipopt(H, c, A, l, u, xmin, xmax, x0, opt)

        x = qps_ipopt(H, c, A, l, u)
        x = qps_ipopt(H, c, A, l, u, xmin, xmax)
        x = qps_ipopt(H, c, A, l, u, xmin, xmax, x0)
        x = qps_ipopt(H, c, A, l, u, xmin, xmax, x0, opt)
        x = qps_ipopt(problem), where problem is a struct with fields:
                        H, c, A, l, u, xmin, xmax, x0, opt
                        all fields except 'c', 'A' and 'l' or 'u' are optional
        x = qps_ipopt(...)
        x, f = qps_ipopt(...)
        x, f, exitflag = qps_ipopt(...)
        x, f, exitflag, output = qps_ipopt(...)
        x, f, exitflag, output, lmbda = qps_ipopt(...)

    Example::
        H = [   1003.1  4.3     6.3     5.9;
                4.3     2.2     2.1     3.9;
                6.3     2.1     3.5     4.8;
                5.9     3.9     4.8     10  ]
        c = zeros((4, 1))
        A = [   1       1       1       1
                0.17    0.11    0.10    0.18    ]
        l = [1, 0.10]
        u = [1, Inf]
        xmin = zeros((4, 1))
        x0 = [1, 0, 0, 1]
        opt = {'verbose': 2)
        x, f, s, out, lambda = qps_ipopt(H, c, A, l, u, xmin, [], x0, opt)

    Problem from U{http://www.jmu.edu/docs/sasdoc/sashtml/iml/chap8/sect12.htm}

    @see: C{pyipopt}, L{ipopt_options}

    @author: Ray Zimmerman (PSERC Cornell)
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
