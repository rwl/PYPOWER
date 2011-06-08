# Copyright (C) 2004-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

from numpy import array, ones, Inf

from scipy.io import loadmat
from scipy.sparse import csr_matrix as sparse

from pypower.ppoption import ppoption
from pypower.rundcopf import rundcopf
from pypower.loadcase import loadcase

from pypower.idx_bus import \
    BUS_AREA, BASE_KV, VMIN, VM, VA, LAM_P, LAM_Q, MU_VMIN, MU_VMAX

from pypower.idx_gen import \
    GEN_BUS, QMAX, QMIN, MBASE, APF, PG, QG, VG, MU_PMAX, MU_QMIN

from pypower.idx_brch import \
    ANGMAX, PF, QT, MU_SF, MU_ST, MU_ANGMAX, MU_ANGMIN

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end


def t_opf_dc_pips(quiet=False):
    """Tests for DC optimal power flow using PIPS solver.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    num_tests = 23

    t_begin(num_tests, quiet)

    casefile = 't_case9_opf'
    verbose = not quiet

    t0 = 'DC OPF (PIPS): '
    ppopt = ppoption(VERBOSE=verbose, OUT_ALL=0, OPF_ALG_DC=200)

    ## run DC OPF

    ## set up indices
    ib_data     = range(BUS_AREA + 1) + range(BASE_KV, VMIN)
    ib_voltage  = range(VM, VA + 1)
    ib_lam      = range(LAM_P, LAM_Q + 1)
    ib_mu       = range(MU_VMAX, MU_VMIN + 1)
    ig_data     = [GEN_BUS, QMAX, QMIN] + range(MBASE, APF + 1)
    ig_disp     = [PG, QG, VG]
    ig_mu       = range(MU_PMAX, MU_QMIN + 1)
    ibr_data    = range(ANGMAX)
    ibr_flow    = range(PF, QT + 1)
    ibr_mu      = [MU_SF, MU_ST]
    ibr_angmu   = [MU_ANGMIN, MU_ANGMAX]

    ## get solved DC power flow case from MAT-file
    soln9_dcopf = loadmat('soln9_dcopf')       ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_dcopf['bus_soln']
    gen_soln = soln9_dcopf['gen_soln']
    branch_soln = soln9_dcopf['branch_soln']
    f_soln = soln9_dcopf['f_soln']

    ## run OPF
    t = t0
    _, bus, gen, _, branch, f, success, _ = rundcopf(casefile, ppopt)
    t_ok(success, [t, 'success'])
    t_is(f, f_soln, 3, [t, 'f'])
    t_is(   bus[:, ib_data   ],    bus_soln[:, ib_data   ], 10, [t, 'bus data'])
    t_is(   bus[:, ib_voltage],    bus_soln[:, ib_voltage],  3, [t, 'bus voltage'])
    t_is(   bus[:, ib_lam    ],    bus_soln[:, ib_lam    ],  3, [t, 'bus lambda'])
    t_is(   bus[:, ib_mu     ],    bus_soln[:, ib_mu     ],  2, [t, 'bus mu'])
    t_is(   gen[:, ig_data   ],    gen_soln[:, ig_data   ], 10, [t, 'gen data'])
    t_is(   gen[:, ig_disp   ],    gen_soln[:, ig_disp   ],  3, [t, 'gen dispatch'])
    t_is(   gen[:, ig_mu     ],    gen_soln[:, ig_mu     ],  3, [t, 'gen mu'])
    t_is(branch[:, ibr_data  ], branch_soln[:, ibr_data  ], 10, [t, 'branch data'])
    t_is(branch[:, ibr_flow  ], branch_soln[:, ibr_flow  ],  3, [t, 'branch flow'])
    t_is(branch[:, ibr_mu    ], branch_soln[:, ibr_mu    ],  2, [t, 'branch mu'])

    ##-----  run OPF with extra linear user constraints & costs  -----
    ## two new z variables
    ##      0 <= z1, P2 - P1 <= z1
    ##      0 <= z2, P2 - P3 <= z2
    ## with A and N sized for DC opf
    ppc = loadcase(casefile)
    row = [0, 0, 0, 1, 1, 1]
    col = [9, 10, 12, 10, 11, 13]
    ppc.A = sparse(([-1, 1, -1, 1, -1, -1], (row, col)), (2, 14))
    ppc.u = [0, 0]
    ppc.l = [-Inf, -Inf]
    ppc.zl = [0, 0]

    ppc.N = sparse(([1, 1], ([0, 1], [12, 13])), (2, 14))   ## new z variables only
    ppc.fparm = ones((2, 1)) * [1, 0, 0, 1]           ## w = r = z
    ppc.H = sparse((2, 2))                            ## no quadratic term
    ppc.Cw = array([1000, 1])

    t = [t0, 'w/extra constraints & costs 1 : ']
    r, success = rundcopf(ppc, ppopt)
    t_ok(success, [t, 'success'])
    t_is(r.gen[0, PG], 116.15974, 4, [t, 'Pg1 = 116.15974'])
    t_is(r.gen[1, PG], 116.15974, 4, [t, 'Pg2 = 116.15974'])
    t_is(r['var']['val']['z'], [0, 0.3348], 4, [t, 'user vars'])
    t_is(r['cost']['usr'], 0.3348, 3, [t, 'user costs'])

    ## with A and N sized for AC opf
    ppc = loadcase(casefile)
    row = [0, 0, 0, 1, 1, 1]
    col = [18, 19, 24, 19, 20, 25]
    ppc.A = sparse(([-1, 1, -1, 1, -1, -1], (row, col)), (2, 26))
    ppc.u = [0, 0]
    ppc.l = [-Inf, -Inf]
    ppc.zl = [0, 0]

    ppc.N = sparse(([1, 1], ([0, 1], [24, 25])), (2, 26))   ## new z variables only
    ppc.fparm = ones((2, 1)) * [1, 0, 0, 1]           ## w = r = z
    ppc.H = sparse((2, 2))                            ## no quadratic term
    ppc.Cw = array([1000, 1])

    t = [t0, 'w/extra constraints & costs 2 : ']
    r, success = rundcopf(ppc, ppopt)
    t_ok(success, [t, 'success'])
    t_is(r.gen[0, PG], 116.15974, 4, [t, 'Pg1 = 116.15974'])
    t_is(r.gen[1, PG], 116.15974, 4, [t, 'Pg2 = 116.15974'])
    t_is(r['var']['val']['z'], [0, 0.3348], 4, [t, 'user vars'])
    t_is(r['cost']['usr'], 0.3348, 3, [t, 'user costs'])

    t = [t0, 'infeasible : ']
    ## with A and N sized for DC opf
    ppc = loadcase(casefile)
    ppc.A = sparse(([1, 1], ([0, 0], [9, 10])), (1, 14))   ## Pg1 + Pg2
    ppc.u = Inf
    ppc.l = 600
    r, success = rundcopf(ppc, ppopt)
    t_ok(not success, [t, 'no success'])

    t_end
