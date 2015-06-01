# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for PIPS-based AC optimal power flow.
"""

from os.path import dirname, join

from numpy import array, ones, zeros, Inf, r_, ix_, argsort, arange

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

    @author: Ray Zimmerman (PSERC Cornell)
    """
    num_tests = 101

    t_begin(num_tests, quiet)

    tdir = dirname(__file__)
    casefile = join(tdir, 't_case9_opf')
    verbose = 0#not quiet

    t0 = 'PIPS : '
    ppopt = ppoption(OPF_VIOLATION=1e-6, PDIPM_GRADTOL=1e-8,
                   PDIPM_COMPTOL=1e-8, PDIPM_COSTTOL=1e-9)
    ppopt = ppoption(ppopt, OUT_ALL=0, VERBOSE=verbose, OPF_ALG=560)

    ## set up indices
    ib_data     = r_[arange(BUS_AREA + 1), arange(BASE_KV, VMIN + 1)]
    ib_voltage  = arange(VM, VA + 1)
    ib_lam      = arange(LAM_P, LAM_Q + 1)
    ib_mu       = arange(MU_VMAX, MU_VMIN + 1)
    ig_data     = r_[[GEN_BUS, QMAX, QMIN], arange(MBASE, APF + 1)]
    ig_disp     = array([PG, QG, VG])
    ig_mu       = arange(MU_PMAX, MU_QMIN + 1)
    ibr_data    = arange(ANGMAX + 1)
    ibr_flow    = arange(PF, QT + 1)
    ibr_mu      = array([MU_SF, MU_ST])
    ibr_angmu   = array([MU_ANGMIN, MU_ANGMAX])

    ## get solved AC power flow case from MAT-file
    soln9_opf = loadmat(join(tdir, 'soln9_opf.mat'), struct_as_record=True)
    ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf['bus_soln']
    gen_soln = soln9_opf['gen_soln']
    branch_soln = soln9_opf['branch_soln']
    f_soln = soln9_opf['f_soln'][0]

    ## run OPF
    t = t0
    r = runopf(casefile, ppopt)
    bus, gen, branch, f, success = \
            r['bus'], r['gen'], r['branch'], r['f'], r['success']
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
    t = ''.join([t0, '(single-block PWL) : '])
    ppc = loadcase(casefile)
    ppc['gencost'][2, NCOST] = 2
    r = runopf(ppc, ppopt)
    bus, gen, branch, f, success = \
            r['bus'], r['gen'], r['branch'], r['f'], r['success']
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
    soln9_opf_Plim = loadmat(join(tdir, 'soln9_opf_Plim.mat'), struct_as_record=True)
    ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf_Plim['bus_soln']
    gen_soln = soln9_opf_Plim['gen_soln']
    branch_soln = soln9_opf_Plim['branch_soln']
    f_soln = soln9_opf_Plim['f_soln'][0]

    ## run OPF with active power line limits
    t = ''.join([t0, '(P line lim) : '])
    ppopt1 = ppoption(ppopt, OPF_FLOW_LIM=1)
    r = runopf(casefile, ppopt1)
    bus, gen, branch, f, success = \
            r['bus'], r['gen'], r['branch'], r['f'], r['success']
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
    ppc['gencost'] = array([
        [2,   1500, 0,   3,   0.11,    5,   0],
        [2,   2000, 0,   3,   0.085,   1.2, 0],
        [2,   3000, 0,   3,   0.1225,  1,   0]
    ])
    r = runopf(ppc, ppopt)
    bus_soln, gen_soln, branch_soln, f_soln, success = \
            r['bus'], r['gen'], r['branch'], r['f'], r['success']
    branch_soln = branch_soln[:, :MU_ST + 1]

    A = None
    l = array([])
    u = array([])
    nb = ppc['bus'].shape[0]      # number of buses
    ng = ppc['gen'].shape[0]      # number of gens
    thbas = 0;                thend    = thbas + nb
    vbas     = thend;     vend     = vbas + nb
    pgbas    = vend;      pgend    = pgbas + ng
