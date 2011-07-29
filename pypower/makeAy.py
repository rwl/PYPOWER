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

"""Make the A matrix and RHS for the CCV formulation.
"""

from numpy import array, diff, any, zeros, r_, flatnonzero as find
#from scipy.sparse import csr_matrix as sparse
from scipy.sparse import lil_matrix as sparse

from idx_cost import MODEL, PW_LINEAR, NCOST, COST


def makeAy(baseMVA, ng, gencost, pgbas, qgbas, ybas):
    """Make the A matrix and RHS for the CCV formulation.

    Constructs the parameters for linear "basin constraints" on C{Pg}, C{Qg}
    and C{Y} used by the CCV cost formulation, expressed as::

         Ay * x <= by

    where C{x} is the vector of optimization variables. The starting index
    within the C{x} vector for the active, reactive sources and the C{y}
    variables should be provided in arguments C{pgbas}, C{qgbas}, C{ybas}.
    The number of generators is C{ng}.

    Assumptions: All generators are in-service.  Filter any generators
    that are offline from the C{gencost} matrix before calling L{makeAy}.
    Efficiency depends on C{Qg} variables being after C{Pg} variables, and
    the C{y} variables must be the last variables within the vector C{x} for
    the dimensions of the resulting C{Ay} to be conformable with C{x}.

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Richard Lincoln
    """
    ## find all pwl cost rows in gencost, either real or reactive
    iycost = find(gencost[:, MODEL] == PW_LINEAR)

    ## this is the number of extra "y" variables needed to model those costs
    ny = iycost.shape[0]

    if ny == 0:
        Ay = zeros((0, ybas + ny))
        by = array([])
        return Ay, by

    ## if p(i),p(i+1),c(i),c(i+1) define one of the cost segments, then
    ## the corresponding constraint on Pg (or Qg) and Y is
    ##                                             c(i+1) - c(i)
    ##  Y   >=   c(i) + m * (Pg - p(i)),      m = ---------------
    ##                                             p(i+1) - p(i)
    ##
    ## this becomes   m * Pg - Y   <=   m*p(i) - c(i)

    ## Form A matrix.  Use two different loops, one for the PG/Qg coefs,
    ## then another for the y coefs so that everything is filled in the
    ## same order as the compressed column sparse format used by matlab
    ## this should be the quickest.

    m = sum( gencost[iycost, NCOST].astype(int) )  ## total number of cost points
    Ay = sparse((m - ny, ybas + ny))
    by = array([])
    ## First fill the Pg or Qg coefficients (since their columns come first)
    ## and the rhs
    k = 0
    for i in iycost:
        ns = gencost[i, NCOST].astype(int)         ## # of cost points segments = ns-1
        p = gencost[i, COST:COST + 2 * ns:2] / baseMVA
        c = gencost[i, COST + 1:COST + 2 * ns + 1:2]
        m = diff(c) / diff(p)               ## slopes for Pg (or Qg)
        if any(diff(p) == 0):
            print 'makeAy: bad x axis data in row ##i of gencost matrix' % i
        b = m * p[:ns - 1] - c[:ns - 1]        ## and rhs
        by = r_[by,  b]
        if i > ng:
            sidx = qgbas + (i - ng)        ## this was for a q cost
        else:
            sidx = pgbas + i               ## this was for a p cost

        ## FIXME: Bug in SciPy 0.7.2 prevents setting with a sequence
#        Ay[k:k + ns - 1, sidx] = m
        for ii, kk in enumerate(range(k, k + ns - 1)):
            Ay[kk, sidx] = m[ii]

        k = k + ns - 1
    ## Now fill the y columns with -1's
    k = 0
    j = 0
    for i in iycost:
        ns = gencost[i, NCOST].astype(int)
        ## FIXME: Bug in SciPy 0.7.2 prevents setting with a sequence
#        Ay[k:k + ns - 1, ybas + j - 1] = -ones(ns - 1)
        for kk in range(k, k + ns - 1):
            Ay[kk, ybas + j] = -1

        k = k + ns - 1
        j = j + 1

    return Ay.tocsr(), by
