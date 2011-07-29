# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

from sys import stdout

from numpy import array, arange, zeros, ones, linalg, Inf, c_, r_
from numpy import flatnonzero as find

from scipy.sparse import hstack, issparse, csc_matrix as sparse


def LPconstr(FUN, x, idx_xi, ppopt, step0, VLB, VUB, GRADFUN, LPEQUSVR, *args):
#             P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P14,P15):
    """Finds the solution of a nonlinear programming problem based on
    successive linear programs. The key is to set up the problem as follows::

        Min f(xi, xo)
        S.T. g1(xi, xo) =0
        g2(xi, xo) =<0
    where the number of equations in g1 is the same as the number of elements
    in xi.

    Starts at x and finds a constrained minimum to
    the function which is described in FUN (usually an M-file: FUN.M).
    The function 'FUN' should return two arguments: a scalar value of the
    function to be minimized, F, and a matrix of constraints, G:
    [F,G]=FUN(X). F is minimized such that G < zeros(G).

    LPCONSTR allows a vector of optional parameters to be defined. For
    more information type HELP LPOPTION.

    VLB,VUB define a set of lower and upper bounds on the design variables, X,
    so that the solution is always in the range VLB <= X <= VUB.

    The function 'GRADFUN' is entered which returns the partial derivatives
    of the function and the constraints at X:  [gf,GC] = GRADFUN(X).

    The problem-dependent parameters P1,P2,... directly are passed to the
    functions FUN and GRADFUN: FUN(X,P1,P2,...) and GRADFUN(X,P1,P2,...).

    LAMBDA contains the Lagrange multipliers.

    to be worked out: write a generalizer equation solver

    @author: Deqiang (David) Gan (PSERC Cornell & Zhejiang University)
    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """

    # ------------------------------ setting up -------------------------------

    nvars = len(x)
    nequ =  ppopt['OPF_NEQ']

    # set up the arguments of FUN
    if ~any(FUN < 48):  # Check alphanumeric
        etype = 1
        evalstr = FUN
        evalstr = evalstr + '(x'
        for i in range(nargin - 9):
            etype = 2
            evalstr = evalstr + ',P' + str(i)
        evalstr = evalstr + ')'
    else:
        etype = 3
        evalstr = FUN + '; g=g(:)'

    # set up the arguments of GRADFUN
    if ~any(GRADFUN < 48):  # Check alphanumeric
        gtype = 1
        evalstr2 = GRADFUN + '(x'
        for i in range(nargin - 9):
            gtype = 2
            evalstr2 = evalstr2 + ',P' + str(i)
        evalstr2 = evalstr2 + ')'
    else:
        gtype = 3
        evalstr2 = GRADFUN + ';'

    # set up the arguments of LPEQUSVR
    if ~any(LPEQUSVR < 48):  # Check alphanumeric
        lpeqtype = 1
        evalstr3 = LPEQUSVR + '(x'
        for i in range(nargin - 9):
            lpeqtype = 2
            evalstr3 = evalstr3 + ',P' + str(i)
        evalstr3 = evalstr3 + ')'
    else:
        lpeqtype = 3
        evalstr3 = LPEQUSVR + ';'

    # ----------------------------- the main loop -----------------------------

    tequationer = 0
    tcomputefg = 0
    tsetuplp = 0
    tsolvelp = 0
    verbose = ppopt['VERBOSE']
    itcounter = 0
    runcounter = 1

    stepsize = step0 * 0.02  # use this small stpesize to detect how close to optimum, so to choose better stepsize

    #stepsize = step0
    #print '\n LPconstr does not adaptively choose starting point'

    f_best = 9.9e15
    f_best_run = 9.9e15
    max_slackvar_last = 9.9e15
    converged = 0

    if verbose:
        print ' it   obj function   max violation  max slack var    norm grad       norm dx'
        print '----  -------------  -------------  -------------  -------------  -------------'

    while (converged == 0) and (itcounter < ppopt['LPC_MAX_IT']) and (runcounter < ppopt['LPC_MAX_RESTART']):

        itcounter = itcounter + 1
        if verbose:
            stdout.write('%3d ' % itcounter)

        # ----- fix xi temporarily, solve equations g1(xi, xo)=0 to get xo (by Newton method).

        if len(idx_xi) == 0:
            if lpeqtype == 1:
                x, success_lf = eval(LPEQUSVR)(x)
            elif lpeqtype == 2:
                x, success_lf = eval(evalstr3)
            else:
                eval(evalstr3)
        else:
            temp = ones(nvars)
            temp[idx_xi] = zeros(len(idx_xi))
            idx_xo = find(temp)

            success_lf = 0; counter_lf = 0
            while (success_lf == 0) and (counter_lf < 10):
                counter_lf = counter_lf + 1
                if etype == 1:              # compute g(x)
                    f, g = eval(FUN)(x)
                elif etype == 2:
                    f, g = eval(evalstr)
                else:
                    eval(evalstr)

                if gtype == 1:               # compute jacobian matrix
                    df_dx, dg_dx = eval(GRADFUN)(x)
                elif gtype == 2:
                    df_dx, dg_dx = eval(evalstr2)
                else:
                    eval(evalstr2)

                dg_dx = dg_dx.T
