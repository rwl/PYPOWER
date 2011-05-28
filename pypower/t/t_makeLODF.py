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

from pypower.loadcase import loadcase
from pypower.ppoption import ppoption
from pypower.rundcopf import rundcopf
from pypower.ext2int import ext2int
from pypower.makePTDF import makePTDF
from pypower.makeLODF import makeLODF
from pypower.rundcpf import rundcpf

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end

def t_makeLODF(quiet=False):
    """Tests for C{makeLODF}.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ntests = 31
    t_begin(ntests, quiet)

    casefile = 't_auction_case'
    verbose = not quiet

    ## load case
    ppc = loadcase(casefile)
    opt = ppoption()
    opt['VERBOSE'] = 0
    opt['OUT_ALL'] = 0
    baseMVA, bus, gen, gencost, branch, f, success, et = rundcopf(ppc, mpopt)
    i2e, bus, gen, branch = ext2int(bus, gen, branch)

    ## compute injections and flows
    F0  = branch.Pf.copy()

    ## create some PTDF matrices
    H = makePTDF(baseMVA, bus, branch, 0)  # TODO Check zero based indexing

    ## create some PTDF matrices
    try:
        LODF = makeLODF(branch, H)
    except ZeroDivisionError:
        pass

    ## take out non-essential lines one-by-one and see what happens
    ppc.bus = bus.copy()
    ppc.gen = gen.copy()
    branch0 = branch.copy()
    outages = range(12) + range(13, 15) + range(16, 18) + [20] + range(26, 33) + range(34, 41)
    for k in outages:
        ppc.branch = branch0.copy()
        ppc.status[k] = 0
        baseMVA, bus, gen, branch, success, et = rundcpf(ppc, opt)
        F = branch.Pf.copy()

        t_is(LODF[:, k], (F - F0) / F0[k], 6, 'LODF(:, %d)' % k)

    t_end
