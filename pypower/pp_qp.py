# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

"""Quadratic program solver.
"""

from sys import stdout

from numpy import array, r_, zeros, Inf, ones, dot, flatnonzero as find

from scipy.sparse import issparse, tril, csc_matrix as sparse

from pypower.have_fcn import have_fcn


def qp_f(x, user_data=None):
    """Calculates the objective value.
    """
    return 0.5 * dot(x * user_data['H'], x) + dot(user_data['f'], x)


def qp_grad_f(x, user_data=None):
    """Calculates gradient for objective function.
    """
    return user_data['H'] * x + user_data['f']


def qp_g(x, user_data=None):
    """Calculates the constraint values and returns an array.
    """
    return user_data['A'] * x


def qp_jac_g(x, flag, user_data=None):
    """Calculates the Jacobi matrix.

    If the flag is true, returns a tuple (row, col) to indicate the
    sparse Jacobi matrix's structure.
    If the flag is false, returns the values of the Jacobi matrix
    with length nnzj.
    """
    Acoo = user_data['A'].tocoo()
    if flag:
        return (Acoo.row, Acoo.col)
    else:
        return Acoo.data


#def qp_h(x, lagrange, obj_factor, flag, user_data=None):
##    print 'H', type(user_data)
#    H = user_data['H'].tocoo()
#    if flag:
#        return (H.row, H.col)
#    else:
#        return H.data


def qp_h(x, lagrange, obj_factor, flag, Hl):
    if flag:
        return (Hl.row, Hl.col)
    else:
        return Hl.data


