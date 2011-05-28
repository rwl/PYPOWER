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

from numpy import array, ones, zeros, Inf, r_, argsort

from scipy.io import loadmat
from scipy.sparse import spdiags, csr_matrix as sparse

from pypower.ppoption import ppoption
from pypower.runopf import runopf
from pypower.loadcase import loadcase
from pypower.opf import opf

from pypower.idx_bus import \
    BUS_AREA, BASE_KV, VMIN, VM, VA, LAM_P, LAM_Q, MU_VMIN, MU_VMAX

from pypower.idx_gen import \
    GEN_BUS, QMAX, QMIN, MBASE, APF, PG, QG, VG, MU_PMAX, MU_QMIN, \
    PC1, PC2, QC1MIN, QC1MAX, QC2MIN, QC2MAX

from pypower.idx_brch import \
    ANGMAX, PF, QT, MU_SF, MU_ST, MU_ANGMAX, MU_ANGMIN, ANGMIN

from pypower.idx_cost import NCOST

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end

def t_opf_pips(quiet=False):
    """Tests for PIPS-based AC optimal power flow.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    num_tests = 101

    t_begin(num_tests, quiet)

    casefile = 't_case9_opf'
    verbose = not quiet

    t0 = 'PIPS : '
    opt = ppoption
    opt['OPF_VIOLATION'] = 1e-6
    opt['PDIPM_GRADTOL'] = 1e-8
    opt['PDIPM_COMPTOL'] = 1e-8
    opt['PDIPM_COSTTOL'] = 1e-9
    opt['OUT_ALL'] = 0
    opt['VERBOSE'] = verbose
    opt['OPF_ALG'] = 560

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

    ## get solved AC power flow case from MAT-file
    soln9_opf = loadmat('soln9_opf')       ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf['bus_soln']
    gen_soln = soln9_opf['gen_soln']
    branch_soln = soln9_opf['branch_soln']
    f_soln = soln9_opf['f_soln']

    ## run OPF
    t = t0
    _, bus, gen, _, branch, f, success, _ = runopf(casefile, opt)
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

    ## run with automatic conversion of single-block pwl to linear costs
    t = [t0, '(single-block PWL) : '];
    ppc = loadcase(casefile)
    ppc.gencost[2, NCOST] = 2
    r = runopf(ppc, opt)
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
    xr = r_[r['var']['val']['Va'], r['var']['val']['Vm'], r['var']['val']['Pg'],
            r['var']['val']['Qg'], 0, r['var']['val']['y']]
    t_is(r['x'], xr, 8, [t, 'check on raw x returned from OPF'])

    ## get solved AC power flow case from MAT-file
    soln9_opf_Plim = loadmat('soln9_opf_Plim')       ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf_Plim['bus_soln']
    gen_soln = soln9_opf_Plim['gen_soln']
    branch_soln = soln9_opf_Plim['branch_soln']
    f_soln = soln9_opf_Plim['f_soln']

    ## run OPF with active power line limits
    t = [t0, '(P line lim) : ']
    opt1 = opt.copy()
    opt1['OPF_FLOW_LIM'] = 1
    _, bus, gen, _, branch, f, success, _ = runopf(casefile, opt1)
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

    ##-----  test OPF with quadratic gen costs moved to generalized costs  -----
    ppc = loadcase(casefile)
    ppc.gencost = array([
        [2,   1500, 0,   3,   0.11,    5,   0],
        [2,   2000, 0,   3,   0.085,   1.2, 0],
        [2,   3000, 0,   3,   0.1225,  1,   0]
    ])
    _, bus_soln, gen_soln, _, branch_soln, f_soln, success, _ = \
            runopf(ppc, opt)
    branch_soln = branch_soln[:, 0:MU_ST]

    A = sparse((0, 0))
    l = array([])
    u = array([])
    nb = ppc.bus.shape[0]      # number of buses
    ng = ppc.gen.shape[0]      # number of gens
    thbas = 0;                thend    = thbas + nb - 1
    vbas     = thend + 1;     vend     = vbas + nb - 1
    pgbas    = vend + 1;      pgend    = pgbas + ng - 1
#    qgbas    = pgend + 1;     qgend    = qgbas + ng - 1
    nxyz = 2 * nb + 2 * ng
    N = sparse((ppc.baseMVA * ones(ng), (range(ng), range(pgbas, pgend + 1))), (ng, nxyz))
    fparm = ones(ng) * [1, 0, 0, 1]
    ix = argsort(ppc.gen[:, 0])
    H = 2 * spdiags(ppc.gencost[ix, 4], 0, ng, ng, 'csr')
    Cw = ppc.gencost[ix, 5]
    ppc.gencost[:, 4:6] = 0

    ## run OPF with quadratic gen costs moved to generalized costs
    t = [t0, 'w/quadratic generalized gen cost : ']
    r, success = opf(ppc, A, l, u, opt, N, fparm, H, Cw)
    f, bus, gen, branch = r['f'], r['bus'], r['gen'], r['branch']
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
    t_is(r['cost']['usr'], f, 12, [t, 'user cost'])

    ##-----  run OPF with extra linear user constraints & costs  -----
    ## single new z variable constrained to be greater than or equal to
    ## deviation from 1 pu voltage at bus 1, linear cost on this z
    ## get solved AC power flow case from MAT-file
    soln9_opf_extras1 = loadmat('soln9_opf_extras1')       ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf_extras1['bus_soln']
    gen_soln = soln9_opf_extras1['gen_soln']
    branch_soln = soln9_opf_extras1['branch_soln']
    f_soln = soln9_opf_extras1['f_soln']

    row = [1, 1, 2, 2]
    col = [10, 25, 10, 25]
    A = sparse(([-1, 1, 1, 1], (row, col)), (2, 25))
    u = array([Inf, Inf])
    l = array([-1, 1])

    N = sparse(([1], ([0], [25])), (1, 25))    ## new z variable only
    fparm = array([1, 0, 0, 1])              ## w = r = z
    H = sparse((1, 1))                ## no quadratic term
    Cw = 100

    t = [t0, 'w/extra constraints & costs 1 : ']
    r, success = opf(casefile, A, l, u, opt, N, fparm, H, Cw)
    f, bus, gen, branch = r['f'], r['bus'], r['gen'], r['branch']
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
    t_is(r['var']['val']['z'], 0.025419, 6, [t, 'user variable'])
    t_is(r['cost']['usr'], 2.5419, 4, [t, 'user cost'])

    ##-----  test OPF with capability curves  -----
    ppc = loadcase('t_case9_opfv2')
    ## remove angle diff limits
    ppc.branch[0, ANGMAX] = 360
    ppc.branch[8, ANGMIN] = -360

    ## get solved AC power flow case from MAT-file
    soln9_opf_PQcap = loadmat('soln9_opf_PQcap')       ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf_PQcap['bus_soln']
    gen_soln = soln9_opf_PQcap['gen_soln']
    branch_soln = soln9_opf_PQcap['branch_soln']
    f_soln = soln9_opf_PQcap['f_soln']

    ## run OPF with capability curves
    t = [t0, 'w/capability curves : ']
    _, bus, gen, _, branch, f, success, _ = runopf(ppc, opt)
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

    ##-----  test OPF with angle difference limits  -----
    ppc = loadcase('t_case9_opfv2')
    ## remove capability curves
    ppc.gen[1:3, [PC1, PC2, QC1MIN, QC1MAX, QC2MIN, QC2MAX]] = zeros((2, 6))

    ## get solved AC power flow case from MAT-file
    soln9_opf_ang = loadmat('soln9_opf_ang')       ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf_ang['bus_soln']
    gen_soln = soln9_opf_ang['gen_soln']
    branch_soln = soln9_opf_ang['branch_soln']
    f_soln = soln9_opf_ang['f_soln']

    ## run OPF with angle difference limits
    t = [t0, 'w/angle difference limits : ']
    _, bus, gen, _, branch, f, success, _ = runopf(ppc, opt)
    t_ok(success, [t, 'success'])
    t_is(f, f_soln, 3, [t, 'f'])
    t_is(   bus[:, ib_data   ],    bus_soln[:, ib_data   ], 10, [t, 'bus data'])
    t_is(   bus[:, ib_voltage],    bus_soln[:, ib_voltage],  3, [t, 'bus voltage'])
    t_is(   bus[:, ib_lam    ],    bus_soln[:, ib_lam    ],  3, [t, 'bus lambda'])
    t_is(   bus[:, ib_mu     ],    bus_soln[:, ib_mu     ],  1, [t, 'bus mu'])
    t_is(   gen[:, ig_data   ],    gen_soln[:, ig_data   ], 10, [t, 'gen data'])
    t_is(   gen[:, ig_disp   ],    gen_soln[:, ig_disp   ],  3, [t, 'gen dispatch'])
    t_is(   gen[:, ig_mu     ],    gen_soln[:, ig_mu     ],  3, [t, 'gen mu'])
    t_is(branch[:, ibr_data  ], branch_soln[:, ibr_data  ], 10, [t, 'branch data'])
    t_is(branch[:, ibr_flow  ], branch_soln[:, ibr_flow  ],  3, [t, 'branch flow'])
    t_is(branch[:, ibr_mu    ], branch_soln[:, ibr_mu    ],  2, [t, 'branch mu'])
    t_is(branch[:, ibr_angmu ], branch_soln[:, ibr_angmu ],  2, [t, 'branch angle mu'])

    ##-----  test OPF with ignored angle difference limits  -----
    ## get solved AC power flow case from MAT-file
    soln9_opf = loadmat('soln9_opf')       ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf['bus_soln']
    gen_soln = soln9_opf['gen_soln']
    branch_soln = soln9_opf['branch_soln']
    f_soln = soln9_opf['f_soln']

    ## run OPF with ignored angle difference limits
    t = [t0, 'w/ignored angle difference limits : ']
    opt1 = opt.copy()
    opt['OPF_IGNORE_ANG_LIM'] = 1
    _, bus, gen, _, branch, f, success, _ = runopf(ppc, opt1)
    ## ang limits are not in this solution data, so let's remove them
    branch[0, ANGMAX] = 360
    branch[8, ANGMIN] = -360
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

    t_end
