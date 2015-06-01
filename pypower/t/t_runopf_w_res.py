# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests C{runopf_w_res} and the associated callbacks.
"""

from os.path import dirname, join

from numpy import delete

from pypower.ppoption import ppoption
from pypower.loadcase import loadcase
from pypower.runopf_w_res import runopf_w_res

from pypower.idx_gen import GEN_STATUS, RAMP_10

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end


def t_runopf_w_res(quiet=False):
    """Tests C{runopf_w_res} and the associated callbacks.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    t_begin(46, quiet)

    verbose = 0#not quiet

    tdir = dirname(__file__)
    casefile = join(tdir, 't_case30_userfcns')

    ppopt = ppoption(OPF_VIOLATION=1e-6, PDIPM_GRADTOL=1e-8,
                     PDIPM_COMPTOL=1e-8, PDIPM_COSTTOL=1e-9)
    ppopt = ppoption(ppopt, OUT_ALL=0, VERBOSE=verbose, OPF_ALG=560)

    t = 'runopf_w_res(''t_case30_userfcns'') : '
    r = runopf_w_res(casefile, ppopt)
    t_is(r['reserves']['R'], [25, 15, 0, 0, 19.3906, 0.6094], 4, [t, 'R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 2, 5.5, 5.5], 6, [t, 'prc'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 2, 0, 0], 7, [t, 'mu.l'])
    t_is(r['reserves']['mu']['u'], [0.1, 0, 0, 0, 0, 0], 7, [t, 'mu.u'])
    t_is(r['reserves']['mu']['Pmax'], [0, 0, 0, 0, 0.5, 0], 7, [t, 'mu.Pmax'])
    ppc = loadcase(casefile)
    t_is(r['reserves']['cost'], ppc['reserves']['cost'], 12, [t, 'cost'])
    t_is(r['reserves']['qty'], ppc['reserves']['qty'], 12, [t, 'qty'])
    t_is(r['reserves']['totalcost'], 177.8047, 4, [t, 'totalcost'])

    t = 'gen 5 no reserves : ';
    ppc = loadcase(casefile)
    ppc['reserves']['zones'][:, 4] = 0
    ppc['reserves']['cost'] = delete(ppc['reserves']['cost'], 4)
    ppc['reserves']['qty'] = delete(ppc['reserves']['qty'], 4)
    r = runopf_w_res(ppc, ppopt)
    t_is(r['reserves']['R'], [25, 15, 0, 0, 0, 20], 4, [t, 'R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 2, 0, 5.5], 6, [t, 'prc'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 2, 0, 0], 7, [t, 'mu.l'])
    t_is(r['reserves']['mu']['u'], [0.1, 0, 0, 0, 0, 0], 6, [t, 'mu.u'])
    t_is(r['reserves']['mu']['Pmax'], [0, 0, 0, 0, 0, 0], 7, [t, 'mu.Pmax'])
    t_is(r['reserves']['cost'], ppc['reserves']['cost'], 12, [t, 'cost'])
    t_is(r['reserves']['qty'], ppc['reserves']['qty'], 12, [t, 'qty'])
    t_is(r['reserves']['totalcost'], 187.5, 4, [t, 'totalcost'])

    t = 'extra offline gen : ';
    ppc = loadcase(casefile)
    idx = list(range(3)) + [4] + list(range(3, 6))
    ppc['gen'] = ppc['gen'][idx, :]
    ppc['gencost'] = ppc['gencost'][idx, :]
    ppc['reserves']['zones'] = ppc['reserves']['zones'][:, idx]
    ppc['reserves']['cost'] = ppc['reserves']['cost'][idx]
    ppc['reserves']['qty'] = ppc['reserves']['qty'][idx]
    ppc['gen'][3, GEN_STATUS] = 0
    r = runopf_w_res(ppc, ppopt)
    t_is(r['reserves']['R'], [25, 15, 0, 0, 0, 19.3906, 0.6094], 4, [t, 'R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 5.5, 2, 5.5, 5.5], 6, [t, 'prc'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 0, 2, 0, 0], 7, [t, 'mu.l'])
    t_is(r['reserves']['mu']['u'], [0.1, 0, 0, 0, 0, 0, 0], 7, [t, 'mu.u'])
    t_is(r['reserves']['mu']['Pmax'], [0, 0, 0, 0, 0, 0.5, 0], 7, [t, 'mu.Pmax'])
    t_is(r['reserves']['cost'], ppc['reserves']['cost'], 12, [t, 'cost'])
    t_is(r['reserves']['qty'], ppc['reserves']['qty'], 12, [t, 'qty'])
    t_is(r['reserves']['totalcost'], 177.8047, 4, [t, 'totalcost'])

    t = 'both extra & gen 6 no res : ';
    ppc = loadcase(casefile)
    idx = list(range(3)) + [4] + list(range(3, 6))
    ppc['gen'] = ppc['gen'][idx, :]
    ppc['gencost'] = ppc['gencost'][idx, :]
    ppc['reserves']['zones'] = ppc['reserves']['zones'][:, idx]
    ppc['reserves']['cost'] = ppc['reserves']['cost'][idx]
    ppc['reserves']['qty'] = ppc['reserves']['qty'][idx]
    ppc['gen'][3, GEN_STATUS] = 0
    ppc['reserves']['zones'][:, 5] = 0
    ppc['reserves']['cost'] = delete(ppc['reserves']['cost'], 5)
    ppc['reserves']['qty'] = delete(ppc['reserves']['qty'], 5)
    r = runopf_w_res(ppc, ppopt)
    t_is(r['reserves']['R'], [25, 15, 0, 0, 0, 0, 20], 4, [t, 'R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 5.5, 2, 0, 5.5], 6, [t, 'prc'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 0, 2, 0, 0], 7, [t, 'mu.l'])
    t_is(r['reserves']['mu']['u'], [0.1, 0, 0, 0, 0, 0, 0], 6, [t, 'mu.u'])
    t_is(r['reserves']['mu']['Pmax'], [0, 0, 0, 0, 0, 0, 0], 7, [t, 'mu.Pmax'])
    t_is(r['reserves']['cost'], ppc['reserves']['cost'], 12, [t, 'cost'])
    t_is(r['reserves']['qty'], ppc['reserves']['qty'], 12, [t, 'qty'])
    t_is(r['reserves']['totalcost'], 187.5, 4, [t, 'totalcost'])

    t = 'no qty (Rmax) : '
    ppc = loadcase(casefile)
    del ppc['reserves']['qty']
    r = runopf_w_res(ppc, ppopt)
    t_is(r['reserves']['R'], [39.3826, 0.6174, 0, 0, 19.3818, 0.6182], 4, [t, 'R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 2, 5.5, 5.5], 5, [t, 'prc'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 2, 0, 0], 5, [t, 'mu.l'])
    t_is(r['reserves']['mu']['u'], [0, 0, 0, 0, 0, 0], 7, [t, 'mu.u'])
    t_is(r['reserves']['mu']['Pmax'], [0.1, 0, 0, 0, 0.5, 0], 5, [t, 'mu.Pmax'])
    t_is(r['reserves']['cost'], ppc['reserves']['cost'], 12, [t, 'cost'])
    t_is(r['reserves']['totalcost'], 176.3708, 4, [t, 'totalcost'])

    t = 'RAMP_10, no qty (Rmax) : ';
    ppc = loadcase(casefile)
    del ppc['reserves']['qty']
    ppc['gen'][0, RAMP_10] = 25
    r = runopf_w_res(ppc, ppopt)
    t_is(r['reserves']['R'], [25, 15, 0, 0, 19.3906, 0.6094], 4, [t, 'R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 2, 5.5, 5.5], 6, [t, 'prc'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 2, 0, 0], 7, [t, 'mu.l'])
    t_is(r['reserves']['mu']['u'], [0.1, 0, 0, 0, 0, 0], 7, [t, 'mu.u'])
    t_is(r['reserves']['mu']['Pmax'], [0, 0, 0, 0, 0.5, 0], 7, [t, 'mu.Pmax'])
    t_is(r['reserves']['cost'], ppc['reserves']['cost'], 12, [t, 'cost'])
    t_is(r['reserves']['totalcost'], 177.8047, 4, [t, 'totalcost'])

    t_end()


if __name__ == '__main__':
    t_runopf_w_res(quiet=False)