def pp_qp(H, f, A, b, VLB, VUB, x0, N,
          use_finite_differences=True, **kw_args):
    """Quadratic program solver.

    Solves the quadratic programming problem:

          min 0.5*x'Hx + f'x
           x

    subject to:
            l <= Ax <= b
          VLB <=  x <= VUB

    @param x0: initial starting point
    @param N: the first N constraints defined by A and b are equality constr.

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    success = 0

    if (VLB is None) or (len(VLB) == 0):
        VLB = -Inf * ones(x0.shape)
    if (VUB is None) or (len(VUB) == 0):
        VUB =  Inf * ones(x0.shape)

    if have_fcn('pyipopt'):
        import pyipopt

        pyipopt.set_loglevel(1)

        userdata = {'H': H, 'f': f, 'A': A}

        # n is the number of variables
        n = x0.shape[0]
        # lower bound of x as bounded constraints
        xl = VLB
        # upper bound of x as bounded constraints
        xu = VUB
        # number of linear constraints (zero nln)
        m = A.shape[0]
        # lower bound of constraint
        gl = -Inf * ones(m)
        gl[:N] = b[:N]
        # upper bound of constraints
        gu = b
        # number of nonzeros in Jacobi matrix
        nnzj = A.nnz
        # number of non-zeros in Hessian matrix, you can set it to 0
        nnzh = H.nnz

        if use_finite_differences:
            nnzh = 0
            nlp = pyipopt.create(n, xl, xu, m, gl, gu, nnzj, nnzh,
                                 qp_f, qp_grad_f, qp_g, qp_jac_g)
        else:
            Hl = tril(H, format='coo')

            eval_h = lambda x, lagrange, obj_factor, flag, userdata=None: qp_h(x, lagrange, obj_factor, flag, Hl)

            nlp = pyipopt.create(n, xl, xu, m, gl, gu, nnzj, nnzh,
                                 qp_f, qp_grad_f, qp_g, qp_jac_g, eval_h)


        for k, v in kw_args.iteritems():
            if isinstance(v, int):
                nlp.int_option(k, v)
            elif isinstance(v, basestring):
                nlp.str_option(k, v)
            else:
                nlp.num_option(k, v)


        result = nlp.solve(x0, m, userdata)

        ## final values for the primal variables
        xout = result[0]
        ## final values for the lower bound multipliers
        zl = result[1]
        ## final values for the upper bound multipliers
        zu = result[2]
        ## final value of the objective
        obj = result[3]
        ## status of the algorithm
        status = result[4]
        ## final multipliers for constraints
        mG = result[5]

        nlp.close()

#        print obj
#        print len(xout), xout
#        print status
#        print len(mG)
#        print len(zl), len(zu)

#        ## if negative, lowerbound was hit
#        ilt = find(mG <= 0)
#        ## if positive, the upperbound was hit
#        igt = find(mG > 0)
#        mulow = zeros(m)
#        muupp = zeros(m)
#        muupp[ilt] = -mG[ilt]
#        mulow[igt] =  mG[igt]
#        lambdaout = r_[mG, mulow, muupp]

        lambdaout = r_[mG, zl, zu]

        howout = status
        success = (status == 0)


    elif have_fcn('nlopt'):
        raise NotImplementedError
    else:
        raise ValueError, 'no QP solver available'

#    if skip_bpmpd or not have_fcn('bpmpd'):  ## no bpmpd, use QP solver from Opt Tbx
#        if have_fcn('quadprog'):             ## use quadprog from Opt Tbx ver 2.x+
#            if N:
#                nb = len(b)
#                Aeq = A[:N, :]
#                beq = b[:N]
#                Aieq = A[N:nb, :]
#                bieq = b[N:nb]
##            Aieq.todense()
##            bieq
#            else:
#                Aeq = array([])
#                beq = array([])
#                Aieq = A.copy()
#                bieq = b.copy()
#
#            if verbosein > 1:
#                qpopt = optimset('Display', 'iter')
#            elif verbosein == 1:
#                qpopt = optimset('Display', 'final')
#            else:
#                qpopt = optimset('Display', 'off')
#
#            xout, fval, exitflag, output, lmbda = \
#                quadprog(H, f, Aieq, bieq, Aeq, beq, VLB, VUB, x0, qpopt)
#            howout = exitflag
#            if exitflag == 1:
#                success = 1
#
#            lambdaout = r_[ lmbda.eqlin,
#                            lmbda.ineqlin,
#                            lmbda.lower,
#                            lmbda.upper    ]
#        elif have_fcn('qp'):   ## use qp from Opt Tbx ver 1.x/2.x
#            xout, lambdaout, howout = qp(H, f, A, b, VLB, VUB, x0, N, verbosein)
#            if howout == 'ok':
#                success = 1
#        else:
#            raise ValueError, 'This function requires a QP solver. Please install the Optimization Toolbox or the BPMPD solver.'
#    else:            ## use bpmpd
#        n = len(f)
#        m = len(b)
#
#
#        if x0 is None:
#            x0 = zeros(n)    # Until bpmpd features warm start, this is a dummy arg
#        if VUB is None:
#            VUB = array([])
#        if VLB is None:
#            VLB = array([])
#
#        if len(H) > 0:
#            if not issparse(H):
#                H = sparse(H)
#
#        if not issparse(A):
#            A = sparse(A)
#
#        e = -ones(m)
#        if N > 0:
#            e[:N, :] = zeros(N)
#
#        if len(VLB) > 0:
#            llist = find(VLB > -1e15)  # interpret limits <= -1e15 as unbounded
#            lval = VLB[llist]
#        else:
#            llist = array([])
#            lval = array([])
#
#        if len(VUB) > 0:
#            ulist = find(VUB < 1e15)  # interpret limits >= 1e15 as unbounded
#            uval = VUB[ulist]
#        else:
#            ulist = array([])
#            uval = array([])
#
#        if verbosein == -1:
#            prnlev = 0
#        else:
#            prnlev = 1
#
#        if computer == 'PCWIN':
#            if prnlev:
#                stdout.write('Windows version of BPMPD_MEX cannot print to screen.\n')
#
#            prnlev = 0
#
#        myopt = bpopt.copy()
#        #myopt(14)= 1e-1;   # TPIV1  first relative pivot tolerance (desired)
#        #myopt(20)= 1e-10;  # TOPT1  stop if feasible and rel. dual gap less than this
#        #myopt(22)= 1e-6;   # TFEAS1 relative primal feasibility tolerance
#        #myopt(23)= 1e-6;   # TFEAS2 relative dual feasibility tolerance
#        #myopt(29)= 1e-10;  # TRESX  acceptable primal residual
#        #myopt(30)= 1e-10;  # TRESY  acceptable dual residual
#        #myopt(38)= 0;      # SMETHOD1 prescaling method
#
#        xout, y, s, w, howout = bp(H, A, b, f, e, llist, lval,
#                                   ulist, uval, myopt, prnlev)
#
#        ilt = find(w <= 0)
#        igt = find(w > 0)
#        mulow = zeros(n)
#        muupp = zeros(n)
#        muupp[ilt] = -w[ilt]
#        mulow[igt] = w[igt]
#
#        lambdaout = -y
#        if len(VLB) > 0:
#            lambdaout = r_[lambdaout, mulow]
#
#        if len(VUB) > 0:
#            lambdaout = r_[lambdaout, muupp]
#
#        # zero out lambdas smaller than a certain tolerance
#        ii = find(abs(lambdaout) < 1e-9)
#        lambdaout[ii] = zeros(ii.shape)
#
#        # The next is necessary for proper operation of constr.m
#        if howout == 'infeasible primal':
#            lambdaout = zeros(lambdaout.shape)
#
#        if howout == 'optimal solution':
#            success = 1
#
#        if success:
#            # double-check feasibility
#            bpmpd_bug_fatal = 0
#            err_tol = 1e-4
#            nb = len(b)
#            if len(VLB) > 0:
#                lb_violation = VLB - xout
#                if verbosein > 0:
#                    stdout.write('max variable lower bound violatation: %g\n' % max(lb_violation))
#            else:
#                lb_violation = zeros(xout.shape)
#
#            if len(VUB) > 0:
#                ub_violation = xout - VUB
#                if verbosein > 0:
#                    stdout.write('max variable upper bound violation: %g\n' % max(ub_violation))
#            else:
#                ub_violation = zeros(xout.shape)
#
#            if N > 0:
#                eq_violation = abs( A[:N, :] * xout - b[:N] )
#                if verbosein > 0:
#                    stdout.write('max equality constraint violation: %g\n' % max(eq_violation))
#            else:
#                eq_violation = zeros(N)
#
#            if N < nb:
#                ineq_violation = A[N:nb, :] * xout - b[N:nb]
#                if verbosein > 0:
#                    stdout.write('max inequality constraint violation: %g\n' % max(ineq_violation))
#            else:
#                ineq_violation = zeros(nb - N)
#
#            if any( r_[ lb_violation,
#                        ub_violation,
#                        eq_violation,
#                        ineq_violation ] > err_tol):
#                err_cnt = 0
#                errs = []
#                if any( lb_violation > err_tol ):
#                    err_cnt = err_cnt + 1
#                    errs[err_cnt] = \
#                        'variable lower bound violated by #g' % max(lb_violation)
#
#                if any( ub_violation > err_tol ):
#                    err_cnt = err_cnt + 1
#                    errs[err_cnt] = \
#                        'variable upper bound violated by #g' % max(ub_violation)
#
#                if any( eq_violation > err_tol ):
#                    err_cnt = err_cnt + 1
#                    errs[err_cnt] = \
#                        'equality constraint violated by %g' % max(eq_violation)
#
#                if any( ineq_violation > err_tol ):
#                    err_cnt = err_cnt + 1
#                    errs[err_cnt] = \
#                        'inequality constraint violated by %g' % max(ineq_violation)
#
#                stdout.write('\nWARNING: This version of BPMPD_MEX has a bug which caused it to return\n')
#                stdout.write(  '         an incorrect (infeasible) solution for this particular problem.\n')
#                for err_idx in range(err_cnt):
#                    stdout.write('         %s\n' % errs[err_idx])
#
#                if bpmpd_bug_fatal:
#                    raise ValueError, '%s\n%s' + \
#                        'To avoid this bug in BPMPD_MEX you will need' + \
#                        'to use a different QP solver for this problem.'
#                else:
#                    stdout.write('         Retrying with QP solver from Optimization Toolbox ...\n\n')
#                    skip_bpmpd = 1         ## try again using another solver
#                    xout, lambdaout, howout, success = \
#                        mp_qp(H, f, A, b, VLB, VUB, x0, N, verbosein, skip_bpmpd)

    return xout, lambdaout, howout, success
