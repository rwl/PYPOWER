# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

from time import time

from numpy import zeros, c_, shape

from pypower.idx_bus import MU_VMIN
from pypower.idx_gen import PG, QG, MU_QMIN, MU_PMAX, MU_PMIN
from pypower.idx_brch import PF, QF, PT, QT, MU_SF, MU_ST, MU_ANGMIN, MU_ANGMAX

from pypower.ext2int import ext2int
from pypower.opf_args import opf_args
from pypower.opf_setup import opf_setup
from pypower.opf_execute import opf_execute
from int2ext import int2ext


def opf(*args):
    """Solves an optimal power flow.

    Returns either a RESULTS struct and an optional SUCCESS flag, or individual
    data matrices, the objective function value and a SUCCESS flag. In the
    latter case, there are additional optional return values. See Examples
    below for the possible calling syntax options.

    The data for the problem can be specified in one of three ways:
    (1) a string (ppc) containing the file name of a MATPOWER case
      which defines the data matrices baseMVA, bus, gen, branch, and
      gencost (areas is not used at all, it is only included for
      backward compatibility of the API).
    (2) a struct (ppc) containing the data matrices as fields.
    (3) the individual data matrices themselves.

    The optional user parameters for user constraints (A, l, u), user costs
    (N, fparm, H, Cw), user variable initializer (z0), and user variable
    limits (zl, zu) can also be specified as fields in a case struct,
    either passed in directly or defined in a case file referenced by name.

    When specified, A, l, u represent additional linear constraints on the
    optimization variables, l <= A*[x z] <= u. If the user specifies an A
    matrix that has more columns than the number of "x" (OPF) variables,
    then there are extra linearly constrained "z" variables. For an
    explanation of the formulation used and instructions for forming the
    A matrix, see the manual.

    A generalized cost on all variables can be applied if input arguments
    N, fparm, H and Cw are specified.  First, a linear transformation
    of the optimization variables is defined by means of r = N * [x z].
    Then, to each element of r a function is applied as encoded in the
    fparm matrix (see manual). If the resulting vector is named w,
    then H and Cw define a quadratic cost on w: (1/2)*w'*H*w + Cw * w .
    H and N should be sparse matrices and H should also be symmetric.

    The optional mpopt vector specifies MATPOWER options. If the OPF
    algorithm is not explicitly set in the options MATPOWER will use
    the default solver, based on a primal-dual interior point method.
    For the AC OPF this is OPF_ALG = 560, unless the TSPOPF optional
    package is installed, in which case the default is 540. For the
    DC OPF, the default is OPF_ALG_DC = 200. See MPOPTION for
    more details on the available OPF solvers and other OPF options
    and their default values.

    The solved case is returned either in a single results struct (described
    below) or in the individual data matrices, bus, gen and branch. Also
    returned are the final objective function value (f) and a flag which is
    true if the algorithm was successful in finding a solution (success).
    Additional optional return values are an algorithm specific return status
    (info), elapsed time in seconds (et), the constraint vector (g), the
    Jacobian matrix (jac), and the vector of variables (xr) as well
    as the constraint multipliers (pimul).

    The single results struct is a MATPOWER case struct (ppc) with the
    usual baseMVA, bus, branch, gen, gencost fields, along with the
    following additional fields:

        C{order}      see 'help ext2int' for details of this field
        C{et}         elapsed time in seconds for solving OPF
        C{success}    1 if solver converged successfully, 0 otherwise
        C{om}         OPF model object, see 'help opf_model'
        C{x}          final value of optimization variables (internal order)
        C{f}          final objective function value
        C{mu}         shadow prices on ...
            C{var}
                C{l}  lower bounds on variables
                C{u}  upper bounds on variables
            C{nln}
                C{l}  lower bounds on nonlinear constraints
                C{u}  upper bounds on nonlinear constraints
            C{lin}
                C{l}  lower bounds on linear constraints
                C{u}  upper bounds on linear constraints
        C{g}          (optional) constraint values
        C{dg}         (optional) constraint 1st derivatives
        C{df}         (optional) obj fun 1st derivatives (not yet implemented)
        C{d2f}        (optional) obj fun 2nd derivatives (not yet implemented)
        C{raw}        raw solver output in form returned by MINOS, and more
            C{xr}     final value of optimization variables
            C{pimul}  constraint multipliers
            C{info}   solver specific termination code
            C{output} solver specific output information
               C{alg} algorithm code of solver used
        C{var}
            C{val}    optimization variable values, by named block
                C{Va}     voltage angles
                C{Vm}     voltage magnitudes (AC only)
                C{Pg}     real power injections
                C{Qg}     reactive power injections (AC only)
                C{y}      constrained cost variable (only if have pwl costs)
                (other) any user defined variable blocks
            C{mu}     variable bound shadow prices, by named block
                C{l}  lower bound shadow prices
                    C{Va}, C{Vm}, C{Pg}, C{Qg}, C{y}, (other)
                C{u}  upper bound shadow prices
                    C{Va}, C{Vm}, C{Pg}, C{Qg}, C{y}, (other)
        C{nln}    (AC only)
            C{mu}     shadow prices on nonlinear constraints, by named block
                C{l}  lower bounds
                    C{Pmis}   real power mismatch equations
                    C{Qmis}   reactive power mismatch equations
                    C{Sf}     flow limits at "from" end of branches
                    C{St}     flow limits at "to" end of branches
                C{u}  upper bounds
                    C{Pmis}, C{Qmis}, C{Sf}, C{St}
        C{lin}
            C{mu}     shadow prices on linear constraints, by named block
                C{l}  lower bounds
                    C{Pmis}   real power mistmatch equations (DC only)
                    C{Pf}     flow limits at "from" end of branches (DC only)
                    C{Pt}     flow limits at "to" end of branches (DC only)
                    C{PQh}    upper portion of gen PQ-capability curve(AC only)
                    C{PQl}    lower portion of gen PQ-capability curve(AC only)
                    C{vl}     constant power factor constraint for loads
                    (AC only)
                    C{ycon}   basin constraints for CCV for pwl costs
                    (other) any user defined constraint blocks
                C{u}  upper bounds
                    C{Pmis}, C{Pf}, C{Pf}, C{PQh}, C{PQl}, C{vl}, C{ycon},
                    (other)
        C{cost}       user defined cost values, by named block

    @see: L{runopf}, L{dcopf}, L{uopf}, L{caseformat}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ##----- initialization -----
    t0 = time()         ## start timer

    ## process input arguments
    ppc, ppopt = opf_args(*args)

    ## add zero columns to bus, gen, branch for multipliers, etc if needed
    nb   = shape(ppc['bus'])[0]    ## number of buses
    nl   = shape(ppc['branch'])[0] ## number of branches
    ng   = shape(ppc['gen'])[0]    ## number of dispatchable injections
    if shape(ppc['bus'])[1] < MU_VMIN:
        ppc['bus'] = c_[ppc['bus'], zeros((nb, MU_VMIN - shape(ppc['bus'])[1]))]

    if shape(ppc['gen'])[1] < MU_QMIN:
        ppc['gen'] = c_[ppc['gen'], zeros((ng, MU_QMIN - shape(ppc['gen'])[1]))]

    if shape(ppc['branch'])[1] < MU_ANGMAX:
        ppc['branch'] = c_[ppc['branch'], zeros((nl, MU_ANGMAX - shape(ppc['branch'])[1]))]

    ##-----  convert to internal numbering, remove out-of-service stuff  -----
    ppc = ext2int(ppc)

    ##-----  construct OPF model object  -----
    om = opf_setup(ppc, ppopt)

    ##-----  execute the OPF  -----
    results, success, raw = opf_execute(om, ppopt)

    ##-----  revert to original ordering, including out-of-service stuff  -----
    results = int2ext(results)

    ## zero out result fields of out-of-service gens & branches
    if len(results['order']['gen']['status']['off']) > 0:
        results['gen'][results['order']['gen']['status']['off'], [PG, QG, MU_PMAX, MU_PMIN]] = 0

    if len(results['order']['branch']['status']['off']) > 0:
        results['branch'][results['order']['branch']['status']['off'], [PF, QF, PT, QT, MU_SF, MU_ST, MU_ANGMIN, MU_ANGMAX]] = 0

    ##-----  finish preparing output  -----
    et = time() - t0      ## compute elapsed time

    results['et'] = et
    results['success'] = success
    results['raw'] = raw

    return results
