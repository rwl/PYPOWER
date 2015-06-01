# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests of C{qps_pypower} QP solvers.
"""

from numpy import array, zeros, shape, Inf

from scipy.sparse import csr_matrix as sparse

from pypower.ppoption import ppoption
from pypower.cplex_options import cplex_options
from pypower.mosek_options import mosek_options
from pypower.qps_pypower import qps_pypower
from pypower.util import have_fcn

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end
from pypower.t.t_ok import t_ok
from pypower.t.t_skip import t_skip


def t_qps_pypower(quiet=False):
    """Tests of C{qps_pypower} QP solvers.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    algs = [200, 250, 400, 500, 600, 700]
    names = ['PIPS', 'sc-PIPS', 'IPOPT', 'CPLEX', 'MOSEK', 'Gurobi']
    check = [None, None, 'ipopt', 'cplex', 'mosek', 'gurobipy']

    n = 36
    t_begin(n * len(algs), quiet)

    for k in range(len(algs)):
        if check[k] is not None and not have_fcn(check[k]):
            t_skip(n, '%s not installed' % names[k])
        else:
            opt = {'verbose': 0, 'alg': algs[k]}

            if names[k] == 'PIPS' or names[k] == 'sc-PIPS':
                opt['pips_opt'] = {}
                opt['pips_opt']['comptol'] = 1e-8
            if names[k] == 'CPLEX':
#               alg = 0        ## default uses barrier method with NaN bug in lower lim multipliers
                alg = 2        ## use dual simplex
                ppopt = ppoption(CPLEX_LPMETHOD = alg, CPLEX_QPMETHOD = min([4, alg]))
                opt['cplex_opt'] = cplex_options([], ppopt)

            if names[k] == 'MOSEK':
#                alg = 5        ## use dual simplex
                ppopt = ppoption()
