# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for userfcn callbacks (reserves/iflims) w/OPF.
"""

from os.path import dirname, join

from pypower.ppoption import ppoption
from pypower.loadcase import loadcase
from pypower.toggle_reserves import toggle_reserves
from pypower.toggle_iflims import toggle_iflims
from pypower.runopf import runopf
from pypower.rundcopf import rundcopf

from pypower.idx_brch import PF, BR_STATUS

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end


def t_opf_userfcns(quiet=False):
    """Tests for userfcn callbacks (reserves/iflims) w/OPF.

    Includes high-level tests of reserves and iflims implementations.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    t_begin(38, quiet)

    tdir = dirname(__file__)
    casefile = join(tdir, 't_case30_userfcns')
    verbose = 0#not quiet

    ppopt = ppoption(OPF_VIOLATION=1e-6, PDIPM_GRADTOL=1e-8,
                     PDIPM_COMPTOL=1e-8, PDIPM_COSTTOL=1e-9)
    ppopt = ppoption(ppopt, OUT_ALL=0, VERBOSE=verbose,
                     OPF_ALG=560, OPF_ALG_DC=200)
    #ppopt = ppoption(ppopt, OUT_ALL=-1, VERBOSE=2, OUT_GEN=1)

    ## run the OPF with fixed reserves
    t = 'fixed reserves : '
    ppc = loadcase(casefile)
    ppc = toggle_reserves(ppc, 'on')
    r = runopf(ppc, ppopt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['reserves']['R'], [25, 15, 0, 0, 19.3906, 0.6094], 4, [t, 'reserves.R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 2, 5.5, 5.5], 4, [t, 'reserves.prc'])
    t_is(r['reserves']['mu']['Pmax'], [0, 0, 0, 0, 0.5, 0], 4, [t, 'reserves.mu.Pmax'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 2, 0, 0], 4, [t, 'reserves.mu.l'])
    t_is(r['reserves']['mu']['u'], [0.1, 0, 0, 0, 0, 0], 4, [t, 'reserves.mu.u'])
    t_ok('P' not in r['if'], [t, 'no iflims'])
    t_is(r['reserves']['totalcost'], 177.8047, 4, [t, 'totalcost'])

    t = 'toggle_reserves(ppc, \'off\') : ';
    ppc = toggle_reserves(ppc, 'off')
    r = runopf(ppc, ppopt)
    t_ok(r['success'], [t, 'success'])
    t_ok('R' not in r['reserves'], [t, 'no reserves'])
    t_ok('P' not in r['if'], [t, 'no iflims'])

    t = 'interface flow lims (DC) : '
    ppc = loadcase(casefile)
    ppc = toggle_iflims(ppc, 'on')
    r = rundcopf(ppc, ppopt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['if']['P'], [-15, 20], 4, [t, 'if.P'])
    t_is(r['if']['mu']['l'], [4.8427, 0], 4, [t, 'if.mu.l'])
    t_is(r['if']['mu']['u'], [0, 13.2573], 4, [t, 'if.mu.u'])
    t_is(r['branch'][13, PF], 8.244, 3, [t, 'flow in branch 14'])
    t_ok('R' not in r['reserves'], [t, 'no reserves'])

    t = 'reserves + interface flow lims (DC) : '
    ppc = loadcase(casefile)
    ppc = toggle_reserves(ppc, 'on')
    ppc = toggle_iflims(ppc, 'on')
    r = rundcopf(ppc, ppopt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['if']['P'], [-15, 20], 4, [t, 'if.P'])
    t_is(r['if']['mu']['l'], [4.8427, 0], 4, [t, 'if.mu.l'])
    t_is(r['if']['mu']['u'], [0, 38.2573], 4, [t, 'if.mu.u'])
    t_is(r['reserves']['R'], [25, 15, 0, 0, 16.9, 3.1], 4, [t, 'reserves.R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 2, 5.5, 5.5], 4, [t, 'reserves.prc'])
    t_is(r['reserves']['mu']['Pmax'], [0, 0, 0, 0, 0.5, 0], 4, [t, 'reserves.mu.Pmax'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 2, 0, 0], 4, [t, 'reserves.mu.l'])
    t_is(r['reserves']['mu']['u'], [0.1, 0, 0, 0, 0, 0], 4, [t, 'reserves.mu.u'])
    t_is(r['reserves']['totalcost'], 179.05, 4, [t, 'totalcost'])

    t = 'interface flow lims (AC) : '
    ppc = toggle_reserves(ppc, 'off')
    r = runopf(ppc, ppopt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['if']['P'], [-9.101, 21.432], 3, [t, 'if.P'])
    t_is(r['if']['mu']['l'], [0, 0], 4, [t, 'if.mu.l'])
    t_is(r['if']['mu']['u'], [0, 10.198], 3, [t, 'if.mu.u'])
    t_ok('R' not in r['reserves'], [t, 'no reserves'])

    t = 'interface flow lims (line out) : '
    ppc = loadcase(casefile)
    ppc = toggle_iflims(ppc, 'on')
    ppc['branch'][11, BR_STATUS] = 0      ## take out line 6-10
    r = rundcopf(ppc, ppopt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['if']['P'], [-15, 20], 4, [t, 'if.P'])
    t_is(r['if']['mu']['l'], [4.8427, 0], 4, [t, 'if.mu.l'])
    t_is(r['if']['mu']['u'], [0, 13.2573], 4, [t, 'if.mu.u'])
    t_is(r['branch'][13, PF], 10.814, 3, [t, 'flow in branch 14'])
    t_ok('R' not in r['reserves'], [t, 'no reserves'])

    # r['reserves']['R']
    # r['reserves']['prc']
    # r['reserves']['mu.Pmax']
    # r['reserves']['mu']['l']
    # r['reserves']['mu']['u']
    # r['reserves']['totalcost']
    #
    # r['if']['P']
    # r['if']['mu']['l']
    # r['if']['mu']['u']

    t_end()


if __name__ == '__main__':
    t_opf_userfcns(quiet=False)
