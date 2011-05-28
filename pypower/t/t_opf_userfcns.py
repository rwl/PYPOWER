# Copyright (C) 2009-2011 Power System Engineering Research Center
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

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    t_begin(38, quiet)

    casefile = 't_case30_userfcns';
    verbose = not quiet

    opt = ppoption
    opt['OPF_VIOLATION'] = 1e-6
    opt['PDIPM_GRADTOL'] = 1e-8
    opt['PDIPM_COMPTOL'] = 1e-8
    opt['PDIPM_COSTTOL'] = 1e-9
    opt['OUT_ALL'] = 0
    opt['VERBOSE'] = verbose
    opt['OPF_ALG'] = 560
    opt['OPF_ALG_DC'] = 200
    #opt['OUT_ALL'] = -1
    #opt['VERBOSE'] = 2
    #opt['OUT_GEN'] = 1

    ## run the OPF with fixed reserves
    t = 'fixed reserves : '
    ppc = loadcase(casefile)
    ppc = toggle_reserves(ppc, 'on')
    r = runopf(ppc, opt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['reserves']['R'], [25, 15, 0, 0, 19.3906, 0.6094], 4, [t, 'reserves.R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 2, 3.5, 3.5], 4, [t, 'reserves.prc'])
    t_is(r['reserves']['mu.Pmax'], [0, 0, 0, 0, 0.5, 0], 4, [t, 'reserves.mu.Pmax'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 2, 0, 0], 4, [t, 'reserves.mu.l'])
    t_is(r['reserves']['mu']['u'], [0.1, 0, 0, 0, 0, 0], 4, [t, 'reserves.mu.u'])
    t_ok('P' not in r['iface'], [t, 'no iflims'])
    t_is(r['reserves']['totalcost'], 177.8047, 4, [t, 'totalcost'])

    t = 'toggle_reserves(ppc, ''off'') : ';
    ppc = toggle_reserves(ppc, 'off')
    r = runopf(ppc, opt)
    t_ok(r['success'], [t, 'success'])
    t_ok('R' not in r['reserves'], [t, 'no reserves'])
    t_ok('P' not in r['iface'], [t, 'no iflims'])

    t = 'interface flow lims (DC) : ';
    ppc = loadcase(casefile)
    ppc = toggle_iflims(ppc, 'on')
    r = rundcopf(ppc, opt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['iface']['P'], [-15, 20], 4, [t, 'if.P'])
    t_is(r['iface']['mu']['l'], [4.8427, 0], 4, [t, 'if.mu.l'])
    t_is(r['iface']['mu']['u'], [0, 13.2573], 4, [t, 'if.mu.u'])
    t_is(r['branch'][13, PF], 8.244, 3, [t, 'flow in branch 14'])
    t_ok('R' not in r['reserves'], [t, 'no reserves'])

    t = 'reserves + interface flow lims (DC) : ';
    ppc = loadcase(casefile)
    ppc = toggle_reserves(ppc, 'on')
    ppc = toggle_iflims(ppc, 'on')
    r = rundcopf(ppc, opt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['iface']['P'], [-15, 20], 4, [t, 'if.P'])
    t_is(r['iface']['mu']['l'], [4.8427, 0], 4, [t, 'if.mu.l'])
    t_is(r['iface']['mu']['u'], [0, 38.2573], 4, [t, 'if.mu.u'])
    t_is(r['reserves']['R'], [25, 15, 0, 0, 16.9, 3.1], 4, [t, 'reserves.R'])
    t_is(r['reserves']['prc'], [2, 2, 2, 2, 3.5, 3.5], 4, [t, 'reserves.prc'])
    t_is(r['reserves']['mu.Pmax'], [0, 0, 0, 0, 0.5, 0], 4, [t, 'reserves.mu.Pmax'])
    t_is(r['reserves']['mu']['l'], [0, 0, 1, 2, 0, 0], 4, [t, 'reserves.mu.l'])
    t_is(r['reserves']['mu']['u'], [0.1, 0, 0, 0, 0, 0], 4, [t, 'reserves.mu.u'])
    t_is(r['reserves']['totalcost'], 179.05, 4, [t, 'totalcost'])

    t = 'interface flow lims (AC) : ';
    ppc = toggle_reserves(ppc, 'off')
    r = runopf(ppc, opt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['iface']['P'], [-9.101, 21.432], 3, [t, 'if.P'])
    t_is(r['iface']['mu']['l'], [0, 0], 4, [t, 'if.mu.l'])
    t_is(r['iface']['mu']['u'], [0, 10.198], 3, [t, 'if.mu.u'])
    t_ok('R' not in r['reserves'], [t, 'no reserves'])

    t = 'interface flow lims (line out) : ';
    ppc = loadcase(casefile)
    ppc = toggle_iflims(ppc, 'on')
    ppc.branch[11, BR_STATUS] = 0      ## take out line 6-10
    r = rundcopf(ppc, opt)
    t_ok(r['success'], [t, 'success'])
    t_is(r['iface']['P'], [-15, 20], 4, [t, 'if.P'])
    t_is(r['iface']['mu']['l'], [4.8427, 0], 4, [t, 'if.mu.l'])
    t_is(r['iface']['mu']['u'], [0, 13.2573], 4, [t, 'if.mu.u'])
    t_is(r['branch'][13, PF], 10.814, 3, [t, 'flow in branch 14'])
    t_ok('R' not in r['reserves'], [t, 'no reserves'])

    # r['reserves']['R']
    # r['reserves']['prc']
    # r['reserves']['mu.Pmax']
    # r['reserves']['mu']['l']
    # r['reserves']['mu']['u']
    # r['reserves']['totalcost']
    #
    # r['iface']['P']
    # r['iface']['mu']['l']
    # r['iface']['mu']['u']

    t_end
