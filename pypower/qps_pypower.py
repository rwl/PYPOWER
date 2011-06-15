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

import sys

from numpy import array

from pypower.qps_pips import qps_pips
from pypower.qps_ipopt import qps_ipopt
from pypower.qps_cplex import qps_cplex
from pypower.qps_mosek import qps_mosek


def qps_pypower(H, c=None, A=None, l=None, u=None, xmin=None, xmax=None,
                x0=None, opt=None):
    """Quadratic Program Solver for PYPOWER.

    A common wrapper function for various QP solvers.
    Solves the following QP (quadratic programming) problem:

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
            alg (0) - determines which solver to use
                  0 = automatic, first available of BPMPD_MEX, CPLEX, MIPS
                100 = BPMPD_MEX
                200 = MIPS, MATLAB Interior Point Solver
                      pure MATLAB implementation of a primal-dual
                      interior point method
                250 = MIPS-sc, a step controlled variant of MIPS
                300 = Optimization Toolbox, QUADPROG or LINPROG
                400 = IPOPT
                500 = CPLEX
                600 = MOSEK
            verbose (0) - controls level of progress output displayed
                0 = no progress output
                1 = some progress output
                2 = verbose progress output
            max_it (0) - maximum number of iterations allowed
                0 = use algorithm default
            bp_opt - options vector for BP
            cplex_opt - options struct for CPLEX
            ipopt_opt - options struct for IPOPT
            pips_opt - options struct for QPS_MIPS
            mosek_opt - options struct for MOSEK
            ot_opt - options struct for QUADPROG/LINPROG
        PROBLEM : The inputs can alternatively be supplied in a single
            PROBLEM struct with fields corresponding to the input arguments
            described above: H, c, A, l, u, xmin, xmax, x0, opt

    Outputs:
        X : solution vector
        F : final objective function value
        EXITFLAG : exit flag
            1 = converged
            0 or negative values = algorithm specific failure codes
        OUTPUT : output struct with the following fields:
            alg - algorithm code of solver used
            (others) - algorithm specific fields
        LAMBDA : struct containing the Langrange and Kuhn-Tucker
            multipliers on the constraints, with fields:
            mu_l - lower (left-hand) limit on linear constraints
            mu_u - upper (right-hand) limit on linear constraints
            lower - lower bound on optimization variables
            upper - upper bound on optimization variables


    Example from U{http://www.uc.edu/sashtml/iml/chap8/sect12.htm}:

        >>> from numpy import array, zeros, Inf
        >>> from scipy.sparse import csr_matrix
        >>> H = csr_matrix(array([[1003.1,  4.3,     6.3,     5.9],
        ...                       [4.3,     2.2,     2.1,     3.9],
        ...                       [6.3,     2.1,     3.5,     4.8],
        ...                       [5.9,     3.9,     4.8,     10 ]]))
        >>> c = zeros(4)
        >>> A = csr_matrix(array([[1,       1,       1,       1   ],
        ...                       [0.17,    0.11,    0.10,    0.18]]))
        >>> l = array([1, 0.10])
        >>> u = array([1, Inf])
        >>> xmin = zeros(4)
        >>> xmax = None
        >>> x0 = array([1, 0, 0, 1])
        >>> solution = qps_pips(H, c, A, l, u, xmin, xmax, x0)
        >>> round(solution["f"], 11) == 1.09666678128
        True
        >>> solution["converged"]
        True
        >>> solution["output"]["iterations"]
        10

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
#        assert H is not None  zero dimensional sparse matrices not supported
        assert c is not None
#        assert A is not None  zero dimensional sparse matrices not supported
#        assert l is not None  no lower bounds indicated by None

    if opt is None:
        opt = {}
#    if x0 is None:
#        x0 = array([])
#    if xmax is None:
#        xmax = array([])
#    if xmin is None:
#        xmin = array([])

    ## default options
    if 'alg' in opt:
        alg = opt['alg']
    else:
        alg = 0

    if 'verbose' in opt:
        verbose = opt['verbose']
    else:
        verbose = 0

    if alg == 0:
        try:
            import pymosek          #@UnusedImport
            alg = 600               ## use MOSEK by default if available
        except ImportError:
            try:
                import cplex        #@UnusedImport
                alg = 500           ## if not, then CPLEX if available
            except ImportError:
                alg = 200           ## otherwise PIPS


    ##----- call the appropriate solver  -----
    if alg == 200 or alg == 250:    ## use MIPS or sc-MIPS
        ## set up options
        if 'pips_opt' in opt:
            pips_opt = opt['pips_opt']
        else:
            pips_opt = {}

        if 'max_it' in opt:
            pips_opt['max_it'] = opt['max_it']

        if alg == 200:
            pips_opt['step_control'] = False
        else:
            pips_opt['step_control'] = True

        pips_opt['verbose'] = verbose

        ## call solver
        x, f, eflag, output, lmbda = \
            qps_pips(H, c, A, l, u, xmin, xmax, x0, pips_opt)
    elif alg == 400:                    ## use IPOPT
        x, f, eflag, output, lmbda = \
            qps_ipopt(H, c, A, l, u, xmin, xmax, x0, opt)
    elif alg == 500:                    ## use CPLEX
        x, f, eflag, output, lmbda = \
            qps_cplex(H, c, A, l, u, xmin, xmax, x0, opt)
    elif alg == 600:                    ## use MOSEK
        x, f, eflag, output, lmbda = \
            qps_mosek(H, c, A, l, u, xmin, xmax, x0, opt)
    else:
        sys.stderr.write('qps_pypower: %d is not a valid algorithm code\n', alg)

    if 'alg' not in output:
        output['alg'] = alg

    return x, f, eflag, output, lmbda


if __name__ == "__main__":
    import doctest
    doctest.testmod()
