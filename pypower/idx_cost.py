# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

""" Defines constants for named column indices to gencost matrix.

See http://www.pserc.cornell.edu/matpower/ for more info.

Some examples of usage, after defining the constants using the line above,
are:

 start = gencost[4, STARTUP]       # get startup cost of generator 4
 gencost[2, [MODEL, NCOST:COST+1]] = [ POLYNOMIAL 2 30 0 ];
 # set the cost of generator 2 to a linear function COST = 30 * Pg

The index, name and meaning of each column of the gencost matrix is given
below:

columns 1-5
 1  MODEL       cost model, 1 - piecewise linear, 2 - polynomial
 2  STARTUP     startup cost in US dollars
 3  SHUTDOWN    shutdown cost in US dollars
 4  NCOST       number of cost coefficients to follow for polynomial cost
                function, or number of data points for piecewise linear
 5  COST        1st column of cost parameters
                cost data defining total cost function
                For polynomial cost (highest order coeff first):
                        e.g. c2, c1, c0
                where the polynomial is c0 + c1*P + c2*P^2
                For piecewise linear cost:
                        x0, y0, x1, y1, x2, y2, ...
                where x0 < x1 < x2 < ... and the points (x0,y0), (x1,y1),
                (x2,y2), ... are the end- and break-points of the total
                cost function.

additional constants, used to assign/compare values in the MODEL column
 1  PW_LINEAR   piecewise linear generator cost model
 2  POLYNOMIAL  polynomial generator cost model
"""
# define cost models
PW_LINEAR   = 1
POLYNOMIAL  = 2

# define the indices
MODEL       = 1    # cost model, 1 - piecewise linear, 2 - polynomial
STARTUP     = 2    # startup cost in US dollars
SHUTDOWN    = 3    # shutdown cost in US dollars
NCOST       = 4    # number breakpoints in piecewise linear cost function,
                   # or number of coefficients in polynomial cost function
COST        = 5    # beginning of cost parameters,
                   # piecewise linear data as:
                   #      x0, y0, x1, y1, x2, y2, ...
                   # and polynomial data as:
                   #      c2, c1, c0
                   # where the polynomial is c2*P^2 + c1*P + c0
                   # note: polynomials can be of any degree, highest
                   # order coefficient always goes first
