# Copyright (C) 2008-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
