# Copyright (C) 2010-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
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

from math import sqrt

from numpy import zeros, ones, array, eye, prod, Inf

from scipy.sparse import csr_matrix as sparse
from scipy.sparse import eye as speye

from pypower.pips import pips

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end
from pypower.t.t_ok import t_ok


## unconstrained banana function
## from MATLAB Optimization Toolbox's bandem.m
def f2(x):
    a = 100
    f = a * (x[1] - x[0]**2)**2 + (1 - x[0])**2
    df = array([
        4 * a * (x[0]**3 - x[0] * x[1]) + 2 * x[0] - 2,
        2 * a * (x[1] - x[0]**2)
    ])
    d2f = 4 * a * array([
        [3 * x[0]**2 - x[1] + 1 / (2 * a), -x[0]],
        [                           -x[0],   1/2]
    ])
    return f, df, d2f


## unconstrained 3-d quadratic
## from http://www.akiti.ca/QuadProgEx0Constr.html
def f3(x):
    H = array([5, -2, -1, -2, 4, 3, -1, 3, 5])
    c = array([2, -35, -47])
    f = 1/2 * x.T * H * x + c.T * x + 5
    df = H * x + c
    d2f = H
    return f, df, d2f


## constrained 4-d QP
## from http://www.jmu.edu/docs/sasdoc/sashtml/iml/chap8/sect12.htm
def f4(x):
    H = array([
        [1003.1, 4.3, 6.3,  5.9],
        [   4.3, 2.2, 2.1,  3.9],
        [   6.3, 2.1, 3.5,  4.8],
        [   5.9, 3.9, 4.8, 10.0]
    ])
    c = zeros(4)
    f = 1/2 * x.T * H * x + c.T * x
    df = H * x + c
    d2f = H
    return f, df, d2f


## constrained 2-d nonlinear
## from http://en.wikipedia.org/wiki/Nonlinear_programming#2-dimensional_example
def f5(x):
    c = -array([1, 1])
    f = c.T * x
    df = c
    d2f = zeros((2, 2))
    return f, df, d2f

def gh5(x):
    h = array([-1, -1, 1, 1]) * x**2 + array([1, -2])
    dh = 2 * array([-x[0], x[0], -x[1], x[1]])
    g = array([])
    dg = array([])
    return h, g, dh, dg

def hess5(x, lam, cost_mult):
    mu = lam['ineqnonlin']
    Lxx = 2 * array([-1, 1]) * mu * eye(2)
    return Lxx


## constrained 3-d nonlinear
## from http://en.wikipedia.org/wiki/Nonlinear_programming#3-dimensional_example
def f6(x):
    f = -x[0] * x[1] - x[1] * x[2]
    df = -array([x[1], x[0] + x[2], x[1]])
    d2f = -array([0, 1, 0, 1, 0, 1, 0, 1, 0])
    return f, df, d2f

def gh6(x):
    h = array([1, -1, 1, 1, 1, 1]) * x**2 + array([-2, -10])
    dh = 2 * array([x[0], x[0], -x[1], x[1], x[2], x[2]])
    g = array([])
    dg = array([])
    return h, g, dh, dg

def hess6(x, lam, cost_mult=1):
    mu = lam['ineqnonlin']
    Lxx = cost_mult * array([0, -1, 0, -1, 0, -1, 0, -1, 0]) + \
            array([2 * array([1, 1]) * mu, 0, 0, 0,
                   2 * array([-1, 1]) * mu, 0, 0, 0, 2 * array([1, 1]) * mu])
    return Lxx


## constrained 4-d nonlinear
## Hock & Schittkowski test problem #71
def f7(x):
    f = x[0] * x[3] * sum(x[0:3]) + x[2]
    df = array([ x[0] * x[3] + x[3] * sum(x[0:3]),
                 x[0] * x[3],
                 x[0] * x[3] + 1,
                 x[1] * sum(x[0:3]) ])
    d2f = sparse([
        [2 * x[3],               x[3], x[3], 2 * x[0] + x[1] + x[2]],
        [                  x[3],    0,    0,                   x[0]],
        [                  x[3],    0,    0,                   x[0]],
        [2 * x[0] + x[1] + x[2], x[0], x[0],                      0]
    ])
    return f, df, d2f

def gh7(x):
    g = sum(x**2) - 40
    h = -prod(x) + 25
    dg = 2 * x
    dh = -prod(x) / x
    return h, g, dh, dg

def hess7(x, lam, sigma=1):
    lmbda = lam['eqnonlin']
    mu    = lam['ineqnonlin']
    f, df, d2f = f7(x)
    Lxx = sigma * d2f + lmbda * 2 * speye(4) - \
        mu * sparse([
                [0,           x[2] * x[3], x[2] * x[3], x[1] * x[2]],
                [x[2] * x[2],           0, x[0] * x[3], x[0] * x[2]],
                [x[1] * x[3], x[0] * x[3],           0, x[0] * x[1]],
                [x[1] * x[2], x[0] * x[2], x[0] * x[1],           0]
        ])
    return Lxx


