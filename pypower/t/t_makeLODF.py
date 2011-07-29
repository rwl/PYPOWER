# Copyright (C) 2008-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
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

"""Tests for C{makeLODF}.
"""

from os.path import dirname, join

from numpy import arange, r_

from pypower.loadcase import loadcase
from pypower.ppoption import ppoption
from pypower.rundcopf import rundcopf
from pypower.ext2int import ext2int1
from pypower.makePTDF import makePTDF
from pypower.makeLODF import makeLODF
from pypower.rundcpf import rundcpf

from pypower.idx_brch import BR_STATUS, PF

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end


def t_makeLODF(quiet=False):
    """Tests for C{makeLODF}.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ntests = 31
    t_begin(ntests, quiet)

    tdir = dirname(__file__)
    casefile = join(tdir, 't_auction_case')
    verbose = 0#not quiet

    ## load case
    ppc = loadcase(casefile)
    ppopt = ppoption(VERBOSE=verbose, OUT_ALL=0)
    r = rundcopf(ppc, ppopt)
    baseMVA, bus, gen, branch = r['baseMVA'], r['bus'], r['gen'], r['branch']
    _, bus, gen, branch = ext2int1(bus, gen, branch)

    ## compute injections and flows
    F0  = branch[:, PF]

    ## create some PTDF matrices
    H = makePTDF(baseMVA, bus, branch, 0)

    ## create some PTDF matrices
    try:
        LODF = makeLODF(branch, H)
    except ZeroDivisionError:
        pass

    ## take out non-essential lines one-by-one and see what happens
    ppc['bus'] = bus
    ppc['gen'] = gen
    branch0 = branch
    outages = r_[arange(12), arange(13, 15), arange(16, 18),
                 [19], arange(26, 33), arange(34, 41)]
    for k in outages:
        ppc['branch'] = branch0.copy()
        ppc['branch'][k, BR_STATUS] = 0
        r, _ = rundcpf(ppc, ppopt)
        baseMVA, bus, gen, branch = \
                r['baseMVA'], r['bus'], r['gen'], r['branch']
        F = branch[:, PF]

        t_is(LODF[:, k], (F - F0) / F0[k], 6, 'LODF[:, %d]' % k)

    t_end()


if __name__ == '__main__':
    t_makeLODF(quiet=False)