#                dg_dx = sparse(dg_dx.T)

                dxo = -1 * linalg.solve(dg_dx[:nequ, idx_xo], g[:nequ])
                x[idx_xo] = x[idx_xo] + dxo
                if linalg.norm(dxo, Inf) < 1.0e-6:
                    success_lf = 1

        if success_lf == 0:
            stdout.write('\n      Load flow did not converge. LPconstr restarted with reduced stepsize! ')
            x = xbackup
            stepsize = 0.7 * stepsize

        # ----- compute f, g, df_dx, dg_dx

        if etype == 1:              # compute g(x)
            f, g = eval(FUN)(x)
        elif etype == 2:
            f, g = eval(evalstr)
        else:
            eval(evalstr)

        if gtype == 1:               # compute jacobian matrix
            df_dx, dg_dx = eval(GRADFUN)(x)
        elif gtype == 2:
            df_dx, dg_dx = eval(evalstr2)
        else:
            eval(evalstr2)

        dg_dx = dg_dx.T
        max_g = max(g)

        if verbose:
            stdout.write('   %-12.6g   %-12.6g' % (f, max_g))


        # ----- solve the linearized NP, that is, solve a LP to get dx

        a_lp = dg_dx.copy()
        f_lp = df_dx.copy()
        rhs_lp = -g.copy()
        vubdx = stepsize.copy()
        vlbdx = -stepsize.copy()

        if len(VUB) > 0 or len(VLB) > 0:
            raise AttributeError, ' sorry, at this stage LPconstr can not solve a problem with VLB or VUB '

        # put slack variable into the LP problem such that the LP problem is always feasible

        actual_violation = 0

        temp = find( ( g / (abs(g) + ones(len(g))) )  > 0.1 * ppopt['OPF_VIOLATION'])

        if len(temp) > 0:
            n_slack = len(temp)
            if issparse(a_lp):
                a_lp = hstack([a_lp, sparse((-ones(n_slack), (temp, arange(n_slack))), (a_lp.shape[0], n_slack))])
            else:
                a_lp = c_[a_lp, sparse((-ones(n_slack), (temp, arange(n_slack))), (a_lp.shape[0], n_slack)).todense()]

            vubdx = r_[vubdx, g[temp] + 1.0e4 * ones(n_slack)]
            vlbdx = r_[vlbdx, zeros(n_slack)]
            f_lp = r_[f_lp, 9.9e6 * max(df_dx) * ones(n_slack)]

        # Ray's heuristics of deleting constraints

        if itcounter == 1:
            idx_workc = array([])
            flag_workc = zeros(3 * len(rhs_lp) + 2 * nvars)
        else:
            flag_workc = flag_workc - 1
            flag_workc[idx_bindc] = 20 * ones(idx_bindc.shape)

            if itcounter > 20:
                idx_workc = find(flag_workc > 0)


        dx, lmbda, idx_workc, idx_bindc = LPsetup(a_lp, f_lp, rhs_lp, nequ, vlbdx, vubdx, idx_workc, ppopt)


        if len(dx) == nvars:
            max_slackvar = 0
        else:
            max_slackvar = max(dx[nvars:]) if max_slackvar < 1.0e-8 else 0

        if verbose:
            stdout.write('   %-12.6g' % max_slackvar)


        dx = dx[:nvars]  # stripe off the reduendent slack variables


        # ----- update x, compute the objective function

        x = x + dx
        xbackup = x
        dL_dx = df_dx + dg_dx.T * lmbda    # at optimal point, dL_dx should be zero (from KT condition)
        norm_df = linalg.norm(df_dx, Inf)
        norm_dL = linalg.norm(dL_dx, Inf)
        if abs(f) < 1.0e-10:
            norm_grad = norm_dL
        else:
            norm_grad = norm_dL / abs(f)
            #norm_grad = norm_dL / norm_df  # this is more stringent

        norm_dx = linalg.norm(dx / step0, Inf)

        if verbose:
            stdout.write('   %-12.6g   %-12.6g\n' % (norm_grad, norm_dx))

        # ----- check stopping conditions

        if norm_grad < ppopt['LPC_TOL_GRAD'] and \
                max_g < ppopt['OPF_VIOLATION'] and \
                norm_dx < ppopt['LPC_TOL_X']:
            converged = 1
            break

