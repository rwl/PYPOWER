# Copyright (C) 2005-2011 Power System Engineering Research Center
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

from numpy import array, zeros, r_, flatnonzero as find

from pypower.isload import isload
from pypower.idx_cost import NCOST
from pypower.idx_gen import QMAX, QMIN, GEN_STATUS, PMIN, PMAX, QG

from pypower.t.t_begin import t_begin
from pypower.t.t_skip import t_skip
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end


def t_off2case(quiet=False):
    """Tests for code in C{off2case}.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    n_tests = 35

    t_begin(n_tests, quiet)

    ## generator data
    #    bus    Pg    Qg    Qmax    Qmin    Vg    mBase    status    Pmax    Pmin    Pc1    Pc2    Qc1min    Qc1max    Qc2min    Qc2max    ramp_agc    ramp_10    ramp_30    ramp_q    apf
    gen0 = array([
        [1,   10,   0,  60, -15, 1, 100, 1, 60, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2,   10,   0,  60, -15, 1, 100, 1, 60, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [7,  -30, -15,   0, -15, 1, 100, 1, 0, -30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [13,  10,   0,  60, -15, 1, 100, 1, 60, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [30, -30, 7.5, 7.5,   0, 1, 100, 1, 0, -30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])
    ## generator cost data
    #    1    startup    shutdown    n    x1    y1    ...    xn    yn
    #    2    startup    shutdown    n    c(n-1)    ...    c0
    gencost0 = array([
        [1, 0,   0, 4,   0, 0,  12, 240,   36, 1200, 60, 2400],
        [1, 100, 0, 4,   0, 0,  12, 240,   36, 1200, 60, 2400],
        [1, 0,   0, 4, -30, 0, -20, 1000, -10, 2000,  0, 3000],
        [1, 0,   0, 4,   0, 0,  12, 240,   36, 1200, 60, 2400],
        [1, 0,  50, 4, -30, 0, -20, 1000, -10, 2000,  0, 3000]
    ])

    try:
        from pypower.extras.smartmarket import off2case
    except ImportError:
        t_skip(n_tests, 'smartmarket code not available')
        return

    t = 'isload()';
    t_is(isload(gen0), array([0, 0, 1, 0, 1]), 8, t)

    G = find( isload(gen0) == 0 )
    L = find( isload(gen0) )
    nGL = len(G) + len(L)

    t = 'P offers only';
    offers = {'P': {}}
    offers['P']['qty'] = array([25, 26, 27])
    offers['P']['prc'] = array([10, 50, 100])
    gen, gencost = off2case(gen0, gencost0, offers)

    gen1 = gen0.copy()
    gen1.Pmax[G] = offers['P']['qty']
    gen1.status[L] = 0;
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[G, range(gencost1.ncost - 1, gencost1.ncost + 8)] = array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700],
        zeros((3, 4))
    ])

    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    offers['P']['qty'] = array([25, 26, 0,  27, 0])
    offers['P']['prc'] = array([10, 50, 0, 100, 0])
    gen, gencost = off2case(gen0, gencost0, offers)
    t_is( gen, gen1, 8, [t, ' (all rows in offer) - gen'] )
    t_is( gencost, gencost1, 8, [t, ' (all rows in offer) - gencost'] )

    t = 'P offers only (GEN_STATUS=0 for 0 qty offer)';
    offers['P']['qty'] = array([ 0, 26,  27])
    offers['P']['prc'] = array([10, 50, 100])
    gen, gencost = off2case(gen0, gencost0, offers)

    gen1 = gen0.copy()
    gen1.Pmax[G[1:3]] = offers['P']['qty'][1:3]
    gen1.status[G[0]] = 0
    gen1.status[L] = 0
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[G[1:3], NCOST - 1:NCOST + 8] = array([
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700],
        zeros((2, 4))
    ])

    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers, lim[\'P\'][\'max_offer\']';
    offers['P']['qty'] = array([25, 26, 27])
    offers['P']['prc'] = array([10, 50, 100])
    lim = {'P': {}}
    lim['P']['max_offer'] = 75;
    gen, gencost = off2case(gen0, gencost0, offers, [], lim)

    gen1 = gen0.copy()
    gen1.Pmax[G[0:2]] = offers['P']['qty'][0:2, :]
    gen1.status[r_[G[2], L]] = 0;
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[G[0:2], NCOST - 1:NCOST + 8] = array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300],
        zeros(2,4)
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids';
    bids = {'P': {}}
    bids['P']['qty'] = array([20, 28])
    bids['P']['prc'] = array([100, 10])
    gen, gencost = off2case(gen0, gencost0, offers, bids)

    gen1 = gen0.copy()
    gen1.Pmax[G] = offers['P']['qty']
    gen1.Pmin[L] = array([-20, -28])
    gen1.Qmin[L] = array([-10, 0])
    gen1.Qmax[L] = array([0, 7])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, 0:8]
    gencost1[G, NCOST - 1:NCOST + 4] = array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700]
    ])
    gencost1[L, NCOST - 1:NCOST + 4] = array([
        [2, -20, -2000, 0, 0],
        [2, -28,  -280, 0, 0]
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids (all rows in bid)';
    bids['P']['qty'] = array([0, 0,  20, 0, 28])
    bids['P']['prc'] = array([0, 0, 100, 0, 10])
    gen, gencost = off2case(gen0, gencost0, offers, bids)

    t_is( gen, gen1, 8, [t, ' - gen'] )
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids (GEN_STATUS=0 for 0 qty bid)';
    bids['P']['qty'] = array([  0, 28])
    bids['P']['prc'] = array([100, 10])
    gen, gencost = off2case(gen0, gencost0, offers, bids)

    gen1 = gen0.copy()
    gen1.Pmax[G] = offers['P']['qty']
    gen1.status[L[0]] = 0
    gen1.Pmin[L[1]] = -28
    gen1.Pmin[L[1]] = 0
    gen1.Pmin[L[1]] = 7
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[G, NCOST - 1:NCOST + 8] = array([
        [2, 0, 0, 25, 250],
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700],
        zeros((3, 4))
    ])
    gencost1[L[1], NCOST - 1:NCOST + 8] = array([
        [2, -28, -280, 0, 0],
        zeros((1, 4))
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids (1 gen with both)';
    gen2 = gen0.copy()
    gen2.Pmin[1] = -5
    bids['P']['qty'] = array([0,  3,  20, 0, 28])
    bids['P']['prc'] = array([0, 50, 100, 0, 10])
    gen, gencost = off2case(gen2, gencost0, offers, bids)

    gen1 = gen2.copy()
    gen1.Pmax[G] = offers['P']['qty']
    gen1.Pmin[1] = -sum(bids['P']['qty'][1, :])
    gen1.Pmin[L] = array([-20, -28])
    gen1.Qmin[L] = array([-10, 0])
    gen1.Qmax[L] = array([0, 7])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, 0:10]
    gencost1[G, NCOST - 1:NCOST + 6] = array([
        [2,  0,    0, 25,  250,  0,    0],
        [3, -3, -150,  0,    0, 26, 1300],
        [2,  0,    0, 27, 2700,  0,    0]
    ])
    gencost1[L, NCOST - 1:NCOST + 6] = array([
        [2, -20, -2000, 0, 0],
        [2, -28,  -280, 0, 0],
        zeros((2, 2))
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids, lim[\'P\'][\'max_offer\']/[\'min_bid\']'
    bids['P']['qty'] = array([20,  28])
    bids['P']['prc'] = array([100, 10])
    lim['P']['min_bid'] = 50
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1 = gen0.copy()
    gen1.Pmax[G[0:2]] = offers['P']['qty'][0:2, :]
    gen1.status[r_[G[2], L[1]]] = 0
    gen1.Pmin[L[0]] = -20
    gen1.Pmin[L[0]] = -10
    gen1.Pmin[L[0]] = 0
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[G[0:2], NCOST - 1:NCOST + 8] = array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300],
        zeros((2, 4))
    ])
    gencost1[L[0], NCOST - 1:NCOST + 8] = array([2, -20, -2000, 0, 0, 0, 0, 0, 0])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'P offers & P bids, lim[\'P\'][\'max_offer\']/[\'min_bid\'], multi-block'
    offers['P']['qty'] = array([[10,  40], [20, 30], [25, 25]])
    offers['P']['prc'] = array([[10, 100], [25, 65], [50, 90]])
    bids['P']['qty'] = array([[ 20, 10], [12, 18]])
    bids['P']['prc'] = array([[100, 60], [70, 10]])
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1 = gen0.copy()
    gen1.Pmax[G] = array([10, 50, 25])
    gen1.Pmin[L] = array([-30, 12])
    gen1.Qmin[L] = array([-15, 0])
    gen1.Qmax[L] = array([0, 3])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, 0:10]
    gencost1[G, NCOST - 1:NCOST + 6] = array([
        [2, 0, 0, 10,  100, 0,     0],
        [3, 0, 0, 20,  500, 50, 2450],
        [2, 0, 0, 25, 1250, 0,     0]
    ])
    gencost1[L, NCOST - 1:NCOST + 6] = array([
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
    ])

    t = 'PQ offers only';
    offers['P']['qty'] = array([25, 26, 27])
    offers['P']['prc'] = array([10, 50, 100])
    offers['Q']['qty'] = array([10, 20, 30])
    offers['Q']['prc'] = array([10, 5, 1])
    gen, gencost = off2case(gen0, gencost0, offers)

    gen1 = gen0.copy()
    gen1.Pmax[G] = offers['P']['qty']
    gen1.Qmax[G] = offers['Q']['qty']
    gen1.Qmin[G] = 0
    gen1.status[L] = 0
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0.copy()
    gencost1[G, NCOST - 1:NCOST + 8] = array([
        [2, 0, 0, 25,  250],
        [2, 0, 0, 26, 1300],
        [2, 0, 0, 27, 2700],
        zeros((3, 4))
    ])
    gencost1[G + nGL - 1, NCOST - 1:NCOST + 8] = array([
        [2, 0, 0, 10, 100],
        [2, 0, 0, 20, 100],
        [2, 0, 0, 30,  30],
        zeros((3, 4))
    ])

    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'PQ offers & PQ bids, lim.P/Q.max_offer/min_bid, multi-block';
    offers['P']['qty'] = array([[10,  40], [20, 30], [25, 25]])
    offers['P']['prc'] = array([[10, 100], [25, 65], [50, 90]])
    bids['P']['qty'] = array([[ 20, 10], [12, 18]])
    bids['P']['prc'] = array([[100, 60], [70, 10]])
    offers['Q']['qty'] = array([[ 5,  5], [10, 10], [15, 15]])
    offers['Q']['prc'] = array([[10, 20], [ 5, 60], [ 1, 10]])
    bids['Q']['qty'] = array([ 15, 10, 15,  15,  0])
    bids['Q']['prc'] = array([-10,  0,  5, -20, 10])
    lim['Q']['max_offer'] = 50
    lim['Q']['min_bid'] = -15
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1 = gen0.copy()
    gen.status[:] = array([1, 1, 1, 1, 0])
    gen.Pmin[:] = array([10, 12, -30, 12, -30])
    gen.Pmax[:] = array([10, 50, 0, 25, 0])
    gen.Qmin[:] = array([-15, -10, -15, 0, 0])
    gen.Qmax[:] = array([10, 10, 0, 30, 7.5])
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1 = gencost0[:, 0:12]
    gencost1[:, NCOST - 1:NCOST + 8] = array([
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
    gen2.Pmin[0] = 0
    offers['P']['qty'] = array([[0, 40], [20, 30], [25, 25]])
    gen, gencost = off2case(gen2, gencost0, offers, bids, lim)

    gen1.Pmin[0] = 0
    gen1.Pmax[0] = 0
    gen1.Qmin[0] = -15
    gen1.Qmax[0] = 10
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1[0, NCOST - 1:NCOST + 8] = gencost0[0, NCOST - 1:NCOST + 8]
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'PQ offers & PQ bids, for gen, no Q, no shutdown';
    offers['P']['qty'] = array([[10, 40], [20, 30], [25, 25]])
    offers['Q']['qty'] = array([[ 5,  5], [ 0, 10], [15, 15]])
    bids['Q']['qty'] = array([15, 0, 15, 15, 0])
    gen, gencost = off2case(gen0, gencost0, offers, bids, lim)

    gen1.Pmin[0, 1] = [10, 12]  ## restore original
    gen1.Pmax[0, 1] = [10, 50]
    gen1.Qmin[0, 1] = [-15, 0]
    gen1.Qmax[0, 1] = [10,  0]
    t_is( gen, gen1, 8, [t, ' - gen'] )

    gencost1[[0, 1, 6], NCOST - 1:NCOST + 8] = array([
        [2, 0, 0, 10, 100,  0,    0, 0, 0],
        [3, 0, 0, 20, 500, 50, 2450, 0, 0],
        [2, 0, 0,  0,   0,  0,    0, 0, 0]
    ])
    t_is( gencost, gencost1, 8, [t, ' - gencost'] )

    t = 'PQ offers & PQ bids, lim.P/Q.max_offer/min_bid, multi-block';
    offers['P']['qty'] = array([[10,  40], [20, 30], [25, 25]])
    offers['P']['prc'] = array([[10, 100], [25, 65], [50, 90]])
    bids['P']['qty'] = array([[10,   0], [12, 18]])
    bids['P']['prc'] = array([[100, 60], [70, 10]])
    offers['Q']['qty'] = array([[5, 5], [10, 10], [15, 15]])
    offers['Q']['prc'] = array([[10, 20], [5, 60], [1, 10]])
    bids['Q']['qty'] = array([15, 10, 10, 15, 0])
    bids['Q']['prc'] = array([-10, 0, 5, -20, 10])
    lim['Q']['max_offer'] = 50
    lim['Q']['min_bid'] = -15
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

    gencost1 = gencost0[:, 0:12]
    gencost1[:, NCOST:NCOST + 8] = array([
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

    gencost1 = gencost0[:, 0:12]
    gencost1[:, NCOST - 1:NCOST + 8] = array([
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
    offers['P']['qty'] = array([[10,  40], [20, 30], [25, 25]])
    offers['P']['prc'] = array([[10, 100], [25, 65], [50, 90]])
    bids['P']['qty'] = array([[0, 10], [12, 18]])
    bids['P']['prc'] = array([[100, 40], [70, 10]])
    offers['Q']['qty'] = array([[ 5,  5], [10, 10], [15, 15]])
    offers['Q']['prc'] = array([[10, 20], [ 5, 60], [ 1, 10]])
    bids['Q']['qty'] = array([ 15, 10, 15,  15,  0])
    bids['Q']['prc'] = array([-10,  0,  5, -20, 10])
    lim['Q']['max_offer'] = 50
    lim['Q']['min_bid'] = -15
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

    gencost1 = gencost0[:, 0:12]
    gencost1[:, NCOST - 1:NCOST + 8] = array([
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
