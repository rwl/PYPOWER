# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

from numpy import array, zeros, ones, flatnonzero as find

from pypower.opf_slvr import opf_slvr
from pypower.mp_lp import mp_lp


def LPrelax(a, f, b, nequs, vlb, vub, idx_workc, ppopt):
    """@author: Deqiang (David) Gan, PSERC Cornell & Zhejiang University
    """
    ## options
    alg     = ppopt['OPF_ALG_POLY']
    verbose = ppopt['OPF_ALG_POLY']

    if opf_slvr(alg) == 1:
        idx_workc = find(b < 0.001)

    converged = 0
    while converged == 0:

        atemp = a[idx_workc, :]
        btemp = b[idx_workc]

        x2, duals = mp_lp(f, atemp, btemp, vlb, vub, array([]), nequs, -1)

        diffs = b - a * x2                 # diffs should be normalized by what means? under development
        idx_bindc = find(diffs < 1.0e-8)

        idx_violated = find(diffs < -1.0e-8)

        if len(idx_violated) == 0:
            converged = 1
        else:
            flag = zeros(len(b))         # set up flag from scratch
            flag[idx_workc] = ones(len(idx_workc))   # enforce historical working constraints


            idx_add = find(diffs < 0.001)
            flag[idx_add] = ones(len(idx_add))   # enforce violating constraints

            flag[:nequs] = ones(nequs)           # enforce original equality constraints
            idx_workc_new = find(flag)

            if len(idx_workc) == len(idx_workc_new):  # safeguard step
                if len(find(idx_workc - idx_workc_new)) == 0:
                    converged = 1

            idx_workc = idx_workc_new

    duals_rlx = zeros(len(b))
    duals_rlx[idx_workc] = duals[:len(btemp)]

    return x2, duals_rlx, idx_workc, idx_bindc
