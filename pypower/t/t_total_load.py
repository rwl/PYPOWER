# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for code in C{total_load}.
"""

from os.path import dirname, join

from numpy import array, zeros, r_, in1d, vstack, flatnonzero as find

from pypower.loadcase import loadcase
from pypower.isload import isload
from pypower.total_load import total_load

from pypower.idx_bus import PD, QD, BUS_AREA
from pypower.idx_gen import GEN_BUS, QG, PMIN, QMIN, QMAX

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end


def t_total_load(quiet=False):
    """Tests for code in C{total_load}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    n_tests = 48

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

    ##-----  all load  -----
    t = 'Pd, _  = total_load(bus) : '
    Pd, _ = total_load(ppc['bus'])
    t_is(Pd, [area[0]['fixed']['p'], area[1]['fixed']['p'], area[2]['fixed']['p']], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus) : '
    Pd, Qd = total_load(ppc['bus'])
    t_is(Pd, [area[0]['fixed']['p'], area[1]['fixed']['p'], area[2]['fixed']['p']], 12, [t, 'Pd'])
    t_is(Qd, [area[0]['fixed']['q'], area[1]['fixed']['q'], area[2]['fixed']['q']], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen) : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'])
    t_is(Pd, [area[0]['both']['p'], area[1]['both']['p'], area[2]['both']['p']], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen) : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'])
    t_is(Pd, [area[0]['both']['p'], area[1]['both']['p'], area[2]['both']['p']], 12, [t, 'Pd'])
    t_is(Qd, [area[0]['both']['q'], area[1]['both']['q'], area[2]['both']['q']], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, None, \'all\') : '
    Pd, _ = total_load(ppc['bus'], None, 'all')
    t_is(Pd, total['fixed']['p'], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, None, \'all\') : '
    Pd, Qd = total_load(ppc['bus'], None, 'all')
    t_is(Pd, total['fixed']['p'], 12, [t, 'Pd'])
    t_is(Qd, total['fixed']['q'], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, \'all\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], 'all')
    t_is(Pd, total['both']['p'], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, \'all\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], 'all')
    t_is(Pd, total['both']['p'], 12, [t, 'Pd'])
    t_is(Qd, total['both']['q'], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, \'all\', \'BOTH\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], 'all', 'BOTH')
    t_is(Pd, total['both']['p'], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, \'all\', \'BOTH\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], 'all', 'BOTH')
    t_is(Pd, total['both']['p'], 12, [t, 'Pd'])
    t_is(Qd, total['both']['q'], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, \'all\', \'FIXED\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], 'all', 'FIXED')
    t_is(Pd, total['fixed']['p'], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, \'all\', \'FIXED\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], 'all', 'FIXED')
    t_is(Pd, total['fixed']['p'], 12, [t, 'Pd'])
    t_is(Qd, total['fixed']['q'], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, \'all\', \'DISPATCHABLE\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], 'all', 'DISPATCHABLE')
    t_is(Pd, total['disp']['p'], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, \'all\', \'DISPATCHABLE\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], 'all', 'DISPATCHABLE')
    t_is(Pd, total['disp']['p'], 12, [t, 'Pd'])
    t_is(Qd, total['disp']['q'], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, None, \'BOTH\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], None, 'BOTH')
    t_is(Pd, r_[area[0]['both']['p'], area[1]['both']['p'], area[2]['both']['p']], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, None, \'BOTH\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], None, 'BOTH')
    t_is(Pd, [area[0]['both']['p'], area[1]['both']['p'], area[2]['both']['p']], 12, [t, 'Pd'])
    t_is(Qd, [area[0]['both']['q'], area[1]['both']['q'], area[2]['both']['q']], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, None, \'FIXED\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], None, 'FIXED')
    t_is(Pd, [area[0]['fixed']['p'], area[1]['fixed']['p'], area[2]['fixed']['p']], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, None, \'FIXED\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], None, 'FIXED')
    t_is(Pd, [area[0]['fixed']['p'], area[1]['fixed']['p'], area[2]['fixed']['p']], 12, [t, 'Pd'])
    t_is(Qd, [area[0]['fixed']['q'], area[1]['fixed']['q'], area[2]['fixed']['q']], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, None, \'DISPATCHABLE\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], None, 'DISPATCHABLE')
    t_is(Pd, [area[0]['disp']['p'], area[1]['disp']['p'], area[2]['disp']['p']], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, None, \'DISPATCHABLE\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], None, 'DISPATCHABLE')
    t_is(Pd, [area[0]['disp']['p'], area[1]['disp']['p'], area[2]['disp']['p']], 12, [t, 'Pd'])
    t_is(Qd, [area[0]['disp']['q'], area[1]['disp']['q'], area[2]['disp']['q']], 12, [t, 'Qd'])

    ##-----  explicit single load zone  -----
    nb = ppc['bus'].shape[0]
    load_zone = zeros(nb, int)
    k = find(ppc['bus'][:, BUS_AREA] == 2)    ## area 2
    load_zone[k] = 1
    t = 'Pd, _  = total_load(bus, gen, load_zone1, \'BOTH\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], load_zone, 'BOTH')
    t_is(Pd, area[1]['both']['p'], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, load_zone1, \'BOTH\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], load_zone, 'BOTH')
    t_is(Pd, area[1]['both']['p'], 12, [t, 'Pd'])
    t_is(Qd, area[1]['both']['q'], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, load_zone1, \'FIXED\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], load_zone, 'FIXED')
    t_is(Pd, area[1]['fixed']['p'], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, load_zone1, \'FIXED\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], load_zone, 'FIXED')
    t_is(Pd, area[1]['fixed']['p'], 12, [t, 'Pd'])
    t_is(Qd, area[1]['fixed']['q'], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, load_zone1, \'DISPATCHABLE\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], load_zone, 'DISPATCHABLE')
    t_is(Pd, area[1]['disp']['p'], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, load_zone1, \'DISPATCHABLE\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], load_zone, 'DISPATCHABLE')
    t_is(Pd, area[1]['disp']['p'], 12, [t, 'Pd'])
    t_is(Qd, area[1]['disp']['q'], 12, [t, 'Qd'])

    ##-----  explicit multiple load zone  -----
    load_zone = zeros(nb, int)
    k = find(ppc['bus'][:, BUS_AREA] == 3)    ## area 3
    load_zone[k] = 1
    k = find(ppc['bus'][:, BUS_AREA] == 1)    ## area 1
    load_zone[k] = 2
    t = 'Pd, _  = total_load(bus, gen, load_zone2, \'BOTH\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], load_zone, 'BOTH')
    t_is(Pd, [area[2]['both']['p'], area[0]['both']['p']], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, load_zone2, \'BOTH\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], load_zone, 'BOTH')
    t_is(Pd, [area[2]['both']['p'], area[0]['both']['p']], 12, [t, 'Pd'])
    t_is(Qd, [area[2]['both']['q'], area[0]['both']['q']], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, load_zone2, \'FIXED\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], load_zone, 'FIXED')
    t_is(Pd, [area[2]['fixed']['p'], area[0]['fixed']['p']], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, load_zone2, \'FIXED\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], load_zone, 'FIXED')
    t_is(Pd, [area[2]['fixed']['p'], area[0]['fixed']['p']], 12, [t, 'Pd'])
    t_is(Qd, [area[2]['fixed']['q'], area[0]['fixed']['q']], 12, [t, 'Qd'])

    t = 'Pd, _  = total_load(bus, gen, load_zone2, \'DISPATCHABLE\') : '
    Pd, _ = total_load(ppc['bus'], ppc['gen'], load_zone, 'DISPATCHABLE')
    t_is(Pd, [area[2]['disp']['p'], area[0]['disp']['p']], 12, [t, 'Pd'])

    t = 'Pd, Qd = total_load(bus, gen, load_zone2, \'DISPATCHABLE\') : '
    Pd, Qd = total_load(ppc['bus'], ppc['gen'], load_zone, 'DISPATCHABLE')
    t_is(Pd, [area[2]['disp']['p'], area[0]['disp']['p']], 12, [t, 'Pd'])
    t_is(Qd, [area[2]['disp']['q'], area[0]['disp']['q']], 12, [t, 'Qd'])

    t_end()


if __name__ == '__main__':
    t_total_load(quiet=False)
