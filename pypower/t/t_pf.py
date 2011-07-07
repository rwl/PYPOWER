# Copyright (C) 2004-2011 Power System Engineering Research Center
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

"""Tests for power flow solvers.
"""

from os.path import dirname, join

from numpy import array, r_

from scipy.io import loadmat

from pypower.ppoption import ppoption
from pypower.loadcase import loadcase
from pypower.runpf import runpf
from pypower.rundcpf import rundcpf

from pypower.idx_gen import QG, QMIN, QMAX

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end


def t_pf(quiet=False):
    """Tests for power flow solvers.
    """
    t_begin(25, quiet)

    tdir = dirname(__file__)
    casefile = join(tdir, 't_case9_pf')
    verbose = not quiet

    ppopt = ppoption(VERBOSE=verbose, OUT_ALL=0)

    ## get solved AC power flow case from MAT-file
    ## defines bus_soln, gen_soln, branch_soln
    soln9_pf = loadmat(join(tdir, 'soln9_pf.mat'), struct_as_record=False)
    bus_soln = soln9_pf['bus_soln']
    gen_soln = soln9_pf['gen_soln']
    branch_soln = soln9_pf['branch_soln']

    ## run Newton PF
    t = 'Newton PF : ';
    ppopt = ppoption(ppopt, PF_ALG=1)
    results, success = runpf(casefile, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_ok(success, [t, 'success'])
    t_is(bus, bus_soln, 6, [t, 'bus'])
    t_is(gen, gen_soln, 6, [t, 'gen'])
    t_is(branch, branch_soln, 6, [t, 'branch'])

    ## run fast-decoupled PF (XB version)
    t = 'Fast Decoupled (XB) PF : ';
    ppopt = ppoption(ppopt, PF_ALG=2)
    results, success = runpf(casefile, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_ok(success, [t, 'success'])
    t_is(bus, bus_soln, 6, [t, 'bus'])
    t_is(gen, gen_soln, 6, [t, 'gen'])
    t_is(branch, branch_soln, 6, [t, 'branch'])

    ## run fast-decoupled PF (BX version)
    t = 'Fast Decoupled (BX) PF : ';
    ppopt = ppoption(ppopt, PF_ALG=3)
    results, success = runpf(casefile, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_ok(success, [t, 'success'])
    t_is(bus, bus_soln, 6, [t, 'bus'])
    t_is(gen, gen_soln, 6, [t, 'gen'])
    t_is(branch, branch_soln, 6, [t, 'branch'])

    ## run Gauss-Seidel PF
    t = 'Gauss-Seidel PF : ';
    ppopt = ppoption(ppopt, PF_ALG=4)
    results, success = runpf(casefile, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_ok(success, [t, 'success'])
    t_is(bus, bus_soln, 5, [t, 'bus'])
    t_is(gen, gen_soln, 5, [t, 'gen'])
    t_is(branch, branch_soln, 5, [t, 'branch'])

    ## get solved AC power flow case from MAT-file
    ## defines bus_soln, gen_soln, branch_soln
    soln9_dcpf = loadmat(join(tdir, 'soln9_dcpf.mat'), struct_as_record=False)
    bus_soln = soln9_dcpf['bus_soln']
    gen_soln = soln9_dcpf['gen_soln']
    branch_soln = soln9_dcpf['branch_soln']

    ## run DC PF
    t = 'DC PF : '
    results, success = rundcpf(casefile, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_ok(success, [t, 'success'])
    t_is(bus, bus_soln, 6, [t, 'bus'])
    t_is(gen, gen_soln, 6, [t, 'gen'])
    t_is(branch, branch_soln, 6, [t, 'branch'])

    ## check Qg distribution, when Qmin = Qmax
    t = 'check Qg : '
    ppopt = ppoption(ppopt, PF_ALG=1, VERBOSE=0)
    ppc = loadcase(casefile)
    ppc['gen'][0, [QMIN, QMAX]] = [20, 20]
    results, success = runpf(ppc, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_is(gen[0, QG], 24.07, 2, [t, 'single gen, Qmin = Qmax'])

    ppc['gen'] = r_[array([ ppc['gen'][0, :] ]), ppc['gen']]
    ppc['gen'][0, [QMIN, QMAX]] = [10, 10]
    ppc['gen'][1, [QMIN, QMAX]] = [ 0, 50]
    results, success = runpf(ppc, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_is(gen[0:2, QG], [10, 14.07], 2, [t, '2 gens, Qmin = Qmax for one'])

    ppc['gen'][0, [QMIN, QMAX]] = [10, 10]
    ppc['gen'][1, [QMIN, QMAX]] = [-50, -50]
    results, success = runpf(ppc, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_is(gen[0:2, QG], [12.03, 12.03], 2, [t, '2 gens, Qmin = Qmax for both'])

    ppc['gen'][0, [QMIN, QMAX]] = [0,  50]
    ppc['gen'][1, [QMIN, QMAX]] = [0, 100]
    results, success = runpf(ppc, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_is(gen[0:2, QG], [8.02, 16.05], 2, [t, '2 gens, proportional'])

    ppc['gen'][0, [QMIN, QMAX]] = [-50, 0]
    ppc['gen'][1, [QMIN, QMAX]] = [50, 150]
    results, success = runpf(ppc, ppopt)
    bus, gen, branch = results['bus'], results['gen'], results['branch']
    t_is(gen[0:2, QG], [-50 + 8.02, 50 + 16.05], 2, [t, '2 gens, proportional'])

    t_end()


if __name__ == '__main__':
    t_pf(quiet=False)
