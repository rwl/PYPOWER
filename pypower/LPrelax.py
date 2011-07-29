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

from numpy import array, zeros, ones, flatnonzero as find

from pypower.opf_slvr import opf_slvr
from pypower.pp_lp import pp_lp


def LPrelax(a, f, b, nequs, vlb, vub, idx_workc, ppopt):
    """
    @author: Deqiang (David) Gan, PSERC Cornell & Zhejiang University
    @author: Richard Lincoln
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

        x2, duals = pp_lp(f, atemp, btemp, vlb, vub, array([]), nequs, -1)

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
