# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for code in C{scale_load}.
"""

from os.path import dirname, join

from numpy import array, zeros, in1d, vstack, flatnonzero as find

from pypower.loadcase import loadcase
from pypower.isload import isload
from pypower.scale_load import scale_load, ScalingError

from pypower.idx_bus import PD, QD, BUS_AREA
from pypower.idx_gen import GEN_BUS, QG, PMIN, QMIN, QMAX

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end


def t_scale_load(quiet=False):
    """Tests for code in C{scale_load}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    n_tests = 275

    t_begin(n_tests, quiet)

    ppc = loadcase(join(dirname(__file__), 't_auction_case'))
    ppc['gen'][7, GEN_BUS] = 2    ## multiple d. loads per area, same bus as gen
    ppc['gen'][7, [QG, QMIN, QMAX]] = array([3, 0, 3])
    ## put it load before gen in matrix

    ppc['gen'] = vstack([ppc['gen'][7, :], ppc['gen'][:7, :], ppc['gen'][8, :]])
    ld = find(isload(ppc['gen']))
    a = [None] * 3
    lda = [None] * 3
    for k in range(3):
        a[k] = find(ppc['bus'][:, BUS_AREA] == k + 1)  ## buses in area k
        tmp = find( in1d(ppc['gen'][ld, GEN_BUS] - 1, a[k]) )
        lda[k] = ld[tmp]                       ## disp loads in area k

    area = [None] * 3
    for k in range(3):
        area[k] = {'fixed': {}, 'disp': {}, 'both': {}}
        area[k]['fixed']['p'] = sum(ppc['bus'][a[k], PD])
        area[k]['fixed']['q'] = sum(ppc['bus'][a[k], QD])
        area[k]['disp']['p'] = -sum(ppc['gen'][lda[k], PMIN])
        area[k]['disp']['qmin'] = -sum(ppc['gen'][lda[k], QMIN])
        area[k]['disp']['qmax'] = -sum(ppc['gen'][lda[k], QMAX])
        area[k]['disp']['q'] = area[k]['disp']['qmin'] + area[k]['disp']['qmax']
        area[k]['both']['p'] = area[k]['fixed']['p'] + area[k]['disp']['p']
        area[k]['both']['q'] = area[k]['fixed']['q'] + area[k]['disp']['q']

    total = {'fixed': {}, 'disp': {}, 'both': {}}
    total['fixed']['p'] = sum(ppc['bus'][:, PD])
    total['fixed']['q'] = sum(ppc['bus'][:, QD])
    total['disp']['p'] = -sum(ppc['gen'][ld, PMIN])
    total['disp']['qmin'] = -sum(ppc['gen'][ld, QMIN])
    total['disp']['qmax'] = -sum(ppc['gen'][ld, QMAX])
    total['disp']['q'] = total['disp']['qmin'] + total['disp']['qmax']
    total['both']['p'] = total['fixed']['p'] + total['disp']['p']
    total['both']['q'] = total['fixed']['q'] + total['disp']['q']

    ##-----  single load zone, one scale factor  -----
    load = array([2])
    t = 'all fixed loads (PQ) * 2 : '
    bus, _ = scale_load(load, ppc['bus'])
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load * total['fixed']['q'], 8, [t, 'total fixed Q'])
    opt = {'which': 'FIXED'}

    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)

    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load * total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all fixed loads (P) * 2 : '
    opt = {'pq': 'P'}
    bus, _ = scale_load(load, ppc['bus'], None, None, opt)
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    opt = {'pq': 'P', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all loads (PQ) * 2 : '
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'])
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load * total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load * total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), load * total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), load * total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all loads (P) * 2 : '
    opt = {'pq': 'P'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load * total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all disp loads (PQ) * 2 : '
    opt = {'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load * total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), load * total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), load * total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all disp loads (P) * 2 : '
    opt = {'pq': 'P', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load * total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    ##-----  single load zone, one scale quantity  -----
    load = array([200.0])
    t = 'all fixed loads (PQ) => total = 200 : '
    opt = {'scale': 'QUANTITY'}
    bus, _ = scale_load(load, ppc['bus'], None, None, opt)
    t_is(sum(bus[:, PD]), load, 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load / total['fixed']['p'] * total['fixed']['q'], 8, [t, 'total fixed Q'])
    opt = {'scale': 'QUANTITY', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), load - total['disp']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), (load - total['disp']['p'])/total['fixed']['p']*total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all fixed loads (P) => total = 200 : '
    opt = {'scale': 'QUANTITY', 'pq': 'P'}
    bus, _ = scale_load(load, ppc['bus'], None, None, opt)
    t_is(sum(bus[:, PD]), load, 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    opt = {'scale': 'QUANTITY', 'pq': 'P', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), load - total['disp']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all loads (PQ) => total = 200 : '
    opt = {'scale': 'QUANTITY'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), load / total['both']['p']*total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load / total['both']['p']*total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load / total['both']['p']*total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), load / total['both']['p']*total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), load / total['both']['p']*total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all loads (P) => total = 200 : '
    opt = {'scale': 'QUANTITY', 'pq': 'P'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), load / total['both']['p']*total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load / total['both']['p']*total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all disp loads (PQ) => total = 200 : '
    opt = {'scale': 'QUANTITY', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load - total['fixed']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), (load - total['fixed']['p'])/total['disp']['p']*total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), (load - total['fixed']['p'])/total['disp']['p']*total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all disp loads (P) => total = 200 : '
    opt = {'scale': 'QUANTITY', 'pq': 'P', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    t_is(sum(bus[:, PD]), total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load - total['fixed']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    ##-----  3 zones, area scale factors  -----
    t = 'area fixed loads (PQ) * [3 2 1] : '
    load = array([3, 2, 1])
    bus, _ = scale_load(load, ppc['bus'])
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), load[k] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))

    opt = {'which': 'FIXED'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), load[k] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area fixed loads (P) * [3 2 1] : '
    load = array([3, 2, 1])
    opt = {'pq': 'P'}
    bus, _ = scale_load(load, ppc['bus'], None, None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))

    opt = {'pq': 'P', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'all area loads (PQ) * [3 2 1] : '
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'])
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), load[k] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), load[k] * area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), load[k] * area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))


    t = 'all area loads (P) * [3 2 1] : '
    opt = {'pq': 'P'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area disp loads (PQ) * [3 2 1] : '
    opt = {'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), load[k] * area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), load[k] * area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area disp loads (P) * [3 2 1] : '
    opt = {'pq': 'P', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    ##-----  3 zones, area scale quantities  -----
    t = 'area fixed loads (PQ) => total = [100 80 60] : '
    load = array([100, 80, 60], float)
    opt = {'scale': 'QUANTITY'}
    bus, _ = scale_load(load, ppc['bus'], None, None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), load[k] / area[k]['fixed']['p'] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))

    opt = {'scale': 'QUANTITY', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] - area[k]['disp']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), (load[k] - area[k]['disp']['p']) / area[k]['fixed']['p'] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area fixed loads (P) => total = [100 80 60] : '
    load = array([100, 80, 60], float)
    opt = {'scale': 'QUANTITY', 'pq': 'P'}
    bus, _ = scale_load(load, ppc['bus'], None, None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))

    opt = {'scale': 'QUANTITY', 'pq': 'P', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k]-area[k]['disp']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'all area loads (PQ) => total = [100 80 60] : '
    opt = {'scale': 'QUANTITY'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] / area[k]['both']['p'] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), load[k] / area[k]['both']['p'] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] / area[k]['both']['p'] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), load[k] / area[k]['both']['p'] * area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), load[k] / area[k]['both']['p'] * area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'all area loads (P) => total = [100 80 60] : '
    opt = {'scale': 'QUANTITY', 'pq': 'P'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] / area[k]['both']['p'] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] / area[k]['both']['p'] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area disp loads (PQ) => total = [100 80 60] : throws expected exception'
    load = array([100, 80, 60], float)
    opt = {'scale': 'QUANTITY', 'which': 'DISPATCHABLE'}
    err = 0
    try:
        bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    except ScalingError as e:
        expected = 'scale_load: impossible to make zone 2 load equal 80 by scaling non-existent dispatchable load'
        err = expected not in str(e)
    t_ok(err, t)

    t = 'area disp loads (PQ) => total = [100 74.3941 60] : '
    load = array([100, area[1]['fixed']['p'], 60], float)
    opt = {'scale': 'QUANTITY', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k]-area[k]['fixed']['p'], 8, '%s area %d disp P' % (t, k))
        if k == 1:
            t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
            t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))
        else:
            t_is(-sum(gen[lda[k], QMIN]), (load[k] - area[k]['fixed']['p']) / area[k]['disp']['p'] * area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
            t_is(-sum(gen[lda[k], QMAX]), (load[k] - area[k]['fixed']['p']) / area[k]['disp']['p'] * area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area disp loads (P) => total = [100 74.3941 60] : '
    opt = {'scale': 'QUANTITY', 'pq': 'P', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], None, opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k]-area[k]['fixed']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    ##-----  explict single load zone  -----
    t = 'explicit single load zone'
    load_zone = zeros(ppc['bus'].shape[0])
    load_zone[[2, 3]] = 1
    load = array([2.0])
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], load_zone)
    Pd = ppc['bus'][:, PD]
    Pd[[2, 3]] = load * Pd[[2, 3]]
    t_is( bus[:, PD], Pd, 8, t)

    ##-----  explict multiple load zone  -----
    t = 'explicit multiple load zone'
    load_zone = zeros(ppc['bus'].shape[0])
    load_zone[[2, 3]] = 1
    load_zone[[6, 7]] = 2
    load = array([2, 0.5])
    bus, gen = scale_load(load, ppc['bus'], ppc['gen'], load_zone)
    Pd = ppc['bus'][:, PD]
    Pd[[2, 3]] = load[0] * Pd[[2, 3]]
    Pd[[6, 7]] = load[1] * Pd[[6, 7]]
    t_is( bus[:, PD], Pd, 8, t)

    t_end()


if __name__ == '__main__':
    t_scale_load(quiet=False)
