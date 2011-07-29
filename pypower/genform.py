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

"""Help file describing the generalized OPF formulation used by
the IPOPT solver.

==========
 CONTENTS
==========

1. General OPF Problem Formulation
2. General Linear Constraints
3. Generalized Cost Function
4. Piecewise Linear Convex Cost Formulation Using Constrained Cost Variables
5. Generator P-Q Capability Curves
6. Dispatchable Loads
7. Problem Data Transformation
8. Example of Additional Linear Constraint
9. Miscellaneous


====================================
 1. GENERAL OPF PROBLEM FORMULATION
====================================

The problem is formulated in terms of 3 groups of optimization variables,
labeled x, y and z. The vector x = [ Theta; V; Pg; Qg ] contains the OPF
variables, consisting of the voltage angles Theta and magnitudes V at each of
the nb buses, and real and reactive generator injections Pg and Qg for each of
the ng generators. The y variables are the helper variables used by the
constrained cost variable (CCV) formulation of the piecewise linear generator
cost functions. Additional user defined variables are grouped in z.

The optimization problem can be expressed as follows:

   min  sum( f1i(Pgi) + f2i(Qgi) ) + sum(y) + 0.5 * w' * H * w + Cw' * w
  x,y,z

subject to
  g(x) <=> 0          (nonlinear constraints: bus power balance equations
                                              & branch flow limits)
  l <= A*[x;y;z] <= u (general linear constraints)
  xmin <= x <= xmax   (variable bounds: voltage limits, generation limits)

The most significant additions to the traditional, simple OPF formulation
appear in the generalized cost terms containing w and in the general linear
constraints involving the matrix A, described in the next two sections.


===============================
 2. GENERAL LINEAR CONSTRAINTS
===============================

In addition to the standard non-linear equality constraints for nodal power
balance and non-linear inequality constraints for line flow limits, this
formulation includes a framework for additional linear constraints involving
the full set of optimization variables.

  l <= A*[x;y;z] <= u (general linear constraints)

Some portions of these linear constraints are supplied directly by the user,
while others are generated automatically based on the case data. Automatically
generated portions include:

* rows for constraints that define generator P-Q capability curves
* rows for constant power factor constraints for dispatchable loads
* rows and columns for the y variables from the CCV implementation of
  piecewise linear generator costs and their associated constraints

In addition to these automatically generated constraints, the user can provide
a matrix Au and vectors lu and uu to define further linear constraints. These
user supplied constraints could be used, for example, to restrict voltage
angle differences between specific buses. The matrix Au must have at least nx
columns where nx is the number of x variables. If Au has more than nx columns,
a corresponding z optimization variable is created for each additional column.
These z variables also enter into the generalized cost terms described below,
so Au and N must have the same number of columns.

  lu <= Au*[x;z] <= uu (user supplied linear constraints)

*Change from MATPOWER 3.0*: The Au matrix supplied by the user no longer
includes the (all zero) col-umns corresponding to the y variables for
piecewise linear generator costs. This should simplify signifi-cantly the
creation of the desired Au matrix.


==============================
 3. GENERALIZED COST FUNCTION
==============================

The cost function consists of 3 parts. The first two are the polynomial and
piecewise linear costs, respectively, of generation. A polynomial or piecewise
linear cost is specified for each generator's active output and, optionally,
reactive output in the appropriate row(s) of the gencost matrix. Any piecewise
linear costs are implemented using the CCV formulation described below which
introduces corresponding helper y variables. The general formulation allows
generator costs of mixed type (polynomial and piece-wise linear) in the same
problem.

The third part of the cost function provides a general framework for imposing
additional costs on the optimization variables, enabling things such as using
penalty functions as soft limits on voltages, additional costs on variables
involved in constraints handled by Langrangian relaxation, etc. This general
cost term is specified through a set of parameters  H, Cw,  N and fparm,
described below. It consists of a general quadratic function of an  nw x 1
vector w of transformed optimization variables.

  1/2 * w' * H * w + Cw' * w

H is the nw x nw symmetric, sparse matrix of quadratic coefficients and Cw
is the nw x 1 vector of linear coefficients. The sparse N matrix is nw x nxz,
where the number of columns must match that of any user supplied Au matrix.
And fparm is nw x 4, where the 4 columns are labeled as

  fparm = [ d rhat h m ].

The vector w is created from the x and z optimization variables by first
applying a general linear transformation

  r = N * [x; z],

followed by a scaled function with a shifted "dead zone", defined by the
remaining elements of fparm. Each element of r is transformed into the
corresponding element of w as follows:

        /  mi * fi(ri - rhati + hi),  for ri - rhati < -hi
  wi = <   0,                         for -hi <= ri - rhati <= hi
        \  mi * fi(ri - rhati - hi),  for ri - rhati > hi

where the function fi is a predetermined function selected by the index in di.
The current implementation includes linear and quadratic options.

           /  t,    for di = 1
  fi(t) = <
           \  t^2,  for di = 2

See the User's Manual for an illustration of the linear case.


==============================================================================
 4. PIECEWISE LINEAR CONVEX COST FORMULATION USING CONSTRAINED COST VARIABLES
==============================================================================

The OPF formulations in MATPOWER allow for the specification of convex
piecewise linear cost functions for active or reactive generator output. An
example of such a cost curve is shown below.

 cost axis
     ^
c2   |                           *
     |                        *
     |                     *
c1   |                  *
     |          *
c0   |   *
     |------------------------------->   Pg axis
         x0            x1         x2
        Pmin                     Pmax
This non-differentiable cost is modeled using an extra helper cost variable
for each such cost curve and additional constraints on this variable and Pg,
one for each segment of the curve. The constraints build a convex "basin"
equivalent to requiring the cost variable to lie in the epigraph of the cost
curve. When the cost is minimized, the cost variable will be pushed against
this basin. If the helper cost variable is y, then the contribution of the
generator's cost to the total cost is exactly y. In the above case, the two
additional required constraints are

  1)  y >= m1*(Pg - x0) + c0   (y must lie above the first segment)
  2)  y >= m2*(Pg - x1) + c1   (y must lie above the second segment)

where  m1 and m2 are the slopes of the two segments. Also needed, of course,
are the box restrictions on Pg:  Pmin � Pg � Pmax. The additive part of the
cost contributed by this generator is y.

This constrained cost variable (CCV) formulation is used by all of the
MATPOWER OPF solvers for handling piecewise linear cost functions. In the
generalized OPF formulation, the capability to accept general linear
constraints is used to introduce new y variables (one for each piecewise
linear cost in the problem) and constraints (one for each cost segment in the
problem). The function that builds the coefficient matrix for the restrictions
is makeAy. This is done inside fmincopf (or mopf when using MINOPF) and is
automatically added to the user supplied linear constraints and general costs.


====================================
 5. GENERATOR P-Q CAPABILITY CURVES
====================================

The traditional AC OPF formulation models the generator P-Q capability curves
as simple box constraints defined by the PMIN, PMAX, QMIN and QMAX columns of
the gen matrix. In MATPOWER 3.1, version 2 of the case file format is
introduced, which includes 6 new columns in the gen matrix for specifying
additional sloped upper and lower portions of the capability curves. The new
columns are PC1, PC2, QC1MIN, QC1MAX, QC2MIN, and QC2MAX. The feasible region
for generator operation with this more general capability curve is the area
inside the original box constraints that lies below the line which passes
through (PC1, QC1MAX), (PC2, QC2MAX) and above the line which passes through
(PC1, QC1MIN), (PC2, QC2MIN). See the User's Manual for an illustration.

The particular values of PC1 and PC2 are not important and may be set equal to
PMIN and PMAX for convenience. The important point is to set the corresponding
QCnMAX (QCnMIN) limits such that the two resulting points define the desired
line corresponding to the upper (lower) sloped portion of the capability
curve.


=======================
 6. DISPATCHABLE LOADS
=======================

In general, dispatchable or price-sensitive loads can be modeled as negative
real power injections with associated costs. The current test is that if
PMIN < PMAX = 0 for a generator, then it is really a dispatchable load. If a
load has a demand curve like the following

 quantity
    ^
    |
    |
P2  |-------------+
    |             |
    |             |
P1  |_____________|_____________+
    |                           |
    |                           |
    |---------------------------+---->   price
                price1        price2

so that it will consume zero if the price is higher than price2, P1 if the
price is less than price2 but higher than price1, and P2 if the price is equal
or lower than price1. Considered as a negative injection, the desired dispatch
is zero if the price is greater than price2, -P1 if the price is higher than
price1 but lower than price2, and -P2 if the price is equal to or lower than
price1. This suggests the following piecewise linear cost curve:

                                      cost
                                       ^
         -P2              -P1         0|
---------------------------------------*-->  power
                                     * |0
                      slope=price2 *   |
                                 *     |
                               *       |
                             *         |
                           *           |
                      *                |
                 *                     |
            * slope=price1             |
       *                               |


Note that this assumes that the demand blocks can be partially dispatched or
"split"; if the price trigger is reached half-way through the block, the load
must accept the partial block. Otherwise, accepting or rejecting whole blocks
really poses a mixed-integer problem, which is outside the scope of the
current MATPOWER implementation.

When there are dispatchable loads, the issue of reactive dispatch arises. If
the QMIN/QMAX generation limits for the "negative generator" in question are
not set to zero, then the algorithm will dispatch the reactive injection to
the most convenient value. Since this is not normal load behavior, in the
generalized formulation it is assumed that dispatchable loads maintain a
constant power factor. The mechanism for posing additional general linear
constraints is employed to automatically include restrictions for these
injections to keep the ratio of Pg and Qg constant. This ratio is inferred
from the values of PMIN and either QMIN (for inductive loads) or QMAX (for
capacitive loads) in the gen table. It is important to set these
appropriately, keeping in mind that PG is negative and that for normal
inductive loads QG should also be negative (a positive reactive load is a
negative reactive injection). The initial values of the PG and QG columns of
the gen matrix must be consistent with the ratio defined by PMIN and the
appropriate Q limit.


================================
 5. PROBLEM DATA TRANSFORMATION
================================

Defining a user supplied A matrix to add additional linear constraints
requires knowledge of the order of the optimization variables in the x vector.
This requires an understanding of the standard transformations performed on
the input data (bus, gen, branch, areas and gencost tables) before the problem
is solved. All of these transformations are reversed after solving the problem
so the output data is correctly placed in the tables.

The first step filters out inactive generators and branches; original tables
are saved for data output.

  comgen   = find(gen(:,GEN_STATUS) > 0);      find online generators
  onbranch = find(branch(:,BR_STATUS) ~= 0);   find online branches
  gen      = gen(comgen, :);
  branch   = branch(onbranch, :);

The second step is a renumbering of the bus numbers in the bus table so that
the resulting table contains consecutively-numbered buses starting from 1:

  [i2e, bus, gen, branch, areas] = ext2int(bus, gen, branch, areas);

where i2e is saved for inverse reordering at the end. Finally, generators are
further reordered by bus number:

  ng = size(gen,1);                  number of generators or injections
  [tmp, igen] = sort(gen(:, GEN_BUS));
  [tmp, inv_gen_ord] = sort(igen);   save for inverse reordering at the end
  gen  = gen(igen, :);
  if ng == size(gencost,1)           This is because gencost might have
    gencost = gencost(igen, :);      twice as many rows as gen if there
  else                               are reactive injection costs.
    gencost = gencost( [igen; igen+ng], :);
  end

Having done this, the variables inside the x vector now have the same ordering
as in the bus, gen tables:

 x = [  Theta ;     nb bus voltage angles
          V   ;     nb bus voltage magnitudes
          Pg  ;     ng active power injections (p.u.) (ascending bus order)
          Qg ];     ng reactive power injections (p.u.)(ascending bus order)

and the nonlinear constraints have the same order as in the bus, branch tables

 g = [  gp;         nb real power flow mismatches (p.u.)
        gq;         nb reactive power flow mismatches (p.u.)
        gsf;        nl "from" end apparent power injection limits (p.u.)
        gst ];      nl "to" end apparent power injection limits (p.u.)

With this setup, box bounds on the variables are applied as follows: the
reference angle is bounded above and below with the value specified for it in
the original bus table. The V section of x is bounded above and below with the
corresponding values for VMAX and VMIN in the bus table. The Pg and Qg
sections of x are bounded above and below with the corresponding values for
PMAX, PMIN, QMAX and QMIN in the gen table. The nonlinear constraints are
similarly setup so that gp and gq are equality constraints (zero RHS) and the
limits for gsf, gst are taken from the RATE_A column in the branch table.


============================================
 8. EXAMPLE OF ADDITIONAL LINEAR CONSTRAINT
============================================

The following example illustrates how an additional general linear constraint
can be added to the problem formulation. In the standard solution to case9.m,
the voltage angle for bus 7 lags the voltage angle in bus 2 by 6.09 degrees.
Suppose we want to limit that lag to 5 degrees at the most. A linear
restriction of the form

  Theta(2) * Theta(7) <= 5 degrees

would do the trick. We have nb = 9 buses, ng = 3 generators and nl = 9
branches. Therefore the first 9 elements of x are bus voltage angles, elements
10-18 are bus voltage magnitudes, elements 19-21 are active injections
corresponding to the generators in buses 1, 2 and 3 (in that order) and
elements 22-24 are the corresponding reactive injections. Note that in this
case the generators in the original data already appear in ascending bus
order, so no permutation with respect to the original data is necessary. Going
back to the angle restriction, we see that it can be cast as

 [ 0 1 0 0 0 0 -1 0 0 zeros(1,nb+ng+ng) ] * x  <= 5 degrees

We can set up the problem as follows:

  A = sparse([1;1], [2;7], [1;-1], 1, 24);
  l = -Inf;
  u = 5 * pi/180;
  mpopt = mpoption('OPF_ALG', 520);  use fmincon w/generalized formulation
  opf('case9', A, l, u, mpopt)

which indeed restricts the angular separation to 5 degrees.


==================
 9. MISCELLANEOUS
==================

Finally, to complete this section we include the structure of
the Jacobian used internally by MINOS; note that the sparse matrix
returned by the solvers only includes the rows up to the last of the
nonlinear constraints (those related to the injection limit on the
"to" side of the branches).

        nb       nb       ng       ng               ny + nz
    +------------------------------------+-------------------------+
    |   dgP      dgP      dgP            |                         |
nb  |   ---      ---      ---       0    |                         |
    |   dth      dV       dP             |                         |
    |                                    |                         |
    |   dgQ      dgQ               dgQ   |                         |
nb  |   ---      ---       0       ---   |                         |
    |   dth      dV                dQ    |                         |
    |                                    | sparse(2*nb+2*nl,ny+nz) |
    |   dSf      dSf                     |                         |
nl  |   ---      ---       0        0    |                         | M = 2*nb
    |   dth      dV                      |                         |   + 2*nl
    |                                    |                         |   + mA
    |   dSt      dSt                     |                         |
nl  |   ---      ---       0        0    |                         |
    |   dth      dV                      |                         |
    +------------------------------------+-------------------------+
    |                                                              |
mA  |                                A                             |
    |                                                              |
    +--------------------------------------------------------------+
                         N = 2*nb + 2*ng + ny + nz


@author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad Autonoma
de Manizales)
@author: Ray Zimmerman (PSERC Cornell)
"""
