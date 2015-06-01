# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Quadratic Program Solver based on CPLEX.
"""

import re

from sys import stdout, stderr

from numpy import array, NaN, Inf, ones, zeros, shape, finfo, arange, r_
from numpy import flatnonzero as find

from scipy.sparse import csr_matrix as sparse

try:
    from cplex import Cplex, cplexlp, cplexqp
except ImportError:
#    print 'CPLEX not available'
    pass

from pypower.cplex_options import cplex_options


EPS = finfo(float).eps


def qps_cplex(H, c, A, l, u, xmin, xmax, x0, opt):
    """Quadratic Program Solver based on CPLEX.

    A wrapper function providing a PYPOWER standardized interface for using
    C{cplexqp} or C{cplexlp} to solve the following QP (quadratic programming)
    problem::

        min 1/2 X'*H*x + c'*x
         x

    subject to::

        l <= A*x <= u       (linear constraints)
        xmin <= x <= xmax   (variable bounds)

    Inputs (all optional except C{H}, C{c}, C{A} and C{l}):
        - C{H} : matrix (possibly sparse) of quadratic cost coefficients
        - C{c} : vector of linear cost coefficients
        - C{A, l, u} : define the optional linear constraints. Default
        values for the elements of L and U are -Inf and Inf, respectively.
        - C{xmin, xmax} : optional lower and upper bounds on the
        C{x} variables, defaults are -Inf and Inf, respectively.
        - C{x0} : optional starting value of optimization vector C{x}
        - C{opt} : optional options structure with the following fields,
        all of which are also optional (default values shown in parentheses)
            - C{verbose} (0) - controls level of progress output displayed
                - 0 = no progress output
                - 1 = some progress output
                - 2 = verbose progress output
            - C{cplex_opt} - options dict for CPLEX, value in
            verbose overrides these options
        - C{problem} : The inputs can alternatively be supplied in a single
        C{problem} dict with fields corresponding to the input arguments
        described above: C{H, c, A, l, u, xmin, xmax, x0, opt}

    Outputs:
        - C{x} : solution vector
        - C{f} : final objective function value
        - C{exitflag} : CPLEXQP/CPLEXLP exit flag
        (see C{cplexqp} and C{cplexlp} documentation for details)
        - C{output} : CPLEXQP/CPLEXLP output dict
        (see C{cplexqp} and C{cplexlp} documentation for details)
        - C{lmbda} : dict containing the Langrange and Kuhn-Tucker
        multipliers on the constraints, with fields:
            - mu_l - lower (left-hand) limit on linear constraints
            - mu_u - upper (right-hand) limit on linear constraints
            - lower - lower bound on optimization variables
            - upper - upper bound on optimization variables

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
            stderr.write('qps_cplex: LP problem must include constraints or variable bounds\n')
        else:
            if len(A) > 0:
                nx = shape(A)[1]
            elif len(xmin) > 0:
                nx = len(xmin)
            else:    # if len(xmax) > 0
                nx = len(xmax)
    else:
        nx = shape(H)[0]

    if len(c) == 0:
        c = zeros(nx)

    if  len(A) > 0 and (len(l) == 0 or all(l == -Inf)) and \
                       (len(u) == 0 or all(u ==  Inf)):
        A = None                    ## no limits => no linear constraints

    nA = shape(A)[0]                ## number of original linear constraints
    if len(u) == 0:                 ## By default, linear inequalities are ...
        u = Inf * ones(nA)          ## ... unbounded above and ...

    if len(l) == 0:
        l = -Inf * ones(nA)         ## ... unbounded below.

    if len(xmin) == 0:              ## By default, optimization variables are ...
        xmin = -Inf * ones(nx)      ## ... unbounded below and ...

    if len(xmax) == 0:
        xmax = Inf * ones(nx)       ## ... unbounded above.

    if len(x0) == 0:
        x0 = zeros(nx)

    ## default options
    if 'verbose' in opt:
        verbose = opt['verbose']
    else:
        verbose = 0

    #if 'max_it' in opt:
    #    max_it = opt['max_it']
    #else:
    #    max_it = 0

    ## split up linear constraints
    ieq = find( abs(u-l) <= EPS )           ## equality
    igt = find( u >=  1e10 & l > -1e10 )    ## greater than, unbounded above
    ilt = find( l <= -1e10 & u <  1e10 )    ## less than, unbounded below
    ibx = find( (abs(u-l) > EPS) & (u < 1e10) & (l > -1e10) )
    Ae = A[ieq, :]
    be = u[ieq]
    Ai  = r_[ A[ilt, :], -A[igt, :], A[ibx, :] -A[ibx, :] ]
    bi  = r_[ u[ilt],    -l[igt],    u[ibx],   -l[ibx]    ]

    ## grab some dimensions
    nlt = len(ilt)      ## number of upper bounded linear inequalities
    ngt = len(igt)      ## number of lower bounded linear inequalities
    nbx = len(ibx)      ## number of doubly bounded linear inequalities

    ## set up options struct for CPLEX
    if 'cplex_opt' in opt:
        cplex_opt = cplex_options(opt['cplex_opt'])
    else:
        cplex_opt = cplex_options


    cplex = Cplex('null')
    vstr = cplex.getVersion
    s, e, tE, m, t = re.compile(vstr, '(\d+\.\d+)\.')
    vnum = int(t[0][0])
    vrb = max([0, verbose - 1])
    cplex_opt['barrier']['display']   = vrb
    cplex_opt['conflict']['display']  = vrb
    cplex_opt['mip']['display']       = vrb
    cplex_opt['sifting']['display']   = vrb
    cplex_opt['simplex']['display']   = vrb
    cplex_opt['tune']['display']      = vrb
    if vrb and (vnum > 12.2):
        cplex_opt['diagnostics']   = 'on'
    #if max_it:
    #    cplex_opt.    ## not sure what to set here

    if len(Ai) == 0 and len(Ae) == 0:
        unconstrained = 1
        Ae = sparse((1, nx))
        be = 0
    else:
        unconstrained = 0

    ## call the solver
    if verbose:
        methods = [
            'default',
            'primal simplex',
            'dual simplex',
            'network simplex',
            'barrier',
            'sifting',
            'concurrent'
        ]

    if len(H) == 0 or not any(any(H)):
        if verbose:
            stdout.write('CPLEX Version %s -- %s LP solver\n' %
                (vstr, methods[cplex_opt['lpmethod'] + 1]))

        x, f, eflag, output, lam = \
            cplexlp(c, Ai, bi, Ae, be, xmin, xmax, x0, cplex_opt)
    else:
        if verbose:
            stdout.write('CPLEX Version %s --  %s QP solver\n' %
                (vstr, methods[cplex_opt['qpmethod'] + 1]))
        ## ensure H is numerically symmetric
        if H != H.T:
            H = (H + H.T) / 2

        x, f, eflag, output, lam = \
            cplexqp(H, c, Ai, bi, Ae, be, xmin, xmax, x0, cplex_opt)


    ## check for empty results (in case optimization failed)
    if len(x) == 0:
        x = NaN * zeros(nx)

    if len(f) == 0:
        f = NaN

    if len(lam) == 0:
        lam['ineqlin'] = NaN * zeros(len(bi))
        lam['eqlin']   = NaN * zeros(len(be))
        lam['lower']   = NaN * zeros(nx)
        lam['upper']   = NaN * zeros(nx)
        mu_l        = NaN * zeros(nA)
        mu_u        = NaN * zeros(nA)
    else:
        mu_l        = zeros(nA)
        mu_u        = zeros(nA)

    if unconstrained:
        lam['eqlin'] = array([])

    ## negate prices depending on version
    if vnum < 12.3:
        lam['eqlin']   = -lam['eqlin']
        lam['ineqlin'] = -lam['ineqlin']

    ## repackage lambdas
    kl = find(lam.eqlin < 0)   ## lower bound binding
    ku = find(lam.eqlin > 0)   ## upper bound binding

    mu_l[ieq[kl]] = -lam['eqlin'][kl]
    mu_l[igt] = lam['ineqlin'][nlt + arange(ngt)]
    mu_l[ibx] = lam['ineqlin'][nlt + ngt + nbx + arange(nbx)]

    mu_u[ieq[ku]] = lam['eqlin'][ku]
    mu_u[ilt] = lam['ineqlin'][:nlt]
    mu_u[ibx] = lam['ineqlin'][nlt + ngt + arange(nbx)]

    lmbda = {
        'mu_l': mu_l,
        'mu_u': mu_u,
        'lower': lam.lower,
        'upper': lam.upper
    }

    return x, f, eflag, output, lmbda