def t_pips(quiet=False):
    """Tests of pips NLP solver.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    t_begin(60, quiet)

    t = 'unconstrained banana function : '
    ## from MATLAB Optimization Toolbox's bandem.m
    f_fcn = f2
    x0 = array([-1.9, 2])
    # [x, f, s, out, lam] = pips(f_fcn, x0, [], [], [], [], [], [], [], struct('verbose', 2))
    x, f, s, out, lam = pips(f_fcn, x0)
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
    # x, f, s, out, lam = pips(f_fcn, x0, [], [], [], [], [], [], [], struct('verbose', 2))
    x, f, s, out, lam = pips(f_fcn, x0)
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
    x0 = array([1, 0, 0, 1], float)
    A = array([
        [1,       1,    1,    1],
        [0.17, 0.11, 0.10, 0.18]
    ])
    l = array([1, 0.10])
    u = array([1, Inf])
    xmin = zeros(4)
    # [x, f, s, out, lam] = pips(f_fcn, x0, A, l, u, xmin, [], [], [], struct('verbose', 2))
    x, f, s, out, lam = pips(f_fcn, x0, A, l, u, xmin)
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, array([0, 2.8, 0.2, 0]) / 3, 6, [t, 'x'])
    t_is(f, 3.29 / 3, 6, [t, 'f'])
    t_is(out['hist'][-1]['compcond'], 0, 6, [t, 'compcond'])
    t_is(lam['mu_l'], 6.580 / 3, 6, [t, 'lam.mu_l'])
    t_is(lam['mu_u'], array([0, 0]), 13, [t, 'lam.mu_u'])
    t_is(lam['lower'], array([2.24, 0, 0, 1.7667]), 4, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 13, [t, 'lam[\'upper\']'])

    H = array([
        [1003.1, 4.3, 6.3,  5.9],
        [   4.3, 2.2, 2.1,  3.9],
        [   6.3, 2.1, 3.5,  4.8],
        [   5.9, 3.9, 4.8, 10.0]
    ])
    c = zeros(4)
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
    x0 = array([1.1, 0])
    xmin = zeros(2)
    # xmax = 3 * ones(2, 1)
    # [x, f, s, out, lam] = pips(f_fcn, x0, [], [], [], xmin, [], gh_fcn, hess_fcn, struct('verbose', 2))
    x, f, s, out, lam = pips(f_fcn, x0, [], [], [], xmin, [], gh_fcn, hess_fcn)
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, array([1, 1]), 6, [t, 'x'])
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
    x0 = array([1, 1, 0], float)
    # x, f, s, out, lam = pips(f_fcn, x0, [], [], [], [], [], gh_fcn, hess_fcn, {'verbose': 2, 'comptol': 1e-9})
    x, f, s, out, lam = pips(f_fcn, x0, [], [], [], [], [], gh_fcn, hess_fcn)
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, array([1.58113883, 2.23606798, 1.58113883]), 6, [t, 'x'])
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

    t = 'constrained 3-d nonlinear (struct) : '
    p = {'f_fcn': f_fcn, 'x0': x0, 'gh_fcn': gh_fcn, 'hess_fcn': hess_fcn}
    x, f, s, out, lam = pips(p)
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, array([1.58113883, 2.23606798, 1.58113883]), 6, [t, 'x'])
    t_is(f, -5 * sqrt(2), 6, [t, 'f'])
    t_is(out['hist'][-1]['compcond'], 0, 6, [t, 'compcond'])
    t_is(lam['ineqnonlin'], array([0, sqrt(2) / 2]), 7, [t, 'lam.ineqnonlin'])
    t_ok(len(lam['mu_l']) == 0, [t, 'lam.mu_l'])
    t_ok(len(lam['mu_u']) == 0, [t, 'lam.mu_u'])
    t_is(lam['lower'], zeros(x.shape), 13, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 13, [t, 'lam[\'upper\']'])

    t = 'constrained 4-d nonlinear : '
    ## Hock & Schittkowski test problem #71
    f_fcn = f7
    gh_fcn = gh7
    hess_fcn = hess7
    x0 = array([1, 5, 5, 1], float)
    xmin = ones(4)
    xmax = 5 * xmin
    # [x, f, s, out, lam] = pips(f_fcn, x0, [], [], [], xmin, xmax, gh_fcn, hess_fcn, struct('verbose', 2, 'comptol', 1e-9))
    x, f, s, out, lam = pips(f_fcn, x0, [], [], [], xmin, xmax, gh_fcn, hess_fcn)
    t_is(s, 1, 13, [t, 'success'])
    t_is(x, array([1, 4.7429994, 3.8211503, 1.3794082]), 6, [t, 'x'])
    t_is(f, 17.0140173, 6, [t, 'f'])
    t_is(lam.eqnonlin, 0.1614686, 5, [t, 'lam.eqnonlin'])
    t_is(lam.ineqnonlin, 0.55229366, 5, [t, 'lam.ineqnonlin'])
    t_ok(len(lam['mu_l']) == 0, [t, 'lam.mu_l'])
    t_ok(len(lam['mu_u']) == 0, [t, 'lam.mu_u'])
    t_is(lam['lower'], array([1.08787121024, 0, 0, 0]), 5, [t, 'lam[\'lower\']'])
    t_is(lam['upper'], zeros(x.shape), 7, [t, 'lam[\'upper\']'])

    t_end


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
