# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for DC optimal power flow using PIPS solver.
"""

from os.path import dirname, join

from numpy import array, ones, Inf, arange, r_

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
    ANGMAX, PF, QT, MU_SF, MU_ST

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end


def t_opf_dc_pips(quiet=False):
    """Tests for DC optimal power flow using PIPS solver.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    num_tests = 23

    t_begin(num_tests, quiet)

    tdir = dirname(__file__)
    casefile = join(tdir, 't_case9_opf')
    verbose = 0#not quiet

    t0 = 'DC OPF (PIPS): '
    ppopt = ppoption(VERBOSE=verbose, OUT_ALL=0, OPF_ALG_DC=200)

    ## run DC OPF

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
    #ibr_angmu   = array([MU_ANGMIN, MU_ANGMAX])

    ## get solved DC power flow case from MAT-file
    soln9_dcopf = loadmat(join(tdir, 'soln9_dcopf.mat'), struct_as_record=True)
    ## defines bus_soln, gen_soln, branch_soln, f_soln
    bus_soln = soln9_dcopf['bus_soln']
    gen_soln = soln9_dcopf['gen_soln']
    branch_soln = soln9_dcopf['branch_soln']
    f_soln = soln9_dcopf['f_soln'][0]

    ## run OPF
    t = t0
    r = rundcopf(casefile, ppopt)
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

    ##-----  run OPF with extra linear user constraints & costs  -----
    ## two new z variables
    ##      0 <= z1, P2 - P1 <= z1
    ##      0 <= z2, P2 - P3 <= z2
    ## with A and N sized for DC opf
    ppc = loadcase(casefile)
    row = [0, 0, 0, 1, 1, 1]
    col = [9, 10, 12, 10, 11, 13]
    ppc['A'] = sparse(([-1, 1, -1, 1, -1, -1], (row, col)), (2, 14))
    ppc['u'] = array([0, 0])
    ppc['l'] = array([-Inf, -Inf])
    ppc['zl'] = array([0, 0])

    ppc['N'] = sparse(([1, 1], ([0, 1], [12, 13])), (2, 14))   ## new z variables only
    ppc['fparm'] = ones((2, 1)) * array([[1, 0, 0, 1]])           ## w = r = z
    ppc['H'] = sparse((2, 2))                            ## no quadratic term
    ppc['Cw'] = array([1000, 1])

    t = ''.join([t0, 'w/extra constraints & costs 1 : '])
    r = rundcopf(ppc, ppopt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['gen'][0, PG], 116.15974, 4, [t, 'Pg1 = 116.15974'])
    t_is(r['gen'][1, PG], 116.15974, 4, [t, 'Pg2 = 116.15974'])
    t_is(r['var']['val']['z'], [0, 0.3348], 4, [t, 'user vars'])
    t_is(r['cost']['usr'], 0.3348, 3, [t, 'user costs'])

    ## with A and N sized for AC opf
    ppc = loadcase(casefile)
    row = [0, 0, 0, 1, 1, 1]
    col = [18, 19, 24, 19, 20, 25]
    ppc['A'] = sparse(([-1, 1, -1, 1, -1, -1], (row, col)), (2, 26))
    ppc['u'] = array([0, 0])
    ppc['l'] = array([-Inf, -Inf])
    ppc['zl'] = array([0, 0])

    ppc['N'] = sparse(([1, 1], ([0, 1], [24, 25])), (2, 26))   ## new z variables only
    ppc['fparm'] = ones((2, 1)) * array([[1, 0, 0, 1]])        ## w = r = z
    ppc['H'] = sparse((2, 2))                            ## no quadratic term
    ppc['Cw'] = array([1000, 1])

    t = ''.join([t0, 'w/extra constraints & costs 2 : '])
    r = rundcopf(ppc, ppopt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['gen'][0, PG], 116.15974, 4, [t, 'Pg1 = 116.15974'])
    t_is(r['gen'][1, PG], 116.15974, 4, [t, 'Pg2 = 116.15974'])
    t_is(r['var']['val']['z'], [0, 0.3348], 4, [t, 'user vars'])
    t_is(r['cost']['usr'], 0.3348, 3, [t, 'user costs'])

    t = ''.join([t0, 'infeasible : '])
    ## with A and N sized for DC opf
    ppc = loadcase(casefile)
    ppc['A'] = sparse(([1, 1], ([0, 0], [9, 10])), (1, 14))   ## Pg1 + Pg2
    ppc['u'] = array([Inf])
    ppc['l'] = array([600])
    r = rundcopf(ppc, ppopt)
    t_ok(not r['success'], [t, 'no success'])

    t_end()


if __name__ == '__main__':
    t_opf_dc_pips(quiet=False)