#    qgbas    = pgend;     qgend    = qgbas + ng
    nxyz = 2 * nb + 2 * ng
    N = sparse((ppc['baseMVA'] * ones(ng), (arange(ng), arange(pgbas, pgend))), (ng, nxyz))
    fparm = ones((ng, 1)) * array([[1, 0, 0, 1]])
    ix = argsort(ppc['gen'][:, 0])
    H = 2 * spdiags(ppc['gencost'][ix, 4], 0, ng, ng, 'csr')
    Cw = ppc['gencost'][ix, 5]
    ppc['gencost'][:, 4:7] = 0

    ## run OPF with quadratic gen costs moved to generalized costs
    t = ''.join([t0, 'w/quadratic generalized gen cost : '])
    r = opf(ppc, A, l, u, ppopt, N, fparm, H, Cw)
    f, bus, gen, branch, success = \
            r['f'], r['bus'], r['gen'], r['branch'], r['success']
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
    soln9_opf_extras1 = loadmat(join(tdir, 'soln9_opf_extras1.mat'), struct_as_record=True)
    ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf_extras1['bus_soln']
    gen_soln = soln9_opf_extras1['gen_soln']
    branch_soln = soln9_opf_extras1['branch_soln']
    f_soln = soln9_opf_extras1['f_soln'][0]

    row = [0, 0, 1, 1]
    col = [9, 24, 9, 24]
    A = sparse(([-1, 1, 1, 1], (row, col)), (2, 25))
    u = array([Inf, Inf])
    l = array([-1, 1])

    N = sparse(([1], ([0], [24])), (1, 25))    ## new z variable only
    fparm = array([[1, 0, 0, 1]])              ## w = r = z
    H = sparse((1, 1))                ## no quadratic term
    Cw = array([100.0])

    t = ''.join([t0, 'w/extra constraints & costs 1 : '])
    r = opf(casefile, A, l, u, ppopt, N, fparm, H, Cw)
    f, bus, gen, branch, success = \
            r['f'], r['bus'], r['gen'], r['branch'], r['success']
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
    ppc = loadcase(join(tdir, 't_case9_opfv2'))
    ## remove angle diff limits
    ppc['branch'][0, ANGMAX] =  360
    ppc['branch'][8, ANGMIN] = -360

    ## get solved AC power flow case from MAT-file
    soln9_opf_PQcap = loadmat(join(tdir, 'soln9_opf_PQcap.mat'), struct_as_record=True)
    ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf_PQcap['bus_soln']
    gen_soln = soln9_opf_PQcap['gen_soln']
    branch_soln = soln9_opf_PQcap['branch_soln']
    f_soln = soln9_opf_PQcap['f_soln'][0]

    ## run OPF with capability curves
    t = ''.join([t0, 'w/capability curves : '])
    r = runopf(ppc, ppopt)
    bus, gen, branch, f, success = \
            r['bus'], r['gen'], r['branch'], r['f'], r['success']
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
    ppc = loadcase(join(tdir, 't_case9_opfv2'))
    ## remove capability curves
    ppc['gen'][ix_(arange(1, 3),
                   [PC1, PC2, QC1MIN, QC1MAX, QC2MIN, QC2MAX])] = zeros((2, 6))

    ## get solved AC power flow case from MAT-file
    soln9_opf_ang = loadmat(join(tdir, 'soln9_opf_ang.mat'), struct_as_record=True)
    ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf_ang['bus_soln']
    gen_soln = soln9_opf_ang['gen_soln']
    branch_soln = soln9_opf_ang['branch_soln']
    f_soln = soln9_opf_ang['f_soln'][0]

    ## run OPF with angle difference limits
    t = ''.join([t0, 'w/angle difference limits : '])
    r = runopf(ppc, ppopt)
    bus, gen, branch, f, success = \
            r['bus'], r['gen'], r['branch'], r['f'], r['success']
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
    soln9_opf = loadmat(join(tdir, 'soln9_opf.mat'), struct_as_record=True)
    ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_opf['bus_soln']
    gen_soln = soln9_opf['gen_soln']
    branch_soln = soln9_opf['branch_soln']
    f_soln = soln9_opf['f_soln'][0]

    ## run OPF with ignored angle difference limits
    t = ''.join([t0, 'w/ignored angle difference limits : '])
    ppopt1 = ppoption(ppopt, OPF_IGNORE_ANG_LIM=1)
    r = runopf(ppc, ppopt1)
    bus, gen, branch, f, success = \
            r['bus'], r['gen'], r['branch'], r['f'], r['success']
    ## ang limits are not in this solution data, so let's remove them
    branch[0, ANGMAX] =  360
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

    t_end()


if __name__ == '__main__':
    t_opf_pips(quiet=False)
