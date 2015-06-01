# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests of PIPS NLP solver.
"""

from math import sqrt

from numpy import zeros, ones, array, eye, prod, dot, asscalar, Inf

from scipy.sparse import csr_matrix as sparse
from scipy.sparse import eye as speye

from pypower.pips import pips

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end
from pypower.t.t_ok import t_ok


## unconstrained banana function
## from MATLAB Optimization Toolbox's bandem.m
def f2(x, return_hessian=False):
    a = 100
    f = a * (x[1] - x[0]**2)**2 + (1 - x[0])**2
    df = array([
        4 * a * (x[0]**3 - x[0] * x[1]) + 2 * x[0] - 2,
        2 * a * (x[1] - x[0]**2)
    ])

    if not return_hessian:
        return f, df

    d2f = 4 * a * sparse([
        [3 * x[0]**2 - x[1] + 1. / (2 * a), -x[0]],
        [                           -x[0],   0.5]
    ])
    return f, df, d2f


## unconstrained 3-d quadratic
## from http://www.akiti.ca/QuadProgEx0Constr.html
def f3(x, return_hessian=False):
    H = sparse([
        [ 5, -2, -1],
        [-2,  4,  3],
        [-1,  3,  5]
    ], dtype=float)
    c = array([2, -35, -47], float)
    f = 0.5 * dot(x * H, x) + dot(c, x) + 5
    df = H * x + c
    if not return_hessian:
        return f, df
    d2f = H
    return f, df, d2f


## constrained 4-d QP
## from http://www.jmu.edu/docs/sasdoc/sashtml/iml/chap8/sect12.htm
def f4(x, return_hessian=False):
    H = sparse([
        [1003.1, 4.3, 6.3,  5.9],
        [   4.3, 2.2, 2.1,  3.9],
        [   6.3, 2.1, 3.5,  4.8],
        [   5.9, 3.9, 4.8, 10.0]
    ])
    c = zeros(4)
    f = 0.5 * dot(x * H, x) + dot(c, x)
    df = H * x + c
    if not return_hessian:
        return f, df
    d2f = H
    return f, df, d2f


## constrained 2-d nonlinear
## from http://en.wikipedia.org/wiki/Nonlinear_programming#2-dimensional_example
def f5(x, return_hessian=False):
    c = -array([1.0, 1.0])
    f = dot(c, x)
    df = c
    if not return_hessian:
        return f, df
    d2f = sparse((2, 2))
    return f, df, d2f

def gh5(x):
    h = dot([[-1.0, -1.0],
             [ 1.0,  1.0]], x**2) + [1, -2]
    dh = 2 * sparse([[-x[0], x[0]],
                     [-x[1], x[1]]])
    g = array([])
    dg = None
    return h, g, dh, dg

def hess5(x, lam, cost_mult):
    mu = lam['ineqnonlin']
    Lxx = 2 * dot([-1.0, 1.0], mu) * eye(2)
    return Lxx


## constrained 3-d nonlinear
## from http://en.wikipedia.org/wiki/Nonlinear_programming#3-dimensional_example
def f6(x, return_hessian=False):
    f = -x[0] * x[1] - x[1] * x[2]
    df = -array([x[1], x[0] + x[2], x[1]])
    if not return_hessian:
        return f, df
    d2f = -sparse([[0, 1, 0],
                   [1, 0, 1],
                   [0, 1, 0]], dtype=float)
    return f, df, d2f

def gh6(x):
    h = dot([[1.0, -1.0, 1.0],
             [1.0,  1.0, 1.0]], x**2) + [-2.0, -10.0]
    dh = 2 * sparse([[ x[0], x[0]],
                     [-x[1], x[1]],
                     [ x[2], x[2]]], dtype=float)
    g = array([])
    dg = None
    return h, g, dh, dg

def hess6(x, lam, cost_mult=1):
    mu = lam['ineqnonlin']
    Lxx = cost_mult * \
        sparse([[ 0, -1,  0],
                [-1,  0, -1],
                [ 0, -1,  0]], dtype=float) + \
        sparse([[2 * dot([1, 1], mu),  0, 0],
                [0, 2 * dot([-1, 1], mu), 0],
                [0, 0,  2 * dot([1, 1], mu)]], dtype=float)
    return Lxx


## constrained 4-d nonlinear
## Hock & Schittkowski test problem #71
def f7(x, return_hessian=False):
    f = x[0] * x[3] * sum(x[:3]) + x[2]
    df = array([ x[0] * x[3] + x[3] * sum(x[:3]),
                 x[0] * x[3],
                 x[0] * x[3] + 1,
                 x[0] * sum(x[:3]) ])
    if not return_hessian:
        return f, df
    d2f = sparse([
        [2 * x[3],               x[3], x[3], 2 * x[0] + x[1] + x[2]],
        [                  x[3],  0.0,  0.0,                   x[0]],
        [                  x[3],  0.0,  0.0,                   x[0]],
        [2 * x[0] + x[1] + x[2], x[0], x[0],                    0.0]
    ])
    return f, df, d2f

def gh7(x):
    g = array( [sum(x**2) - 40.0] )
    h = array( [ -prod(x) + 25.0] )
    dg = sparse( 2 * x ).T
    dh = sparse( -prod(x) / x ).T
    return h, g, dh, dg

def hess7(x, lam, sigma=1):
    lmbda = asscalar( lam['eqnonlin'] )
    mu    = asscalar( lam['ineqnonlin'] )
    _, _, d2f = f7(x, True)

    Lxx = sigma * d2f + lmbda * 2 * speye(4, 4) - \
        mu * sparse([
            [        0.0, x[2] * x[3], x[2] * x[3], x[1] * x[2]],
            [x[2] * x[2],         0.0, x[0] * x[3], x[0] * x[2]],
            [x[1] * x[3], x[0] * x[3],         0.0, x[0] * x[1]],
            [x[1] * x[2], x[0] * x[2], x[0] * x[1],         0.0]
        ])
    return Lxx


def t_pips(quiet=False):
    """Tests of pips NLP solver.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    t_begin(60, quiet)

    t = 'unconstrained banana function : '
    ## from MATLAB Optimization Toolbox's bandem.m
    f_fcn = f2
    x0 = array([-1.9, 2])
    # solution = pips(f_fcn, x0, opt={'verbose': 2})
    solution = pips(f_fcn, x0)
    x, f, s, lam, out = solution["x"], solution["f"], solution["eflag"], \
            solution["lmbda"], solution["output"]
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, [1, 1], 13, [t, 'x'])
    t_is(f, 0, 13, [t, 'f'])
    t_is(out['hist'][-1]['compcond'], 0, 6, [t, 'compcond'])
    t_ok(len(lam['mu_l']) == 0, [t, 'lam.mu_l'])
    t_ok(len(lam['mu_u']) == 0, [t, 'lam.mu_u'])
    t_is(lam['lower'], zeros(x.shape), 13, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 13, [t, 'lam[\'upper\']'])

    t = 'unconstrained 3-d quadratic : '
    ## from http://www.akiti.ca/QuadProgEx0Constr.html
    f_fcn = f3
    x0 = array([0, 0, 0], float)
    # solution = pips(f_fcn, x0, opt={'verbose': 2})
    solution = pips(f_fcn, x0)
    x, f, s, lam, out = solution["x"], solution["f"], solution["eflag"], \
            solution["lmbda"], solution["output"]
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, [3, 5, 7], 13, [t, 'x'])
    t_is(f, -244, 13, [t, 'f'])
    t_is(out['hist'][-1]['compcond'], 0, 6, [t, 'compcond'])
    t_ok(len(lam['mu_l']) == 0, [t, 'lam.mu_l'])
    t_ok(len(lam['mu_u']) == 0, [t, 'lam.mu_u'])
    t_is(lam['lower'], zeros(x.shape), 13, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 13, [t, 'lam[\'upper\']'])

    t = 'constrained 4-d QP : '
    ## from http://www.jmu.edu/docs/sasdoc/sashtml/iml/chap8/sect12.htm
    f_fcn = f4
    x0 = array([1.0, 0.0, 0.0, 1.0])
    A = array([
        [1.0,  1.0,  1.0,  1.0 ],
        [0.17, 0.11, 0.10, 0.18]
    ])
    l = array([1,  0.10])
    u = array([1.0, Inf])
    xmin = zeros(4)
    # solution = pips(f_fcn, x0, A, l, u, xmin, opt={'verbose': 2})
    solution = pips(f_fcn, x0, A, l, u, xmin)
    x, f, s, lam, out = solution["x"], solution["f"], solution["eflag"], \
            solution["lmbda"], solution["output"]
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, array([0, 2.8, 0.2, 0]) / 3, 6, [t, 'x'])
    t_is(f, 3.29 / 3, 6, [t, 'f'])
    t_is(out['hist'][-1]['compcond'], 0, 6, [t, 'compcond'])
    t_is(lam['mu_l'], array([6.58, 0]) / 3, 6, [t, 'lam.mu_l'])
    t_is(lam['mu_u'], array([0, 0]), 13, [t, 'lam.mu_u'])
    t_is(lam['lower'], array([2.24, 0, 0, 1.7667]), 4, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 13, [t, 'lam[\'upper\']'])

    # H = array([
    #     [1003.1, 4.3, 6.3,  5.9],
    #     [   4.3, 2.2, 2.1,  3.9],
    #     [   6.3, 2.1, 3.5,  4.8],
    #     [   5.9, 3.9, 4.8, 10.0]
    # ])
    # c = zeros(4)
    # ## check with quadprog (for dev testing only)
    # x, f, s, out, lam = quadprog(H,c,-A(2,:), -0.10, A(1,:), 1, xmin)
    # t_is(s, 1, 13, [t, 'success'])
    # t_is(x, [0 2.8 0.2 0]/3, 6, [t, 'x'])
    # t_is(f, 3.29/3, 6, [t, 'f'])
    # t_is(lam['eqlin'], -6.58/3, 6, [t, 'lam.eqlin'])
    # t_is(lam.['ineqlin'], 0, 13, [t, 'lam.ineqlin'])
    # t_is(lam['lower'], [2.24001.7667], 4, [t, 'lam[\'lower\']'])
    # t_is(lam['upper'], [0000], 13, [t, 'lam[\'upper\']'])

    t = 'constrained 2-d nonlinear : '
    ## from http://en.wikipedia.org/wiki/Nonlinear_programming#2-dimensional_example
    f_fcn = f5
    gh_fcn = gh5
    hess_fcn = hess5
    x0 = array([1.1, 0.0])
    xmin = zeros(2)
    # xmax = 3 * ones(2, 1)
    # solution = pips(f_fcn, x0, xmin=xmin, gh_fcn=gh_fcn, hess_fcn=hess_fcn, opt={'verbose': 2})
    solution = pips(f_fcn, x0, xmin=xmin, gh_fcn=gh_fcn, hess_fcn=hess_fcn)
    x, f, s, lam, out = solution["x"], solution["f"], solution["eflag"], \
            solution["lmbda"], solution["output"]
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, [1, 1], 6, [t, 'x'])
    t_is(f, -2, 6, [t, 'f'])
    t_is(out['hist'][-1]['compcond'], 0, 6, [t, 'compcond'])
    t_is(lam['ineqnonlin'], array([0, 0.5]), 6, [t, 'lam.ineqnonlin'])
    t_ok(len(lam['mu_l']) == 0, [t, 'lam.mu_l'])
    t_ok(len(lam['mu_u']) == 0, [t, 'lam.mu_u'])
    t_is(lam['lower'], zeros(x.shape), 13, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 13, [t, 'lam[\'upper\']'])
    # ## check with fmincon (for dev testing only)
    # # fmoptions = optimset('Algorithm', 'interior-point')
    # # [x, f, s, out, lam] = fmincon(f_fcn, x0, [], [], [], [], xmin, [], gh_fcn, fmoptions)
    # [x, f, s, out, lam] = fmincon(f_fcn, x0, [], [], [], [], [], [], gh_fcn)
    # t_is(s, 1, 13, [t, 'success'])
    # t_is(x, [1 1], 4, [t, 'x'])
    # t_is(f, -2, 6, [t, 'f'])
    # t_is(lam.ineqnonlin, [00.5], 6, [t, 'lam.ineqnonlin'])

    t = 'constrained 3-d nonlinear : '
    ## from http://en.wikipedia.org/wiki/Nonlinear_programming#3-dimensional_example
    f_fcn = f6
    gh_fcn = gh6
    hess_fcn = hess6
    x0 = array([1.0, 1.0, 0.0])
    # solution = pips(f_fcn, x0, gh_fcn=gh_fcn, hess_fcn=hess_fcn, opt={'verbose': 2, 'comptol': 1e-9})
    solution = pips(f_fcn, x0, gh_fcn=gh_fcn, hess_fcn=hess_fcn)
    x, f, s, lam, out = solution["x"], solution["f"], solution["eflag"], \
            solution["lmbda"], solution["output"]
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, [1.58113883, 2.23606798, 1.58113883], 6, [t, 'x'])
    t_is(f, -5 * sqrt(2), 6, [t, 'f'])
    t_is(out['hist'][-1]['compcond'], 0, 6, [t, 'compcond'])
    t_is(lam['ineqnonlin'], array([0, sqrt(2) / 2]), 7, [t, 'lam.ineqnonlin'])
    t_ok(len(lam['mu_l']) == 0, [t, 'lam.mu_l'])
    t_ok(len(lam['mu_u']) == 0, [t, 'lam.mu_u'])
    t_is(lam['lower'], zeros(x.shape), 13, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 13, [t, 'lam[\'upper\']'])
    # ## check with fmincon (for dev testing only)
    # # fmoptions = optimset('Algorithm', 'interior-point')
    # # [x, f, s, out, lam] = fmincon(f_fcn, x0, [], [], [], [], xmin, [], gh_fcn, fmoptions)
    # [x, f, s, out, lam] = fmincon(f_fcn, x0, [], [], [], [], [], [], gh_fcn)
    # t_is(s, 1, 13, [t, 'success'])
    # t_is(x, [1.58113883 2.23606798 1.58113883], 4, [t, 'x'])
    # t_is(f, -5*sqrt(2), 8, [t, 'f'])
    # t_is(lam.ineqnonlin, [0sqrt(2)/2], 8, [t, 'lam.ineqnonlin'])

    t = 'constrained 3-d nonlinear (dict) : '
    p = {'f_fcn': f_fcn, 'x0': x0, 'gh_fcn': gh_fcn, 'hess_fcn': hess_fcn}
    solution = pips(p)
    x, f, s, lam, out = solution["x"], solution["f"], solution["eflag"], \
            solution["lmbda"], solution["output"]
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, [1.58113883, 2.23606798, 1.58113883], 6, [t, 'x'])
    t_is(f, -5 * sqrt(2), 6, [t, 'f'])
    t_is(out['hist'][-1]['compcond'], 0, 6, [t, 'compcond'])
    t_is(lam['ineqnonlin'], [0, sqrt(2) / 2], 7, [t, 'lam.ineqnonlin'])
    t_ok(len(lam['mu_l']) == 0, [t, 'lam.mu_l'])
    t_ok(len(lam['mu_u']) == 0, [t, 'lam.mu_u'])
    t_is(lam['lower'], zeros(x.shape), 13, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 13, [t, 'lam[\'upper\']'])

    t = 'constrained 4-d nonlinear : '
    ## Hock & Schittkowski test problem #71
    f_fcn = f7
    gh_fcn = gh7
    hess_fcn = hess7
    x0 = array([1.0, 5.0, 5.0, 1.0])
    xmin = ones(4)
    xmax = 5 * xmin
    # solution = pips(f_fcn, x0, xmin=xmin, xmax=xmax, gh_fcn=gh_fcn, hess_fcn=hess_fcn, opt={'verbose': 2, 'comptol': 1e-9})
    solution = pips(f_fcn, x0, xmin=xmin, xmax=xmax, gh_fcn=gh_fcn, hess_fcn=hess_fcn)
    x, f, s, lam, _ = solution["x"], solution["f"], solution["eflag"], \
            solution["lmbda"], solution["output"]
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, [1, 4.7429994, 3.8211503, 1.3794082], 6, [t, 'x'])
    t_is(f, 17.0140173, 6, [t, 'f'])
    t_is(lam['eqnonlin'], 0.1614686, 5, [t, 'lam.eqnonlin'])
    t_is(lam['ineqnonlin'], 0.55229366, 5, [t, 'lam.ineqnonlin'])
    t_ok(len(lam['mu_l']) == 0, [t, 'lam.mu_l'])
    t_ok(len(lam['mu_u']) == 0, [t, 'lam.mu_u'])
    t_is(lam['lower'], [1.08787121024, 0, 0, 0], 5, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 7, [t, 'lam[\'upper\']'])

    t_end()


    # ##-----  eg99 : linearly constrained fmincon example, pips can't solve  -----
    # function [f, df, d2f] = eg99(x)
    # f = -x(1)*x(2)*x(3)
    # df = -[ x(2)*x(3)
    #         x(1)*x(3)
    #         x(1)*x(2)   ]
    # d2f = -[    0       x(3)    x(2)
    #             x(3)    0       x(1)
    #             x(2)    x(1)    0   ]
    # end
    #
    # x0 = [101010]
    # A = [1 2 2]
    # l = 0
    # u = 72
    # fmoptions = optimset('Display', 'testing')
    # fmoptions = optimset(fmoptions, 'Algorithm', 'interior-point')
    # [x, f, s, out, lam] = fmincon(f_fcn, x0, [-A A], [-l u], [], [], [], [], [], fmoptions)
    # t_is(x, [24 12 12], 13, t)
    # t_is(f, -3456, 13, t)


if __name__ == '__main__':
    t_pips(quiet=False)
