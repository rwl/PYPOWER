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

"""Tests C{ext2int} and C{int2ext}.
"""

from numpy import ones, delete, c_, r_

from pypower.loadcase import loadcase
from pypower.ext2int import ext2int
from pypower.int2ext import int2ext

from pypower.t.t_begin import t_begin
from pypower.t.t_end import t_end
from pypower.t.t_is import t_is

from pypower.t.t_case_ext import t_case_ext
from pypower.t.t_case_int import t_case_int


def t_ext2int2ext(quiet=False):
    """Tests C{ext2int} and C{int2ext}.
    """
    t_begin(85, quiet)

    ##-----  ppc = ext2int/int2ext(ppc)  -----
    t = 'ppc = ext2int(ppc) : '
    ppce = loadcase(t_case_ext())
    ppci = loadcase(t_case_int())
    ppc = ext2int(ppce)
    t_is(ppc['bus'], ppci['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppci['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppci['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppci['gencost'], 12, [t, 'gencost'])
    t_is(ppc['areas'], ppci['areas'], 12, [t, 'areas'])
    t_is(ppc['A'], ppci['A'], 12, [t, 'A'])
    t_is(ppc['N'], ppci['N'], 12, [t, 'N'])
    t = 'ppc = ext2int(ppc) - repeat : '
    ppc = ext2int(ppc)
    t_is(ppc['bus'], ppci['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppci['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppci['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppci['gencost'], 12, [t, 'gencost'])
    t_is(ppc['areas'], ppci['areas'], 12, [t, 'areas'])
    t_is(ppc['A'], ppci['A'], 12, [t, 'A'])
    t_is(ppc['N'], ppci['N'], 12, [t, 'N'])
    t = 'ppc = int2ext(ppc) : '
    ppc = int2ext(ppc)
    t_is(ppc['bus'], ppce['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppce['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppce['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppce['gencost'], 12, [t, 'gencost'])
    t_is(ppc['areas'], ppce['areas'], 12, [t, 'areas'])
    t_is(ppc['A'], ppce['A'], 12, [t, 'A'])
    t_is(ppc['N'], ppce['N'], 12, [t, 'N'])

    ##-----  val = ext2int/int2ext(ppc, val, ...)  -----
    t = 'val = ext2int(ppc, val, \'bus\')'
    ppc = ext2int(ppce)
    got = ext2int(ppc, ppce['xbus'], 'bus')
    ex = ppce['xbus']
    ex = delete(ex, 5, 0)
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'bus\')'
    tmp = ones(ppce['xbus'].shape)
    tmp[5, :] = ppce['xbus'][5, :]
    got = int2ext(ppc, ex, tmp, 'bus')
    t_is(got, ppce['xbus'], 12, t)

    t = 'val = ext2int(ppc, val, \'bus\', 1)'
    got = ext2int(ppc, ppce['xbus'], 'bus', 1)
    ex = ppce['xbus']
    ex = delete(ex, 5, 1)
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'bus\', 1)'
    tmp = ones(ppce['xbus'].shape)
    tmp[:, 5] = ppce['xbus'][:, 5]
    got = int2ext(ppc, ex, tmp, 'bus', 1)
    t_is(got, ppce['xbus'], 12, t)

    t = 'val = ext2int(ppc, val, \'gen\')'
    got = ext2int(ppc, ppce['xgen'], 'gen')
    ex = ppce['xgen'][[3, 1, 0], :]
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'gen\')'
    tmp = ones(ppce['xgen'].shape)
    tmp[2, :] = ppce['xgen'][2, :]
    got = int2ext(ppc, ex, tmp, 'gen')
    t_is(got, ppce['xgen'], 12, t)

    t = 'val = ext2int(ppc, val, \'gen\', 1)'
    got = ext2int(ppc, ppce['xgen'], 'gen', 1)
    ex = ppce['xgen'][:, [3, 1, 0]]
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'gen\', 1)'
    tmp = ones(ppce['xgen'].shape)
    tmp[:, 2] = ppce['xgen'][:, 2]
    got = int2ext(ppc, ex, tmp, 'gen', 1)
    t_is(got, ppce['xgen'], 12, t)

    t = 'val = ext2int(ppc, val, \'branch\')'
    got = ext2int(ppc, ppce['xbranch'], 'branch')
    ex = ppce['xbranch']
    ex = delete(ex, 6, 0)
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'branch\')'
    tmp = ones(ppce['xbranch'].shape)
    tmp[6, :] = ppce['xbranch'][6, :]
    got = int2ext(ppc, ex, tmp, 'branch')
    t_is(got, ppce['xbranch'], 12, t)

    t = 'val = ext2int(ppc, val, \'branch\', 1)'
    got = ext2int(ppc, ppce['xbranch'], 'branch', 1)
    ex = ppce['xbranch']
    ex = delete(ex, 6, 1)
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'branch\', 1)'
    tmp = ones(ppce['xbranch'].shape)
    tmp[:, 6] = ppce['xbranch'][:, 6]
    got = int2ext(ppc, ex, tmp, 'branch', 1)
    t_is(got, ppce['xbranch'], 12, t)

    t = 'val = ext2int(ppc, val, {\'branch\', \'gen\', \'bus\'})'
    got = ext2int(ppc, ppce['xrows'], ['branch', 'gen', 'bus'])
    ex = r_[ppce['xbranch'][range(6) + range(7, 10), :4],
            ppce['xgen'][[3, 1, 0], :],
            ppce['xbus'][range(5) + range(6, 10), :4],
            -1 * ones((2, 4))]
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, {\'branch\', \'gen\', \'bus\'})'
    tmp1 = ones(ppce['xbranch'][:, :4].shape)
    tmp1[6, :4] = ppce['xbranch'][6, :4]
    tmp2 = ones(ppce['xgen'].shape)
    tmp2[2, :] = ppce['xgen'][2, :]
    tmp3 = ones(ppce['xbus'][:, :4].shape)
    tmp3[5, :4] = ppce['xbus'][5, :4]
    tmp = r_[tmp1, tmp2, tmp3]
    got = int2ext(ppc, ex, tmp, ['branch', 'gen', 'bus'])
    t_is(got, ppce['xrows'], 12, t)

    t = 'val = ext2int(ppc, val, {\'branch\', \'gen\', \'bus\'}, 1)'
    got = ext2int(ppc, ppce['xcols'], ['branch', 'gen', 'bus'], 1)
    ex = r_[ppce['xbranch'][range(6) + range(7, 10), :4],
            ppce['xgen'][[3, 1, 0], :],
            ppce['xbus'][range(5) + range(6, 10), :4],
            -1 * ones((2, 4))].T
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, {\'branch\', \'gen\', \'bus\'}, 1)'
    tmp1 = ones(ppce['xbranch'][:, :4].shape)
    tmp1[6, :4] = ppce['xbranch'][6, :4]
    tmp2 = ones(ppce['xgen'].shape)
    tmp2[2, :] = ppce['xgen'][2, :]
    tmp3 = ones(ppce['xbus'][:, :4].shape)
    tmp3[5, :4] = ppce['xbus'][5, :4]
    tmp = r_[tmp1, tmp2, tmp3].T
    got = int2ext(ppc, ex, tmp, ['branch', 'gen', 'bus'], 1)
    t_is(got, ppce['xcols'], 12, t)

    ##-----  ppc = ext2int/int2ext(ppc, field, ...)  -----
    t = 'ppc = ext2int(ppc, field, \'bus\')'
    ppc = ext2int(ppce)
    ex = ppce['xbus']
    ex = delete(ex, 5, 0)
    got = ext2int(ppc, 'xbus', 'bus')
    t_is(got['xbus'], ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'bus\')'
    got = int2ext(got, 'xbus', ordering='bus')
    t_is(got['xbus'], ppce['xbus'], 12, t)

    t = 'ppc = ext2int(ppc, field, \'bus\', 1)'
    ex = ppce['xbus']
    ex = delete(ex, 5, 1)
    got = ext2int(ppc, 'xbus', 'bus', 1)
    t_is(got['xbus'], ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'bus\', 1)'
    got = int2ext(got, 'xbus', ordering='bus', dim=1)
    t_is(got['xbus'], ppce['xbus'], 12, t)

    t = 'ppc = ext2int(ppc, field, \'gen\')'
    ex = ppce['xgen'][[3, 1, 0], :]
    got = ext2int(ppc, 'xgen', 'gen')
    t_is(got['xgen'], ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'gen\')'
    got = int2ext(got, 'xgen', ordering='gen')
    t_is(got['xgen'], ppce['xgen'], 12, t)

    t = 'ppc = ext2int(ppc, field, \'gen\', 1)'
    ex = ppce['xgen'][:, [3, 1, 0]]
    got = ext2int(ppc, 'xgen', 'gen', 1)
    t_is(got['xgen'], ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'gen\', 1)'
    got = int2ext(got, 'xgen', ordering='gen', dim=1)
    t_is(got['xgen'], ppce['xgen'], 12, t)

    t = 'ppc = ext2int(ppc, field, \'branch\')'
    ex = ppce['xbranch']
    ex = delete(ex, 6, 0)
    got = ext2int(ppc, 'xbranch', 'branch')
    t_is(got['xbranch'], ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'branch\')'
    got = int2ext(got, 'xbranch', ordering='branch')
    t_is(got['xbranch'], ppce['xbranch'], 12, t)

    t = 'ppc = ext2int(ppc, field, \'branch\', 1)'
    ex = ppce['xbranch']
    ex = delete(ex, 6, 1)
    got = ext2int(ppc, 'xbranch', 'branch', 1)
    t_is(got['xbranch'], ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'branch\', 1)'
    got = int2ext(got, 'xbranch', ordering='branch', dim=1)
    t_is(got['xbranch'], ppce['xbranch'], 12, t)

    t = 'ppc = ext2int(ppc, field, {\'branch\', \'gen\', \'bus\'})'
    ex = r_[ppce['xbranch'][range(6) + range(7, 10), :4],
            ppce['xgen'][[3, 1, 0], :],
            ppce['xbus'][range(5) + range(6, 10), :4],
            -1 * ones((2, 4))]
    got = ext2int(ppc, 'xrows', ['branch', 'gen', 'bus'])
    t_is(got['xrows'], ex, 12, t)
    t = 'ppc = int2ext(ppc, field, {\'branch\', \'gen\', \'bus\'})'
    got = int2ext(got, 'xrows', ordering=['branch', 'gen', 'bus'])
    t_is(got['xrows'], ppce['xrows'], 12, t)

    t = 'ppc = ext2int(ppc, field, {\'branch\', \'gen\', \'bus\'}, 1)'
    ex = r_[ppce['xbranch'][range(6) + range(7, 10), :4],
            ppce['xgen'][[3, 1, 0], :],
            ppce['xbus'][range(5) + range(6, 10), :4],
            -1 * ones((2, 4))].T
    got = ext2int(ppc, 'xcols', ['branch', 'gen', 'bus'], 1)
    t_is(got['xcols'], ex, 12, t)
    t = 'ppc = int2ext(ppc, field, {\'branch\', \'gen\', \'bus\'})'
    got = int2ext(got, 'xcols', ordering=['branch', 'gen', 'bus'], dim=1)
    t_is(got['xcols'], ppce['xcols'], 12, t)

    t = 'ppc = ext2int(ppc, {\'field1\', \'field2\'}, ordering)'
    ex = ppce['x']['more'][[3, 1, 0], :]
    got = ext2int(ppc, ['x', 'more'], 'gen')
    t_is(got['x']['more'], ex, 12, t)
    t = 'ppc = int2ext(ppc, {\'field1\', \'field2\'}, ordering)'
    got = int2ext(got, ['x', 'more'], ordering='gen')
    t_is(got['x']['more'], ppce['x']['more'], 12, t)

    t = 'ppc = ext2int(ppc, {\'field1\', \'field2\'}, ordering, 1)'
    ex = ppce['x']['more'][:, [3, 1, 0]]
    got = ext2int(ppc, ['x', 'more'], 'gen', 1)
    t_is(got['x']['more'], ex, 12, t)
    t = 'ppc = int2ext(ppc, {\'field1\', \'field2\'}, ordering, 1)'
    got = int2ext(got, ['x', 'more'], ordering='gen', dim=1)
    t_is(got['x']['more'], ppce['x']['more'], 12, t)

    ##-----  more ppc = ext2int/int2ext(ppc)  -----
    t = 'ppc = ext2int(ppc) - bus/gen/branch only : '
    ppce = loadcase(t_case_ext())
    ppci = loadcase(t_case_int())
    del ppce['gencost']
    del ppce['areas']
    del ppce['A']
    del ppce['N']
    del ppci['gencost']
    del ppci['areas']
    del ppci['A']
    del ppci['N']
    ppc = ext2int(ppce)
    t_is(ppc['bus'], ppci['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppci['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppci['gen'], 12, [t, 'gen'])

    t = 'ppc = ext2int(ppc) - no areas/A : '
    ppce = loadcase(t_case_ext())
    ppci = loadcase(t_case_int())
    del ppce['areas']
    del ppce['A']
    del ppci['areas']
    del ppci['A']
    ppc = ext2int(ppce)
    t_is(ppc['bus'], ppci['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppci['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppci['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppci['gencost'], 12, [t, 'gencost'])
    t_is(ppc['N'], ppci['N'], 12, [t, 'N'])

    t = 'ppc = ext2int(ppc) - Qg cost, no N : '
    ppce = loadcase(t_case_ext())
    ppci = loadcase(t_case_int())
    del ppce['N']
    del ppci['N']
    ppce['gencost'] = c_[ppce['gencost'], ppce['gencost']]
    ppci['gencost'] = c_[ppci['gencost'], ppci['gencost']]
    ppc = ext2int(ppce)
    t_is(ppc['bus'], ppci['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppci['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppci['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppci['gencost'], 12, [t, 'gencost'])
    t_is(ppc['areas'], ppci['areas'], 12, [t, 'areas'])
    t_is(ppc['A'], ppci['A'], 12, [t, 'A'])

    t = 'ppc = ext2int(ppc) - A, N are DC sized : '
    ppce = loadcase(t_case_ext())
    ppci = loadcase(t_case_int())
    eVmQgcols = range(10, 20) + range(24, 28)
    iVmQgcols = range(9, 18) + range(21, 24)
    ppce['A'] = delete(ppce['A'], eVmQgcols, 1)
    ppce['N'] = delete(ppce['N'], eVmQgcols, 1)
    ppci['A'] = delete(ppci['A'], iVmQgcols, 1)
    ppci['N'] = delete(ppci['N'], iVmQgcols, 1)
    ppc = ext2int(ppce)
    t_is(ppc['bus'], ppci['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppci['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppci['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppci['gencost'], 12, [t, 'gencost'])
    t_is(ppc['areas'], ppci['areas'], 12, [t, 'areas'])
    t_is(ppc['A'], ppci['A'], 12, [t, 'A'])
    t_is(ppc['N'], ppci['N'], 12, [t, 'N'])
    t = 'ppc = int2ext(ppc) - A, N are DC sized : '
    ppc = int2ext(ppc)
    t_is(ppc['bus'], ppce['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppce['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppce['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppce['gencost'], 12, [t, 'gencost'])
    t_is(ppc['areas'], ppce['areas'], 12, [t, 'areas'])
    t_is(ppc['A'], ppce['A'], 12, [t, 'A'])
    t_is(ppc['N'], ppce['N'], 12, [t, 'N'])

    t_end()


if __name__ == '__main__':
    t_ext2int2ext(False)
