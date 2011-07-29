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

from numpy import array, arange, linalg, r_, flatnonzero as find

from scipy.sparse import hstack

from pypower.opf_slvr import opf_slvr
from pypower.pp_lp import pp_lp
from pypower.LPrelax import LPrelax


def LPsetup(a, f, b, nequs, vlb, vub, idx_workc, ppopt):
    """Solves a LP problem using a callable LP routine.

    The LP problem is defined as follows:

    min     f' * x
    S.T.    a * x =< b
            vlb =< x =< vub

    All of the equality constraints must appear before inequality constraints.
    nequs specifies how many of the constraints are equality constraints.

    The algorithm (set in ppopt) can be set to the following options:

    220  - solve LP using ICS (equality constraints are eliminated)
    240  - solve LP using Iterative Constraint Search (ICS)
           (equality constraints are preserved, typically superior to 220 and 250)
    250  - solve LP with full set of constraints

    @author: Deqiang (David) Gan, PSERC Cornell & Zhejiang University
    @author: Richard Lincoln
    """
    ## options
    alg = ppopt['OPF_ALG_POLY']

    # ----- solve LP directly -----

    if opf_slvr(alg) == 3:           ## sparse LP with full constraints
        x, duals = pp_lp(f, a, b, vlb, vub, array([]), nequs, -1)
        duals = duals[:len(b)]                   # built-in LP solver has more elements in duals than we want
        idx_workc = array([])
        idx_bindc = array([])
        return x, duals, idx_workc, idx_bindc

    # ----- solve LP using constraint relaxation (equality constraints are preserved) ------

    if opf_slvr(alg) == 2:           ## sparse LP with relaxed constraints
        if len(idx_workc) == 0:
            idx_workc = find(b < 1.0e-5)

        x, duals, idx_workc, idx_bindc = LPrelax(a, f, b, nequs, vlb, vub, idx_workc, ppopt)
        return x, duals, idx_workc, idx_bindc

    # ----- solve LP using constraint relaxation (equality constraints are eliminated) ------

    # so opf_slvr(alg) == 1         ## dense LP

    # set up the indicies of variables and constraints

    idx_x1 = arange(nequs - 1)
    idx_x2 = arange(nequs, len(f))
    idx_c1 = arange(nequs - 1)
    idx_c2 = arange(nequs, len(b))

    # eliminate equality constraints

    b1 = b[idx_c1]
    b2 = b[idx_c2]

    a11 = a[idx_c1, idx_x1]
    a12 = a[idx_c1, idx_x2]
    a21 = a[idx_c2, idx_x1]
    a22 = a[idx_c2, idx_x2]

    a11b1 = linalg.solve(a11, b1)
    a11a12 = linalg.solve(a11, a12)

    # set up the reduced LP

    fred = -((f[idx_x1]).T * a11a12).T + f[idx_x2]
    ared =  hstack([-a21 * a11a12 + a22,
         -a11a12,
          a11a12])
    bred =  r_[ b2 - a21 * a11b1,
         vub[idx_x1] - a11b1,
         a11b1 - vlb[idx_x1]]
    vubred = vub[idx_x2]
    vlbred = vlb[idx_x2]
    nequsred = nequs - len(idx_x1)

    # solve the reduced LP problem using constraint relaxation

    if len(idx_workc) == 0:
        idx_workc = find(b2< 1.0e-5)

    x2, dualsred, idx_workc, idx_bindc = LPrelax(ared, fred, bred, nequsred, vlbred, vubred, idx_workc, ppopt)

    # parse the solution of the reduced LP to get the solution of the original LP

    x[idx_x1] = a11b1 - a11a12 * x2
    x[idx_x2] = x2
    x = x.T

    dualsc2 = dualsred[:len(idx_c2)]

    temp = find(dualsc2)
    dualsc1 =  linalg.solve(a11.T, ( -f[idx_x1] - (a21[temp, :]).T * dualsc2[temp] ))

    duals[idx_c1] = dualsc1
    duals[idx_c2] = dualsc2
    duals = duals.T

    return x, duals, idx_workc, idx_bindc