#        if max_slackvar > 1.0e-8 and itcounter > 60: break

        if norm_dx < 0.05 * ppopt['LPC_TOL_X']:      # stepsize is overly small, so what is happening?

            if max_g < ppopt['OPF_VIOLATION'] and abs(f_best - f_best_run) / f_best_run < 1.0e-4:

                # The solution is the same as that we got in previous run. So we conclude that
                # the stopping conditions are overly stringent, and LPconstr HAS found the solution.
                converged = 1
                break

            else:
                # stepsize is overly small to make good progress, we'd better restart using larger stepsize
                f_best_run = f_best
                stepsize = 0.4 * step0

                if verbose:
                    stdout.write('\n----- restarted with larger stepsize\n')

                runcounter = runcounter + 1


        # ----- adjust stepsize

        if itcounter == 1:                  # the 1th iteration is a trial one which sets up starting stepsize
            if norm_grad < ppopt['LPC_TOL_GRAD']:
                stepsize = 0.015 * step0   # use extra-small stepsize
            elif norm_grad < 2.0 * ppopt['LPC_TOL_GRAD']:
                stepsize = 0.05 * step0    # use very small stepsize
            elif norm_grad < 4.0 * ppopt['LPC_TOL_GRAD']:
                stepsize = 0.3  * step0    # use small stepsize
            elif norm_grad < 6.0 * ppopt['LPC_TOL_GRAD']:
                stepsize = 0.6  * step0    # use less small stepsize
            else:
                stepsize = step0           # use large stepsize

        if itcounter > 2:
            if max_slackvar > max_slackvar_last + 1.0e-10:
                stepsize = 0.7 * stepsize

            if max_slackvar < 1.0e-7:        # the trust region method
                actual_df  = f_last - f
                if abs(predict_df) > 1.0e-12:
                    ratio = actual_df / predict_df
                else:
                    ratio = -99999

                if ratio < 0.25 or f > f_last * 0.9999:
                    stepsize = 0.5 * stepsize
                elif ratio > 0.80:
                    stepsize = 1.05 * stepsize

                if linalg.norm(stepsize / step0, Inf) > 3.0:
                    stepsize = 3 * step0    # ceiling of stepsize

        max_slackvar_last = max_slackvar
        f_best = min([f, f_best])
        f_last = f
        predict_df = -(df_dx[:nvars]).T * dx[:nvars]

    # ------ recompute f and g
    if etype == 1:              # compute g(x)
        f, g = eval(FUN)(x)
    elif etype == 2:
        f, g = eval(evalstr)
    else:
        eval(evalstr)

    i = find(g < -ppopt['OPF_VIOLATION'])
    lmbda[i] = zeros(i.shape)

    return x, lmbda, converged
