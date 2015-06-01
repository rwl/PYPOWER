# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for code in C{off2case}.
"""

from numpy import array, zeros, ix_, r_, c_, flatnonzero as find

from pypower.isload import isload
from pypower.idx_cost import NCOST
from pypower.idx_gen import QMAX, QMIN, GEN_STATUS, PMIN, PMAX, QG

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_skip import t_skip
from pypower.t.t_end import t_end


def t_off2case(quiet=False):
    """Tests for code in C{off2case}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    n_tests = 35

    t_begin(n_tests, quiet)

    ## generator data
    #    bus Pg Qg Qmax Qmin Vg mBase status Pmax Pmin Pc1 Pc2 Qc1min Qc1max Qc2min Qc2max ramp_agc ramp_10 ramp_30 ramp_q apf
    gen0 = array([
        [1,   10,   0,  60, -15, 1, 100, 1, 60, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2,   10,   0,  60, -15, 1, 100, 1, 60, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [7,  -30, -15,   0, -15, 1, 100, 1, 0, -30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [13,  10,   0,  60, -15, 1, 100, 1, 60, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [30, -30, 7.5, 7.5,   0, 1, 100, 1, 0, -30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ], float)
    ## generator cost data
    #    1    startup    shutdown    n    x1    y1    ...    xn    yn
    #    2    startup    shutdown    n    c(n-1)    ...    c0
    gencost0 = array([
        [1, 0,   0, 4,   0, 0,  12, 240,   36, 1200, 60, 2400],
        [1, 100, 0, 4,   0, 0,  12, 240,   36, 1200, 60, 2400],
        [1, 0,   0, 4, -30, 0, -20, 1000, -10, 2000,  0, 3000],
        [1, 0,   0, 4,   0, 0,  12, 240,   36, 1200, 60, 2400],
        [1, 0,  50, 4, -30, 0, -20, 1000, -10, 2000,  0, 3000]
    ], float)

    try:
        from pypower.extras.smartmarket import off2case
    except ImportError:
        t_skip(n_tests, 'smartmarket code not available')
        return

    t = 'isload()'
    t_is(isload(gen0), array([0, 0, 1, 0, 1], bool), 8, t)

    G = find( ~isload(gen0) )
    L = find(  isload(gen0) )
    nGL = len(G) + len(L)

    t = 'P offers only';
    offers = {'P': {}}
    offers['P']['qty'] = array([[25], [26], [27]], float)
    offers['P']['prc'] = array([[10], [50], [100]], float)
    gen, gencost = off2case(gen0, gencost0, offers)

    gen1 = gen0.copy()
    gen1[G, PMAX] = offers['P']['qty'].flatten()
    gen1[L, GEN_STATUS] = 0
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[ix_(G, range(NCOST, NCOST + 9))] = c_[array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700],
    ]), zeros((3, 4))]

    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    offers['P']['qty'] = array([[25], [26], [0], [27],  [0]], float)
    offers['P']['prc'] = array([[10], [50], [0], [100], [0]], float)
    gen, gencost = off2case(gen0, gencost0, offers)
    t_is( gen, gen1, 8, [t, ' (all rows in offer) - gen'] )
    t_is( gencost, gencost1, 8, [t, ' (all rows in offer) - gencost'] )

    t = 'P offers only (GEN_STATUS=0 for 0 qty offer)';
    offers['P']['qty'] = array([ [0], [26],  [27]], float)
    offers['P']['prc'] = array([[10], [50], [100]], float)
    gen, gencost = off2case(gen0, gencost0, offers)

    gen1 = gen0.copy()
    gen1[G[1:3], PMAX] = offers['P']['qty'].flatten()[1:3]
    gen1[G[0], GEN_STATUS] = 0
    gen1[L, GEN_STATUS] = 0
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[ix_(G[1:3], range(NCOST, NCOST + 9))] = c_[array([
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700]
    ]), zeros((2, 4))]

    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers, lim[\'P\'][\'max_offer\']';
    offers['P']['qty'] = array([[25], [26], [27]], float)
    offers['P']['prc'] = array([[10], [50], [100]], float)
    lim = {'P': {'max_offer': 75}}
    gen, gencost = off2case(gen0, gencost0, offers, lim=lim)

    gen1 = gen0.copy()
    gen1[G[:2], PMAX] = offers['P']['qty'].flatten()[:2, :]
    gen1[r_[G[2], L], GEN_STATUS] = 0
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[ix_(G[:2], range(NCOST, NCOST + 9))] = c_[array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300]
    ]), zeros((2, 4))]
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids';
    bids = {'P': {'qty': array([ [20], [28]], float),
                  'prc': array([[100], [10]], float)}}
    gen, gencost = off2case(gen0, gencost0, offers, bids)

    gen1 = gen0.copy()
    gen1[G, PMAX] = offers['P']['qty']
    gen1[ix_(L, [PMIN, QMIN, QMAX])] = array([
        [-20, -10, 0],
        [-28,   0, 7]
    ])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, :8].copy()
    gencost1[ix_(G, range(NCOST, NCOST + 4))] = array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700]
    ])
    gencost1[ix_(L, range(NCOST, NCOST + 4))] = array([
        [2, -20, -2000, 0, 0],
        [2, -28,  -280, 0, 0]
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids (all rows in bid)';
    bids['P']['qty'] = array([[0], [0],  [20], [0], [28]], float)
    bids['P']['prc'] = array([[0], [0], [100], [0], [10]], float)
    gen, gencost = off2case(gen0, gencost0, offers, bids)

    t_is( gen, gen1, 8, [t, ' - gen'] )
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids (GEN_STATUS=0 for 0 qty bid)';
    bids['P']['qty'] = array([  [0], [28]], float)
    bids['P']['prc'] = array([[100], [10]], float)
    gen, gencost = off2case(gen0, gencost0, offers, bids)

    gen1 = gen0.copy()
    gen1[G, PMAX] = offers['P']['qty']
    gen1[L[0], GEN_STATUS] = 0
    gen1[L[1], [PMIN, QMIN, QMAX]] = array([-28, 0, 7])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[ix_(G, range(NCOST, NCOST + 9))] = c_[array([
        [2, 0, 0, 25, 250],
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700]
    ]), zeros((3, 4))]
    gencost1[L[1], NCOST:NCOST + 8] = c_[array([
        [2, -28, -280, 0, 0]
    ]), zeros((1, 4))]
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids (1 gen with both)';
    gen2 = gen0.copy()
    gen2[1, PMIN] = -5
    bids['P']['qty'] = array([[0],  [3],  [20], [0], [28]], float)
    bids['P']['prc'] = array([[0], [50], [100], [0], [10]], float)
    gen, gencost = off2case(gen2, gencost0, offers, bids)

    gen1 = gen2.copy()
    gen1[G, PMAX] = offers['P']['qty']
    gen1[1, PMIN] = -sum( bids['P']['qty'][1, :] )
    gen1[ix_(L, [PMIN, QMIN, QMAX])] = array([
        [-20, -10, 0],
        [-28,   0, 7]
    ])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, :10].copy()
    gencost1[ix_(G, range(NCOST, NCOST + 7))] = array([
        [2,  0,    0, 25,  250,  0,    0],
        [3, -3, -150,  0,    0, 26, 1300],
        [2,  0,    0, 27, 2700,  0,    0]
    ])
    gencost1[ix_(L, range(NCOST, NCOST + 7))] = c_[array([
        [2, -20, -2000, 0, 0],
        [2, -28,  -280, 0, 0]
    ]), zeros((2, 2))]
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids, lim[\'P\'][\'max_offer\']/[\'min_bid\']'
    bids['P']['qty'] = array([[20],  [28]], float)
    bids['P']['prc'] = array([[100], [10]], float)
    lim['P']['min_bid'] = 50.0
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1 = gen0.copy()
    gen1[G[:2], PMAX] = offers['P']['qty'][:2, :]
    gen1[r_[G[2], L[1]], GEN_STATUS] = 0
    gen1[L[0], [PMIN, QMIN, QMAX]] = array([-20, -10, 0])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[ix_(G[:2], range(NCOST, NCOST + 9))] = c_[array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300]
    ]), zeros((2, 4))]
    gencost1[L[0], NCOST:NCOST + 9] = array([2, -20, -2000, 0, 0, 0, 0, 0, 0])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids, lim[\'P\'][\'max_offer\']/[\'min_bid\'], multi-block'
    offers['P']['qty'] = array([[10,  40], [20, 30], [25, 25]], float)
    offers['P']['prc'] = array([[10, 100], [25, 65], [50, 90]], float)
    bids['P']['qty'] = array([[ 20, 10], [12, 18]], float)
    bids['P']['prc'] = array([[100, 60], [70, 10]], float)
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1 = gen0.copy()
    gen1[G, PMAX] = array([10, 50, 25])
    gen1[ix_(L, [PMIN, QMIN, QMAX])] = array([
        [-30, -15, 0],
        [-12,   0, 3]
    ])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, :10].copy()
    gencost1[ix_(G, range(NCOST, NCOST + 7))] = array([
        [2, 0, 0, 10,  100, 0,     0],
        [3, 0, 0, 20,  500, 50, 2450],
        [2, 0, 0, 25, 1250, 0,     0]
    ])
    gencost1[ix_(L, range(NCOST, NCOST + 7))] = array([
        [3, -30, -2600, -20, -2000, 0, 0],
        [2, -12,  -840,   0,     0, 0, 0]
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    ##-----  reactive  -----
    ## generator cost data
    #    1    startup    shutdown    n    x1    y1    ...    xn    yn
    #    2    startup    shutdown    n    c(n-1)    ...    c0
    gencost0 = array([
        [1,   0,  0, 4,   0,    0,  12,  240,  36, 1200, 60, 2400],
        [1, 100,  0, 4,   0,    0,  12,  240,  36, 1200, 60, 2400],
        [1,   0,  0, 4, -30,    0, -20, 1000, -10, 2000,  0, 3000],
        [1,   0,  0, 4,   0,    0,  12,  240,  36, 1200, 60, 2400],
        [1,   0, 50, 4, -30,    0, -20, 1000, -10, 2000,  0, 3000],
        [1,   0,  0, 4, -15, -150,   0,    0,  30,  150, 60,  450],
        [1, 100,  0, 2,   0,    0,   0,    0,   0,    0,  0,    0],
        [1,   0,  0, 3, -20,  -15, -10,  -10,   0,    0,  0,    0],
        [1,   0,  0, 3,   0,    0,  40,   80,  60,  180,  0,    0],
        [1,   0, 50, 2,   0,    0,   0,    0,   0,    0,  0,    0]
    ], float)

    t = 'PQ offers only';
    offers['P']['qty'] = array([[25], [26],  [27]], float)
    offers['P']['prc'] = array([[10], [50], [100]], float)
    offers['Q']['qty'] = array([[10], [20],  [30]], float)
    offers['Q']['prc'] = array([[10],  [5],   [1]], float)
    gen, gencost = off2case(gen0, gencost0, offers)

    gen1 = gen0.copy()
    gen1[G, PMAX] = offers['P']['qty']
    gen1[G, QMAX] = offers['Q']['qty']
    gen1[G, QMIN] = 0
    gen1[L, GEN_STATUS] = 0
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[ix_(G, range(NCOST, NCOST + 9))] = c_[array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700]
    ]), zeros((3, 4))]
    gencost1[ix_(G + nGL - 1, range(NCOST, NCOST + 9))] = c_[array([
        [2, 0, 0, 10, 100],
        [2, 0, 0, 20, 100],
        [2, 0, 0, 30,  30]
    ]), zeros((3, 4))]

    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'PQ offers & PQ bids, lim.P/Q.max_offer/min_bid, multi-block';
    offers['P']['qty'] = array([[10,  40], [20, 30], [25, 25]], float)
    offers['P']['prc'] = array([[10, 100], [25, 65], [50, 90]], float)
    bids['P']['qty'] = array([[ 20, 10], [12, 18]], float)
    bids['P']['prc'] = array([[100, 60], [70, 10]], float)
    offers['Q']['qty'] = array([[ 5,  5], [10, 10], [15, 15]], float)
    offers['Q']['prc'] = array([[10, 20], [ 5, 60], [ 1, 10]], float)
    bids['Q']['qty'] = array([ 15, 10, 15,  15,  0], float)
    bids['Q']['prc'] = array([-10,  0,  5, -20, 10], float)
    lim['Q']['max_offer'] = 50.0
    lim['Q']['min_bid'] = -15.0
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1 = gen0.copy()
    gen1[:, [GEN_STATUS, PMIN, PMAX, QMIN, QMAX]] = array([
        [1,  10, 10, -15,  10],
        [1,  12, 50, -10,  10],
        [1, -10,  0,  -5,   0],
        [1,  12, 25,   0,  30],
        [0, -30,  0,   0, 7.5]
    ])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, :12].copy()
    gencost1[:, NCOST - 1:NCOST + 9] = array([
        [2,   0,     0,  10,   100,   0,    0,  0,    0],
        [3,   0,     0,  20,   500,  50, 2450,  0,    0],
        [3, -30, -2600, -20, -2000,   0,    0,  0,    0],
        [2,   0,     0,  25,  1250,   0,    0,  0,    0],
        [4, -30,     0, -20,  1000, -10, 2000,  0, 3000],
        [4, -15,   150,   0,     0,   5,   50, 10,  150],
        [3, -10,     0,   0,     0,  10,   50,  0,    0],
        [2, -15,   -75,   0,     0,   0,    0,  0,    0],
        [3,   0,     0,  15,    15,  30,  165,  0,    0],
        [2,   0,     0,   0,     0,   0,    0,  0,    0]
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'PQ offers & PQ bids, for gen, no P, no shutdown';
    gen2 = gen0.copy()
    gen2[0, PMIN] = 0
    offers['P']['qty'] = array([[0, 40], [20, 30], [25, 25]], float)
    gen, gencost = off2case(gen2, gencost0, offers, bids, lim)

    gen1[0, [PMIN, PMAX, QMIN, QMAX]] = array([0, 0, -15, 10])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1[0, NCOST:NCOST + 9] = gencost0[0, NCOST:NCOST + 9]
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'PQ offers & PQ bids, for gen, no Q, no shutdown';
    offers['P']['qty'] = array([[10, 40], [20, 30], [25, 25]], float)
    offers['Q']['qty'] = array([[ 5,  5], [ 0, 10], [15, 15]], float)
    bids['Q']['qty'] = array([15, 0, 15, 15, 0], float)
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1[0, [PMIN, PMAX, QMIN, QMAX]] = array([10, 10, -15, 10])    ## restore original
    gen1[1, [PMIN, PMAX, QMIN, QMAX]] = array([12, 50,   0,  0])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1[ix_([0, 1, 6], range(NCOST, NCOST + 9))] = array([
        [2, 0, 0, 10, 100,  0,    0, 0, 0],
        [3, 0, 0, 20, 500, 50, 2450, 0, 0],
        [2, 0, 0,  0,   0,  0,    0, 0, 0]
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'PQ offers & PQ bids, lim.P/Q.max_offer/min_bid, multi-block';
    offers['P']['qty'] = array([[10,  40], [20, 30], [25, 25]], float)
    offers['P']['prc'] = array([[10, 100], [25, 65], [50, 90]], float)
    bids['P']['qty'] = array([[10,   0], [12, 18]], float)
    bids['P']['prc'] = array([[100, 60], [70, 10]], float)
    offers['Q']['qty'] = array([[5, 5], [10, 10], [15, 15]], float)
    offers['Q']['prc'] = array([[10, 20], [5, 60], [1, 10]], float)
    bids['Q']['qty'] = array([15, 10, 10, 15, 0], float)
    bids['Q']['prc'] = array([-10, 0, 5, -20, 10], float)
    lim['Q']['max_offer'] = 50.0
    lim['Q']['min_bid'] = -15.0
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1 = gen0.copy()
    gen1[:, [GEN_STATUS, PMIN, PMAX, QMIN, QMAX]] = array([
        [1,  10, 10, -15, 10],
        [1,  12, 50, -10, 10],
        [1, -10,  0,  -5,  0],
        [1,  12, 25,   0, 30],
        [0, -30,  0,   0,  7.5]
    ])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, :12].copy()
    gencost1[:, NCOST:NCOST + 9] = array([
        [2,   0,     0,  10,  100,   0,    0,  0,    0],
        [3,   0,     0,  20,  500,  50, 2450,  0,    0],
        [2, -10, -1000,   0,    0,   0,    0,  0,    0],
        [2,   0,     0,  25, 1250,   0,    0,  0,    0],
        [4, -30,     0, -20, 1000, -10, 2000,  0, 3000],
        [4, -15,   150,   0,    0,   5,   50, 10,  150],
        [3, -10,     0,   0,    0,  10,   50,  0,    0],
        [2, -10,   -50,   0,    0,   0,    0,  0,    0],
        [3,   0,     0,  15,   15,  30,  165,  0,    0],
        [2,   0,     0,   0,    0,   0,    0,  0,    0]
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'PQ offers & PQ bids, zero Q load w/P bid, shutdown bugfix';
    gen1 = gen0.copy()
    gen1[4, [QG, QMIN, QMAX]] = 0
    gen, gencost = off2case(gen1, gencost0, offers, bids, lim)

    gen1[:, [PMIN, PMAX, QMIN, QMAX]] = array([
        [ 10, 10, -15, 10],
        [ 12, 50, -10, 10],
        [-10,  0,  -5,  0],
        [ 12, 25,   0, 30],
        [-12,  0,   0,  0]
    ])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, :12].copy()
    gencost1[:, NCOST - 1:NCOST + 9] = array([
        [2,   0,     0, 10,  100,  0,    0,  0,   0],
        [3,   0,     0, 20,  500, 50, 2450,  0,   0],
        [2, -10, -1000,  0,    0,  0,    0,  0,   0],
        [2,   0,     0, 25, 1250,  0,    0,  0,   0],
        [2, -12,  -840,  0,    0,  0,    0,  0,   0],
        [4, -15,   150,  0,    0,  5,   50, 10, 150],
        [3, -10,     0,  0,    0, 10,   50,  0,   0],
        [2, -10,   -50,  0,    0,  0,    0,  0,   0],
        [3,   0,     0, 15,   15, 30,  165,  0,   0],
        [2,   0,     0,  0,    0,  0,    0,  0,   0]
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'PQ offers & PQ bids, non-zero Q load w/no P bid, shutdown bugfix';
    offers['P']['qty'] = array([[10,  40], [20, 30], [25, 25]], float)
    offers['P']['prc'] = array([[10, 100], [25, 65], [50, 90]], float)
    bids['P']['qty'] = array([[0, 10], [12, 18]], float)
    bids['P']['prc'] = array([[100, 40], [70, 10]], float)
    offers['Q']['qty'] = array([[ 5,  5], [10, 10], [15, 15]], float)
    offers['Q']['prc'] = array([[10, 20], [ 5, 60], [ 1, 10]], float)
    bids['Q']['qty'] = array([ 15, 10, 15,  15,  0], float)
    bids['Q']['prc'] = array([-10,  0,  5, -20, 10], float)
    lim['Q']['max_offer'] = 50.0
    lim['Q']['min_bid'] = -15.0
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1 = gen0.copy()
    gen1[:, [GEN_STATUS, PMIN, PMAX, QMIN, QMAX]] = array([
        [1,  10, 10, -15, 10],
        [1,  12, 50, -10, 10],
        [0, -30,  0, -15,  0],
        [1,  12, 25,   0, 30],
        [0, -30,  0,   0, 7.5]
    ])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, :12].copy()
    gencost1[:, NCOST - 1:NCOST + 9] = array([
        [2,   0,   0,  10,  100,   0,    0,  0,    0],
        [3,   0,   0,  20,  500,  50, 2450,  0,    0],
        [4, -30,   0, -20, 1000, -10, 2000,  0, 3000],
        [2,   0,   0,  25, 1250,   0,    0,  0,    0],
        [4, -30,   0, -20, 1000, -10, 2000,  0, 3000],
        [4, -15, 150,   0,    0,   5,   50, 10,  150],
        [3, -10,   0,   0,    0,  10,   50,  0,    0],
        [3, -20, -15, -10,  -10,   0,    0,  0,    0],
        [3,   0,   0,  15,   15,  30,  165,  0,    0],
        [2,   0,   0,   0,    0,   0,    0,  0,    0]
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t_end()


if __name__ == '__main__':
    t_off2case(quiet=False)