#                ppopt = ppoption(ppopt, MOSEK_LP_ALG = alg)
                ppopt = ppoption(ppopt, MOSEK_GAP_TOL=1e-9)
                opt['mosek_opt'] = mosek_options([], ppopt)

            t = '%s - 3-d LP : ' % names[k]
            ## example from 'doc linprog'
            c = array([-5, -4, -6], float)
            A = sparse([[1, -1,  1],
                        [3,  2,  4],
                        [3,  2,  0]], dtype=float)
            l = None
            u = array([20, 42, 30], float)
            xmin = array([0, 0, 0], float)
            x0 = None
            x, f, s, _, lam = qps_pypower(None, c, A, l, u, xmin, None, None, opt)
            t_is(s, 1, 12, [t, 'success'])
            t_is(x, [0, 15, 3], 6, [t, 'x'])
            t_is(f, -78, 6, [t, 'f'])
            t_is(lam['mu_l'], [0, 0, 0], 13, [t, 'lam.mu_l'])
            t_is(lam['mu_u'], [0, 1.5, 0.5], 9, [t, 'lam.mu_u'])
            t_is(lam['lower'], [1, 0, 0], 9, [t, 'lam.lower'])
            t_is(lam['upper'], zeros(shape(x)), 13, [t, 'lam.upper'])

            t = '%s - unconstrained 3-d quadratic : ' % names[k]
            ## from http://www.akiti.ca/QuadProgEx0Constr.html
            H = sparse([
                [ 5, -2, -1],
                [-2,  4,  3],
                [-1,  3,  5]
            ], dtype=float)
            c = array([2, -35, -47], float)
            x0 = array([0, 0, 0], float)
            x, f, s, _, lam = qps_pypower(H, c, opt=opt)
            t_is(s, 1, 12, [t, 'success'])
            t_is(x, [3, 5, 7], 8, [t, 'x'])
            t_is(f, -249, 13, [t, 'f'])
            t_ok(len(lam['mu_l']) == 0, [t, 'lam.mu_l'])
            t_ok(len(lam['mu_u']) == 0, [t, 'lam.mu_u'])
            t_is(lam['lower'], zeros(shape(x)), 13, [t, 'lam.lower'])
            t_is(lam['upper'], zeros(shape(x)), 13, [t, 'lam.upper'])

            t = '%s - constrained 2-d QP : ' % names[k]
            ## example from 'doc quadprog'
            H = sparse([[ 1, -1],
                        [-1,  2]], dtype=float)
            c = array([-2, -6], float)
            A = sparse([[ 1, 1],
                        [-1, 2],
                        [ 2, 1]], dtype=float)
            l = None
            u = array([2, 2, 3], float)
            xmin = array([0, 0])
            x0 = None
            x, f, s, _, lam = qps_pypower(H, c, A, l, u, xmin, None, x0, opt)
            t_is(s, 1, 12, [t, 'success'])
            t_is(x, array([2., 4.]) / 3, 7, [t, 'x'])
            t_is(f, -74. / 9, 6, [t, 'f'])
            t_is(lam['mu_l'], [0., 0., 0.], 13, [t, 'lam.mu_l'])
            t_is(lam['mu_u'], array([28., 4., 0.]) / 9, 7, [t, 'lam.mu_u'])
            t_is(lam['lower'], zeros(shape(x)), 8, [t, 'lam.lower'])
            t_is(lam['upper'], zeros(shape(x)), 13, [t, 'lam.upper'])

            t = '%s - constrained 4-d QP : ' % names[k]
            ## from http://www.jmu.edu/docs/sasdoc/sashtml/iml/chap8/sect12.htm
            H = sparse([[1003.1,  4.3,     6.3,     5.9],
                        [4.3,     2.2,     2.1,     3.9],
                        [6.3,     2.1,     3.5,     4.8],
                        [5.9,     3.9,     4.8,    10.0]])
            c = zeros(4)
            A = sparse([[   1,       1,       1,       1],
                        [0.17,    0.11,    0.10,    0.18]])
            l = array([1, 0.10])
            u = array([1, Inf])
            xmin = zeros(4)
            x0 = array([1, 0, 0, 1], float)
            x, f, s, _, lam = qps_pypower(H, c, A, l, u, xmin, None, x0, opt)
            t_is(s, 1, 12, [t, 'success'])
            t_is(x, array([0, 2.8, 0.2, 0]) / 3, 5, [t, 'x'])
            t_is(f, 3.29 / 3, 6, [t, 'f'])
            t_is(lam['mu_l'], array([6.58, 0]) / 3, 6, [t, 'lam.mu_l'])
            t_is(lam['mu_u'], [0, 0], 13, [t, 'lam.mu_u'])
            t_is(lam['lower'], [2.24, 0, 0, 1.7667], 4, [t, 'lam.lower'])
            t_is(lam['upper'], zeros(shape(x)), 13, [t, 'lam.upper'])

            t = '%s - (dict) constrained 4-d QP : ' % names[k]
            p = {'H': H, 'A': A, 'l': l, 'u': u, 'xmin': xmin, 'x0': x0, 'opt': opt}
            x, f, s, _, lam = qps_pypower(p)
            t_is(s, 1, 12, [t, 'success'])
            t_is(x, array([0, 2.8, 0.2, 0]) / 3, 5, [t, 'x'])
            t_is(f, 3.29 / 3, 6, [t, 'f'])
            t_is(lam['mu_l'], array([6.58, 0]) / 3, 6, [t, 'lam.mu_l'])
            t_is(lam['mu_u'], [0, 0], 13, [t, 'lam.mu_u'])
            t_is(lam['lower'], [2.24, 0, 0, 1.7667], 4, [t, 'lam.lower'])
            t_is(lam['upper'], zeros(shape(x)), 13, [t, 'lam.upper'])

            t = '%s - infeasible LP : ' % names[k]
            p = {'A': sparse([1, 1]), 'c': array([1, 1]), 'u': array([-1]),
                 'xmin': array([0, 0]), 'opt': opt}
            x, f, s, _, lam = qps_pypower(p)
            t_ok(s <= 0, [t, 'no success'])

    t_end()


if __name__ == '__main__':
    t_qps_pypower(quiet=False)
