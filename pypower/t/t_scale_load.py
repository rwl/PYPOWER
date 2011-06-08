# Copyright (C) 2008-2011 Power System Engineering Research Center
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

from numpy import array, zeros, r_, in1d, flatnonzero as find

from pypower.loadcase import loadcase
from pypower.isload import isload
from pypower.scale_load import scale_load

from pypower.idx_bus import PD, QD, BUS_AREA
from pypower.idx_gen import GEN_BUS, QG, PMIN, QMIN, QMAX

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end


def t_scale_load(quiet=False):
    """Tests for code in C{scale_load}.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    n_tests = 275

    t_begin(n_tests, quiet)

    ppc = loadcase('t_auction_case')
    ppc.gen[7, GEN_BUS] = 2    ## multiple d. loads per area, same bus as gen
    ppc.gen[7, [QG, QMIN, QMAX]] = array([3, 0, 3])
    ## put it load before gen in matrix
    ppc.gen = r_[ppc.gen[7, :], ppc.gen[:7, :], ppc.gen[8, :]]
    ld = find(isload(ppc.gen))
    a = [None] * 3
    lda = [None] * 3
    for k in range(3):
        a[k] = find(ppc.bus[:, BUS_AREA] == k)  ## buses in area k
        tmp = find( in1d(ppc.gen[ld, GEN_BUS], a[k]) )
        lda[k] = ld[tmp]                       ## disp loads in area k

    area = []
    for k in range(3):
        area[k] = {'fixed': {}, 'disp': {}, 'both': {}}
        area[k]['fixed']['p'] = sum(ppc.bus[a[k], PD])
        area[k]['fixed']['q'] = sum(ppc.bus[a[k], QD])
        area[k]['disp']['p'] = -sum(ppc.gen[lda[k], PMIN])
        area[k]['disp']['qmin'] = -sum(ppc.gen[lda[k], QMIN])
        area[k]['disp']['qmax'] = -sum(ppc.gen[lda[k], QMAX])
        area[k]['disp']['q'] = area[k]['disp']['qmin'] + area[k]['disp']['qmax']
        area[k]['both']['p'] = area[k]['fixed']['p'] + area[k]['disp']['p']
        area[k]['both']['q'] = area[k]['fixed']['q'] + area[k]['disp']['q']

    total = {'fixed': {}, 'disp': {}, 'both': {}}
    total['fixed']['p'] = sum(ppc.bus[:, PD])
    total['fixed']['q'] = sum(ppc.bus[:, QD])
    total['disp']['p'] = -sum(ppc.gen[ld, PMIN])
    total['disp']['qmin'] = -sum(ppc.gen[ld, QMIN])
    total['disp']['qmax'] = -sum(ppc.gen[ld, QMAX])
    total['disp']['q'] = total['disp']['qmin'] + total['disp']['qmax']
    total['both']['p'] = total['fixed']['p'] + total['disp']['p']
    total['both']['q'] = total['fixed']['q'] + total['disp']['q']

    ##-----  single load zone, one scale factor  -----
    load = 2
    t = 'all fixed loads (PQ) * 2 : '
    bus = scale_load(load, ppc.bus)
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load * total['fixed']['q'], 8, [t, 'total fixed Q'])
    opt = {'which': 'FIXED'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load * total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all fixed loads (P) * 2 : '
    opt = {'pq': 'P'}
    bus = scale_load(load, ppc.bus, [], [], opt)
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    opt = {'pq': 'P', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all loads (PQ) * 2 : '
    bus, gen = scale_load(load, ppc.bus, ppc.gen)
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load * total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load * total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), load * total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), load * total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all loads (P) * 2 : '
    opt = {'pq': 'P'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), load * total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load * total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all disp loads (PQ) * 2 : '
    opt = {'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load * total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), load * total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), load * total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all disp loads (P) * 2 : '
    opt = {'pq': 'P', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load * total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    ##-----  single load zone, one scale quantity  -----
    load = 200
    t = 'all fixed loads (PQ) => total = 200 : '
    opt = {'scale': 'QUANTITY'}
    bus = scale_load(load, ppc.bus, [], [], opt)
    t_is(sum(bus[:, PD]), load, 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load / total['fixed']['p'] * total['fixed']['q'], 8, [t, 'total fixed Q'])
    opt = {'scale': 'QUANTITY', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), load - total['disp']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), (load - total['disp']['p'])/total['fixed']['p']*total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all fixed loads (P) => total = 200 : '
    opt = {'scale': 'QUANTITY', 'pq': 'P'}
    bus = scale_load(load, ppc.bus, [], [], opt)
    t_is(sum(bus[:, PD]), load, 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    opt = {'scale': 'QUANTITY', 'pq': 'P', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), load - total['disp']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all loads (PQ) => total = 200 : '
    opt = {'scale': 'QUANTITY'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), load / total['both']['p']*total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), load / total['both']['p']*total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load / total['both']['p']*total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), load / total['both']['p']*total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), load / total['both']['p']*total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all loads (P) => total = 200 : '
    opt = {'scale': 'QUANTITY', 'pq': 'P'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), load / total['both']['p']*total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load / total['both']['p']*total['disp']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all disp loads (PQ) => total = 200 : '
    opt = {'scale': 'QUANTITY', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load - total['fixed']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), (load - total['fixed']['p'])/total['disp']['p']*total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), (load - total['fixed']['p'])/total['disp']['p']*total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    t = 'all disp loads (P) => total = 200 : '
    opt = {'scale': 'QUANTITY', 'pq': 'P', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    t_is(sum(bus[:, PD]), total['fixed']['p'], 8, [t, 'total fixed P'])
    t_is(sum(bus[:, QD]), total['fixed']['q'], 8, [t, 'total fixed Q'])
    t_is(-sum(gen[ld, PMIN]), load - total['fixed']['p'], 8, [t, 'total disp P'])
    t_is(-sum(gen[ld, QMIN]), total['disp']['qmin'], 8, [t, 'total disp Qmin'])
    t_is(-sum(gen[ld, QMAX]), total['disp']['qmax'], 8, [t, 'total disp Qmax'])

    ##-----  3 zones, area scale factors  -----
    t = 'area fixed loads (PQ) * [3 2 1] : '
    load = array([3, 2, 1])
    bus = scale_load(load, ppc.bus)
    for k in range(len(load)):
        t_is(sum(bus(a[k], PD)), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus(a[k], QD)), load[k] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))

    opt = {'which': 'FIXED'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), load[k] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area fixed loads (P) * [3 2 1] : '
    load = array([3, 2, 1])
    opt = {'pq': 'P'}
    bus = scale_load(load, ppc.bus, [], [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))

    opt = {'pq': 'P', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'all area loads (PQ) * [3 2 1] : '
    bus, gen = scale_load(load, ppc.bus, ppc.gen)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), load[k] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), load[k] * area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), load[k] * area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))


    t = 'all area loads (P) * [3 2 1] : '
    opt = {'pq': 'P'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area disp loads (PQ) * [3 2 1] : '
    opt = {'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), load[k] * area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), load[k] * area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area disp loads (P) * [3 2 1] : '
    opt = {'pq': 'P', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    ##-----  3 zones, area scale quantities  -----
    t = 'area fixed loads (PQ) => total = [100 80 60] : '
    load = array([100, 80, 60])
    opt = {'scale': 'QUANTITY'}
    bus = scale_load(load, ppc.bus, [], [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), load[k] / area[k]['fixed']['p'] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))

    opt = {'scale': 'QUANTITY', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] - area[k]['disp']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), (load[k] - area[k]['disp']['p']) / area[k]['fixed']['p'] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area fixed loads (P) => total = [100 80 60] : '
    load = array([100, 80, 60])
    opt = {'scale': 'QUANTITY', 'pq': 'P'}
    bus = scale_load(load, ppc.bus, [], [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))

    opt = {'scale': 'QUANTITY', 'pq': 'P', 'which': 'FIXED'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k]-area[k]['disp']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'all area loads (PQ) => total = [100 80 60] : '
    opt = {'scale': 'QUANTITY'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] / area[k]['both']['p'] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), load[k] / area[k]['both']['p'] * area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] / area[k]['both']['p'] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), load[k] / area[k]['both']['p'] * area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), load[k] / area[k]['both']['p'] * area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'all area loads (P) => total = [100 80 60] : '
    opt = {'scale': 'QUANTITY', 'pq': 'P'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), load[k] / area[k]['both']['p'] * area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k] / area[k]['both']['p'] * area[k]['disp']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    t = 'area disp loads (PQ) => total = [100 80 60] : throws expected exception'
    load = array([100, 80, 60])
    opt = {'scale': 'QUANTITY', 'which': 'DISPATCHABLE'}
    err = 0
    try:
        bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    except Exception, e:
        expected = 'scale_load: impossible to make zone 2 load equal 80 by scaling non-existent dispatchable load'
        err = expected not in e.msg

    t_ok(err, t)

    t = 'area disp loads (PQ) => total = [100 74.3941 60] : '
    load = array([100, area[1]['fixed']['p'], 60])
    opt = {'scale': 'QUANTITY', 'which': 'DISPATCHABLE'}
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
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
    bus, gen = scale_load(load, ppc.bus, ppc.gen, [], opt)
    for k in range(len(load)):
        t_is(sum(bus[a[k], PD]), area[k]['fixed']['p'], 8, '%s area %d fixed P' % (t, k))
        t_is(sum(bus[a[k], QD]), area[k]['fixed']['q'], 8, '%s area %d fixed Q' % (t, k))
        t_is(-sum(gen[lda[k], PMIN]), load[k]-area[k]['fixed']['p'], 8, '%s area %d disp P' % (t, k))
        t_is(-sum(gen[lda[k], QMIN]), area[k]['disp']['qmin'], 8, '%s area %d disp Qmin' % (t, k))
        t_is(-sum(gen[lda[k], QMAX]), area[k]['disp']['qmax'], 8, '%s area %d disp Qmax' % (t, k))

    ##-----  explict single load zone  -----
    t = 'explicit single load zone'
    load_zone = zeros((1, ppc.bus.size))
    load_zone[[2, 3]] = 1
    load = 2
    bus, gen = scale_load(load, ppc.bus, ppc.gen, load_zone)
    Pd = ppc.bus[:, PD]
    Pd[[2, 3]] = load * Pd([2, 3])
    t_is( bus[:, PD], Pd, 8, t)

    ##-----  explict multiple load zone  -----
    t = 'explicit multiple load zone'
    load_zone = zeros((1, ppc.bus.size))
    load_zone[[2, 3]] = 1
    load_zone[[6, 7]] = 2
    load = array([2, 0.5])
    bus, gen = scale_load(load, ppc.bus, ppc.gen, load_zone)
    Pd = ppc.bus[:, PD]
    Pd[[3, 4]] = load[0] * Pd[[3, 4]]
    Pd[[6, 7]] = load[1] * Pd[[6, 7]]
    t_is( bus[:, PD], Pd, 8, t)

    t_end()
