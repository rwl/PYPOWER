# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for code in auction.py, using PIPS solver.
"""

from numpy import array, copy, ones, diag, flatnonzero as find
from scipy.sparse import csr_matrix as sparse

from pypower.ppoption import ppoption

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is


def t_auction_pips(quiet=False):
    """Tests for code in auction.py, using PIPS solver.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    n_tests = 183

    t_begin(n_tests, quiet)

    try:
        from pypower.extras.smartmarket import runmkt
    except ImportError:
        t_skip(n_tests, 'smartmarket code not available')
        return

    ppopt = ppoption
    ppopt['OPF_VIOLATION'] = 1e-7
    ppopt['PDIPM_GRADTOL'] = 1e-6
    ppopt['PDIPM_COMPTOL'] = 1e-7
    ppopt['PDIPM_COSTTOL'] = 5e-9
    ppopt['OPF_ALG'] = 560
    ppopt['OUT_ALL_LIM'] = 1
    ppopt['OUT_BRANCH'] = 0
    ppopt['OUT_SYS_SUM'] = 0
    ppopt['OUT_ALL'] = 0
    ppopt['VERBOSE'] = 0
    q = array([
        [12, 24, 24],
        [12, 24, 24],
        [12, 24, 24],
        [12, 24, 24],
        [12, 24, 24],
        [12, 24, 24],
        [10, 10, 10],
        [10, 10, 10],
        [10, 10, 10],
    ])

    ##-----  one offer block marginal @ $50  -----
    p = array([
        [20, 50, 60],
        [20, 40, 70],
        [20, 42, 80],
        [20, 44, 90],
        [20, 46, 75],
        [20, 48, 60],
        [100, 70, 60],
        [100, 50, 20],
        [100, 60, 50]
    ])

    t = 'one marginal offer @ $50, auction_type = 5'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1150, 100, [], [], mpopt)
    cq5 = cq.copy()
    cp5 = cp.copy()
    i2e = bus.bus_i
    e2i = sparse((max(i2e), 1))
    e2i[i2e] = range(bus.size())
    G = find( isload(gen) == False )   ## real generators
    L = find( isload(gen) )   ## dispatchable loads
    Gbus = e2i[gen.gen_bus[G]]
    Lbus = e2i[gen.gen_bus[L]]
    Qfudge = zeros(p.shape)
    Qfudge[L, :] = \
        diag(gen.Qg[L] / gen.Pg[L] * bus.lam_Q[Lbus]) * ones(p[L :].shape)

    t_is( cq[G[0], 1:3], [23.32, 0], 2, t )
    t_is( cp[G[0], :], 50, 4, t )
    t_is( cq[L[1], 0:2], [10, 0], 2, t )
    t_is( cp[L[1], :], 54.0312, 4, t )
    t_is( cp[G, 0], bus.lam_P[Gbus], 8, [t, ' : gen prices'] )
    t_is( cp[L, 0], bus.lam_P[Lbus] + Qfudge[L, 0], 8, [t, ' : load prices'] )

    lao_X = p(G[0], 1) / bus.lam_P[Gbus[0], LAM_P]
    fro_X = p(G(5), 2) / bus.lam_P[Gbus[5], LAM_P]
    lab_X = p(L(2), 1) / (bus.lam_P[Lbus[2]] + Qfudge[L[2], 0])
    frb_X = p(L(1), 1) / (bus.lam_P[Lbus[1]] + Qfudge[L[1], 0])

    t_is( lao_X, 1, 4, 'lao_X')
    t_is( fro_X, 1.1324, 4, 'fro_X')
    t_is( lab_X, 1.0787, 4, 'lab_X')
    t_is( frb_X, 0.9254, 4, 'frb_X')

    t = 'one marginal offer @ $50, auction_type = 1'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1110, 100, [], [], mpopt)
    cp1 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5, 6, [t, ' : prices'] )

    t = 'one marginal offer @ $50, auction_type = 2'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1120, 100, [], [], mpopt)
    cp2 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G, :], cp5[G, :] * fro_X, 8, [t, ' : gen prices'] )
    t_is( cp[L[0:1], :], cp5[L[0:1], :] * fro_X, 8, [t, ' : load 1,2 prices'] )
    t_is( cp[L[2], :], 60, 5, [t, ' : load 3 price'] )   ## clipped by accepted bid

    t = 'one marginal offer @ $50, auction_type = 3'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1130, 100, [], [], mpopt)
    cp3 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5 * lab_X, 8, [t, ' : prices'] )

    t = 'one marginal offer @ $50, auction_type = 4'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1140, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G[0], :], p[G[0], 1], 8, [t, ' : gen 1 price'] )
    t_is( cp[G[1:6], :], cp5[G[1:6], :] * frb_X, 8, [t, ' : gen 2-6 prices'] )
    t_is( cp[L, :], cp5[L, :] * frb_X, 8, [t, ' : load prices'] )

    t = 'one marginal offer @ $50, auction_type = 6'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1160, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp3, 8, [t, ' : prices'] )
    p2 = p.copy()
    p2[L, :] = array([
        [100, 100, 100],
        [100,   0,   0],
        [100, 100,   0]
    ])
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1160, 100, [], [], mpopt)
    t_is( cq, cq5, 5, [t, ' : quantities'] )
    t_is( cp[G, :], cp5[G, :] * fro_X, 4, [t, ' : gen prices'] )
    t_is( cp[L, :], cp5[L, :] * fro_X, 4, [t, ' : load prices'] ) ## load 3 not clipped as in FRO

    t = 'one marginal offer @ $50, auction_type = 7'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1170, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5 * (lao_X + lab_X) / 2, 8, [t, ' : prices'] )
    t_is( cp, (cp1 + cp3) / 2, 8, [t, ' : prices'] )

    t = 'one marginal offer @ $50, auction_type = 8'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1180, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G, :], cp1[G, :], 8, [t, ' : gen prices'] )
    t_is( cp[L, :], cp3[L, :], 8, [t, ' : load prices'] )

    t = 'one marginal offer @ $50, auction_type = 0'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1100, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, p, 8, [t, ' : prices'] )


    ##-----  one bid block marginal @ $55  -----
    p[L[1], 1] = 55
    t = 'one marginal bid @ $55, auction_type = 5'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1150, 100, [], [], mpopt)
    cq5 = cq.copy()
    cp5 = cp.copy()
    Qfudge =  zeros(p.shape)
    Qfudge[L, :] = diag(gen.Qg[L] / gen.Pg[L] * bus.lam_Q[Lbus]) * ones(p[L, :].shape)

    t_is( cq[G[0], 1:3], [24, 0], 2, t )
    t_is( cp[G[0], :], 50.016, 3, t )
    t_is( cq[L[1], 0:2], [10, 0.63], 2, t )
    t_is( cp[L[1], :], 55, 4, t )
    t_is( cp[G, 0], bus.lam_P[Gbus], 8, [t, ' : gen prices'] )
    t_is( cp[L, 0], bus.lam_P[Lbus] + Qfudge[L, 0], 8, [t, ' : load prices'] )

    lao_X = p[G[0], 1] / bus.lam_P[Gbus[0]]
    fro_X = p[G[5], 2] / bus.lam_P[Gbus[5]]
    lab_X = p[L[1], 1] / (bus.lam_P[Lbus[1]] + Qfudge[L[1], 0])
    frb_X = p[L[2], 2] / (bus.lam_P[Lbus[2]] + Qfudge[L[2], 0])

    t_is( lao_X, 0.9997, 4, 'lao_X')
    t_is( fro_X, 1.1111, 4, 'fro_X')
    t_is( lab_X, 1, 4, 'lab_X')
    t_is( frb_X, 0.8960, 4, 'frb_X')

    t = 'one marginal bid @ $55, auction_type = 1'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1110, 100, [], [], mpopt)
    cp1 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5 * lao_X, 8, [t, ' : prices'] )

    t = 'one marginal bid @ $55, auction_type = 2'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1120, 100, [], [], mpopt)
    cp2 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G, :], cp5[G, :] * fro_X, 8, [t, ' : gen prices'] )
    t_is( cp[L[0], :], cp5[L[0], :] * fro_X, 8, [t, ' : load 1 price'] )
    t_is( cp[L[1], :], 55, 5, [t, ' : load 2 price'] )
    t_is( cp[L[2], :], 60, 5, [t, ' : load 3 price'] )

    t = 'one marginal bid @ $55, auction_type = 3'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1130, 100, [], [], mpopt)
    cp3 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5, 7, [t, ' : prices'] )

    t = 'one marginal bid @ $55, auction_type = 4'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1140, 100, [], [], mpopt)
    cp4 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G[0], :], 50, 5, [t, ' : gen 1 price'] )
    t_is( cp[G[1:6], :], cp5[G[1:6], :] * frb_X, 8, [t, ' : gen 2-6 prices'] )
    t_is( cp[L, :], cp5[L, :] * frb_X, 8, [t, ' : load prices'] )

    t = 'one marginal bid @ $55, auction_type = 6'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1160, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp1, 8, [t, ' : prices'] )

    p2 = p.copy()
    p2[G, :] = array([
        [0, 0, 100],
        [0, 0, 100],
        [0, 0, 100],
        [0, 0, 100],
        [0, 0, 100],
        [0, 0, 100]
    ])
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1160, 100, [], [], mpopt)
    t_is( cq, cq5, 3, [t, ' : quantities'] )
    t_is( cp[G, :], cp5[G, :] * frb_X, 3, [t, ' : gen prices'] )  ## gen 1, not clipped this time
    t_is( cp[L, :], cp4[L, :], 3, [t, ' : load prices'] )

    t = 'one marginal bid @ $55, auction_type = 7'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1170, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5 * (lao_X + lab_X) / 2, 8, [t, ' : prices'] )
    t_is( cp, (cp1 + cp3) / 2, 8, [t, ' : prices'] )

    t = 'one marginal bid @ $55, auction_type = 8'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1180, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G, :], cp1[G, :], 8, [t, ' : gen prices'] )
    t_is( cp[L, :], cp3[L, :], 8, [t, ' : load prices'] )

    t = 'one marginal bid @ $55, auction_type = 0'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1100, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, p, 8, [t, ' : prices'] )


    ##-----  one bid block marginal @ $54.50 and one offer block marginal @ $50  -----
    p[L[1], 1] = 54.5
    t = 'marginal offer @ $50, bid @ $54.50, auction_type = 5'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1150, 100, [], [], mpopt)
    cq5 = cq.copy()
    cp5 = cp.copy()
    Qfudge =  zeros(p.shape)
    Qfudge[L, :] = diag(gen.Qg[L] / gen.Pg[L] * bus.lam_Q[Lbus]) * ones(p[L, :].shape)

    t_is( cq[G[0], 1:3], [23.74, 0], 2, t )
    t_is( cp[G[0], :], 50, 4, t )
    t_is( cq[L[1], 0:2], [10, 0.39], 2, t )
    t_is( cp[L[1], :], 54.5, 4, t )
    t_is( cp[G, 0], bus.lam_P[Gbus], 8, [t, ' : gen prices'] )
    t_is( cp[L, 0], bus.lam_P[Lbus] + Qfudge[L, 0], 8, [t, ' : load prices'] )

    lao_X = p[G[0], 1] / bus.lam_P[Gbus[0]]
    fro_X = p[G[5], 2] / bus.lam_P[Gbus[5]]
    lab_X = p[L[1], 1] / (bus.lam_P[Lbus[1]] + Qfudge[L[1], 0])
    frb_X = p[L[2], 2] / (bus.lam_P[Lbus[2]] + Qfudge[L[2], 0])

    t_is( lao_X, 1, 4, 'lao_X')
    t_is( fro_X, 1.1221, 4, 'fro_X')
    t_is( lab_X, 1, 4, 'lab_X')
    t_is( frb_X, 0.8976, 4, 'frb_X')

    t = 'marginal offer @ $50, bid @ $54.50, auction_type = 1'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1110, 100, [], [], mpopt)
    cp1 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5, 4, [t, ' : prices'] )

    t = 'marginal offer @ $50, bid @ $54.50, auction_type = 2'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1120, 100, [], [], mpopt)
    cp2 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G, :], cp5[G, :] * fro_X, 5, [t, ' : gen prices'] )
    t_is( cp[L[0], :], cp5[L[0], :] * fro_X, 5, [t, ' : load 1 price'] )
    t_is( cp[L[1], :], 54.5, 5, [t, ' : load 2 price'] )
    t_is( cp[L[2], :], 60, 5, [t, ' : load 3 price'] )

    t = 'marginal offer @ $50, bid @ $54.50, auction_type = 3'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1130, 100, [], [], mpopt)
    cp3 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5, 6, [t, ' : prices'] )

    t = 'marginal offer @ $50, bid @ $54.50, auction_type = 4'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1140, 100, [], [], mpopt)
    cp4 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G[0], :], 50, 5, [t, ' : gen 1 price'] )
    t_is( cp[G[1:5], :], cp5[G[1:5], :] * frb_X, 8, [t, ' : gen 2-5 prices'] )
    t_is( cp[G[5], :], 48, 5, [t, ' : gen 6 price'] )
    t_is( cp[L, :], cp5[L, :] * frb_X, 8, [t, ' : load prices'] )

    t = 'marginal offer @ $50, bid @ $54.50, auction_type = 6'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1160, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5, 4, [t, ' : prices'] )

    t = 'marginal offer @ $50, bid @ $54.50, auction_type = 7'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1170, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5, 4, [t, ' : prices'] )

    t = 'marginal offer @ $50, bid @ $54.50, auction_type = 8'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1180, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5, 4, [t, ' : prices'] )

    t = 'marginal offer @ $50, bid @ $54.50, auction_type = 0'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1100, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, p, 8, [t, ' : prices'] )


    ##-----  gen 1 at Pmin, load 3 block 2 marginal @ $60  -----
    t = 'gen 1 @ Pmin, marginal bid @ $60, auction_type = 5'
    p[L[1], 1] = 50     ## undo previous change
    p2 = p.copy()
    p2[G[0], 1:3] = [65, 65]
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1150, 100, [], [], mpopt)
    Qfudge =  zeros(p.shape)
    Qfudge[L, :] = diag(gen.Qg[L] / gen.Pg[L] * bus.lam_Q[Lbus]) * ones(p[L, :].shape)

    t_is( cp[G[0], :], 65, 4, [t, ' : gen 1 price'] )
    t_is( cp[G[1], :], 54.2974, 4, [t, ' : gen 2 price'] )
    cq5 = cq.copy()
    cp5 = cp.copy()
    cp_lam = cp5.copt()
    cp_lam[0, :] = bus.lam_P[Gbus[0]]  ## unclipped

    lao_X = p2[G[5], 1] / bus.lam_P[Gbus[5]]
    fro_X = p2[G[5], 2] / bus.lam_P[Gbus[5]]
    lab_X = p2[L[2], 1] / (bus.lam_P[Lbus[2]] + Qfudge[L[2], 0])
    frb_X = p2[L[1], 1] / (bus.lam_P[Lbus[1]] + Qfudge[L[1], 0])

    t_is( lao_X, 0.8389, 4, 'lao_X')
    t_is( fro_X, 1.0487, 4, 'fro_X')
    t_is( lab_X, 1, 4, 'lab_X')
    t_is( frb_X, 0.8569, 4, 'frb_X')

    t = 'gen 1 @ Pmin, marginal bid @ $60, auction_type = 1'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1110, 100, [], [], mpopt)
    cp1 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G[0], :], 65, 8, [t, ' : gen 1 price'] )
    t_is( cp[G[1:6], :], cp_lam[G[1:6], :] * lao_X, 8, [t, ' : gen 2-6 prices'] )
    t_is( cp[L, :], cp_lam[L, :] * lao_X, 8, [t, ' : load prices'] )

    t = 'gen 1 @ Pmin, marginal bid @ $60, auction_type = 2'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1120, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G[0], :], 65, 8, [t, ' : gen 1 price'] )
    t_is( cp[G[1:6], :], cp_lam[G[1:6], :] * fro_X, 8, [t, ' : gen 2-6 prices'] )
    t_is( cp[L[0:2], :], cp_lam[L[0:2], :] * fro_X, 8, [t, ' : load 1-2 prices'] )
    t_is( cp[L[2], :], 60, 8, [t, ' : load 3 price'] )

    t = 'gen 1 @ Pmin, marginal bid @ $60, auction_type = 3'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1130, 100, [], [], mpopt)
    cp3 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G[0], :], 65, 8, [t, ' : gen 1 price'] )
    t_is( cp[G[1:6], :], cp_lam[G[1:6], :], 6, [t, ' : gen 2-6 prices'] )
    t_is( cp[L, :], cp_lam[L, :], 6, [t, ' : load prices'] )

    t = 'gen 1 @ Pmin, marginal bid @ $60, auction_type = 4'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1140, 100, [], [], mpopt)
    cp4 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G[0], :], 65, 5, [t, ' : gen 1 price'] )
    t_is( cp[G[1:6], :], cp5[G[1:6], :] * frb_X, 8, [t, ' : gen 2-6 prices'] )
    t_is( cp[L, :], cp5[L, :] * frb_X, 8, [t, ' : load prices'] )

    t = 'gen 1 @ Pmin, marginal bid @ $60, auction_type = 6'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1160, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp4, 8, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal bid @ $60, auction_type = 7'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1170, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G[0], :], 65, 4, [t, ' : gen 1 price'] )
    t_is( cp[G[1:6], :], cp_lam[G[1:6], :] * (lao_X + lab_X) / 2, 8, [t, ' : gen 2-6 prices'] )
    t_is( cp[L, :], cp_lam[L, :] * (lao_X + lab_X) / 2, 8, [t, ' : load prices'] )
    t_is( cp, (cp1 + cp3) / 2, 8, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal bid @ $60, auction_type = 8'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1180, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G, :], cp1[G, :], 8, [t, ' : prices'] )
    t_is( cp[L, :], cp3[L, :], 8, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal bid @ $60, auction_type = 0'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1100, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, p2, 8, [t, ' : prices'] )


    ##-----  gen 1 at Pmin, gen 6 block 3 marginal @ $60  -----
    t = 'gen 1 @ Pmin, marginal offer @ $60, auction_type = 5'
    p2[L, :] = array([
        [100, 100, 100],
        [100,   0,   0],
        [100, 100,   0]
    ])
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1150, 100, [], [], mpopt)
    Qfudge =  zeros(p.shape)
    Qfudge[L, :] = diag(gen.Qg[L] / gen.Pg[L] * bus.lam_Q[Lbus]) * ones(p[L, :].shape)

    t_is( cp[G[0], :], 65, 4, [t, ' : gen 1 price'] )
    t_is( cp[G[1], :], 57.1612, 4, [t, ' : gen 2 price'] )
    cq5 = cq.copy()
    cp5 = cp.copy()
    cp_lam = cp5.copy()
    cp_lam[0, :] = bus.lamP[Gbus[0]]  ## unclipped

    lao_X = p2[G[5], 2] / bus.lam_P[Gbus[5]]
    fro_X = p2[G[0], 2] / bus.lam_P[Gbus[0]]
    lab_X = p2[L[2], 1] / (bus.lam_P[Lbus[2]] + Qfudge[L[2], 0])
    frb_X = p2[L[1], 1] / (bus.lam_P[Lbus[1]] + Qfudge[L[1], 0])

    t_is( lao_X, 1, 4, 'lao_X')
    t_is( fro_X, 1.1425, 4, 'fro_X')
    t_is( lab_X, 1.5813, 4, 'lab_X')
    t_is( frb_X, 0, 4, 'frb_X')

    t = 'gen 1 @ Pmin, marginal offer @ $60, auction_type = 1'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1110, 100, [], [], mpopt)
    cp1 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp5, 6, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal offer @ $60, auction_type = 2'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1120, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp_lam * fro_X, 8, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal offer @ $60, auction_type = 3'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1130, 100, [], [], mpopt)
    cp3 = cp.copy()
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp_lam * lab_X, 8, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal offer @ $60, auction_type = 4'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1140, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G, 0], [654042444660], 4, [t, ' : gen prices'] )
    t_is( cp[L, :], cp_lam[L, :] * frb_X, 8, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal offer @ $60, auction_type = 6'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1160, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp_lam * fro_X, 8, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal offer @ $60, auction_type = 7'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1170, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, cp_lam * (lao_X + lab_X) / 2, 8, [t, ' : prices'] )
    t_is( cp, (cp_lam + cp3) / 2, 7, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal offer @ $60, auction_type = 8'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1180, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp[G, :], cp5[G, :], 7, [t, ' : prices'] )
    t_is( cp[L, :], cp3[L, :], 8, [t, ' : prices'] )

    t = 'gen 1 @ Pmin, marginal offer @ $60, auction_type = 0'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p2, 1100, 100, [], [], mpopt)
    t_is( cq, cq5, 8, [t, ' : quantities'] )
    t_is( cp, p2, 8, [t, ' : prices'] )


    ##-----  gen 2 decommitted, one offer block marginal @ $60  -----
    p[G[1], :] = p[G[1], :] + 100

    t = 'price of decommited gen, auction_type = 5'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1150, 200, [], [], mpopt)
    cp5 = cp.copy()
    Qfudge =  zeros(p.shape)
    Qfudge[L, :] = diag(gen.Qg[L] / gen.Pg[L] * bus.lam_Q[Lbus]) * ones(p[L, :].shape)
    t_is(sum(cq[1, :]), 0, 8, t)
    t_is(cp[1, 0], 59.194, 3, t)

    # Xo = p[0:6, :] / (diag(bus.lam_P[Gbus]) * ones(p[G, :].shape))
    # ao = (cq[0:6, :] != 0)
    # ro = (cq[0:6, :] == 0)
    # Xb = p[6:9, :] / (diag(bus.lam_P[Lbus] + gen.Qg[L] / gen.Pg[L] * bus.lam_Q[Lbus]) * ones(p[L, :].shape))
    # ab = (cq[6:9, :] != 0)
    # rb = (cq[6:9, :] == 0)
    # aXo = ao * Xo
    # rXo = ro * Xo
    # aXb = ab * Xb
    # rXb = rb * Xb

    lao_X = p[G[5], 2] / bus.lam_P[Gbus[5]]
    fro_X = p[G[0], 2] / bus.lam_P[Gbus[0]]
    lab_X = p[L[0], 1] / (bus.lam_P[Lbus[0]] + Qfudge[L[0], 0])
    frb_X = p[L[0], 2] / (bus.lam_P[Lbus[0]] + Qfudge[L[0], 0])

    t_is( lao_X, 1, 4, 'lao_X')
    t_is( fro_X, 1.0212, 4, 'fro_X')
    t_is( lab_X, 1.1649, 4, 'lab_X')
    t_is( frb_X, 0.9985, 4, 'frb_X')

    t = 'price of decommited gen, auction_type = 1'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1110, 200, [], [], mpopt)
    t_is(cp[1, 0], 59.194, 3, t)

    t = 'price of decommited gen, auction_type = 2'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1120, 200, [], [], mpopt)
    t_is(cp[1, 0], cp5[1, 0] * fro_X, 3, t)

    t = 'price of decommited gen, auction_type = 3'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1130, 200, [], [], mpopt)
    t_is(cp[1, 0], cp5[1, 0] * lab_X, 3, t)

    t = 'price of decommited gen, auction_type = 4'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1140, 200, [], [], mpopt)
    t_is(cp[1, 0], cp5[1, 0] * frb_X, 3, t)

    t = 'price of decommited gen, auction_type = 6'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1160, 200, [], [], mpopt)
    t_is(cp[1, 0], cp5[1, 0] * fro_X, 3, t)

    t = 'price of decommited gen, auction_type = 7'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1170, 200, [], [], mpopt)
    t_is(cp[1, 0], cp5[1, 0] * (lao_X + lab_X) / 2, 3, t)

    t = 'price of decommited gen, auction_type = 0'
    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1100, 200, [], [], mpopt)
    t_is(cp[1, 0], 120, 3, t)

    t = 'single block, marginal offer @ $50, auction_type = 5'
    q = array([
        [60],
        [36],
        [36],
        [36],
        [36],
        [36],
        [30],
        [10],
        [20]
    ])

    p = array([
        [50],
        [40],
        [42],
        [44],
        [46],
        [48],
        [100],
        [100],
        [100]
    ])

    MVAbase, cq, cp, bus, gen, gencost, branch, f, dispatch, success, et = \
        runmkt('t_auction_case', q, p, 1150, 100, [], [], mpopt)
    t_is( cq[G[0]], 35.32, 2, t )
    t_is( cq[G[1:6]], q[G[1:6]], 8, [t, ' : gen qtys'] )
    t_is( cp[G[0]], 50, 4, t )
    t_is( cq[L], q[L], 8, [t, ' : load qtys'] )
    t_is( cp[L[1], :], 54.03, 2, t )
    t_is( cp[G], bus.lam_P[Gbus], 8, [t, ' : gen prices'] )
    Qfudge =  zeros(p.shape)
    Qfudge[L, :] = diag(gen.Qg[L] / gen.Pg[L] * bus.lam_Q[Lbus]) * ones(p[L, :].shape)
    t_is( cp[L], bus.lam_P[Lbus] + Qfudge[L, 0], 8, [t, ' : load prices'] )

    t_end()
