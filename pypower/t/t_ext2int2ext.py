# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests C{ext2int} and C{int2ext}.
"""

from numpy import ones, delete, c_, r_

from pypower.loadcase import loadcase
from pypower.e2i_data import e2i_data
from pypower.i2e_data import i2e_data
from pypower.e2i_field import e2i_field
from pypower.i2e_field import i2e_field
from pypower.ext2int import ext2int
from pypower.int2ext import int2ext

from pypower.t.t_begin import t_begin
from pypower.t.t_end import t_end
from pypower.t.t_is import t_is

from pypower.t.t_case_ext import t_case_ext
from pypower.t.t_case_int import t_case_int


def t_ext2int2ext(quiet=False):
    """Tests C{ext2int} and C{int2ext}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    t_begin(85, quiet)

    ##-----  ppc = e2i_data/i2e_data(ppc)  -----
    t = 'ppc = e2i_data(ppc) : '
    ppce = loadcase(t_case_ext())
    ppci = loadcase(t_case_int())
    ppc = e2i_data(ppce)
    t_is(ppc['bus'], ppci['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppci['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppci['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppci['gencost'], 12, [t, 'gencost'])
    t_is(ppc['areas'], ppci['areas'], 12, [t, 'areas'])
    t_is(ppc['A'], ppci['A'], 12, [t, 'A'])
    t_is(ppc['N'], ppci['N'], 12, [t, 'N'])
    t = 'ppc = e2i_data(ppc) - repeat : '
    ppc = e2i_data(ppc)
    t_is(ppc['bus'], ppci['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppci['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppci['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppci['gencost'], 12, [t, 'gencost'])
    t_is(ppc['areas'], ppci['areas'], 12, [t, 'areas'])
    t_is(ppc['A'], ppci['A'], 12, [t, 'A'])
    t_is(ppc['N'], ppci['N'], 12, [t, 'N'])
    t = 'ppc = i2e_data(ppc) : '
    ppc = i2e_data(ppc)
    t_is(ppc['bus'], ppce['bus'], 12, [t, 'bus'])
    t_is(ppc['branch'], ppce['branch'], 12, [t, 'branch'])
    t_is(ppc['gen'], ppce['gen'], 12, [t, 'gen'])
    t_is(ppc['gencost'], ppce['gencost'], 12, [t, 'gencost'])
    t_is(ppc['areas'], ppce['areas'], 12, [t, 'areas'])
    t_is(ppc['A'], ppce['A'], 12, [t, 'A'])
    t_is(ppc['N'], ppce['N'], 12, [t, 'N'])

    ##-----  val = e2i_data/i2e_data(ppc, val, ...)  -----
    t = 'val = e2i_data(ppc, val, \'bus\')'
    ppc = e2i_data(ppce)
    got = e2i_data(ppc, ppce['xbus'], 'bus')
    ex = ppce['xbus']
    ex = delete(ex, 5, 0)
    t_is(got, ex, 12, t)
    t = 'val = i2e_data(ppc, val, oldval, \'bus\')'
    tmp = ones(ppce['xbus'].shape)
    tmp[5, :] = ppce['xbus'][5, :]
    got = i2e_data(ppc, ex, tmp, 'bus')
    t_is(got, ppce['xbus'], 12, t)

    t = 'val = e2i_data(ppc, val, \'bus\', 1)'
    got = e2i_data(ppc, ppce['xbus'], 'bus', 1)
    ex = ppce['xbus']
    ex = delete(ex, 5, 1)
    t_is(got, ex, 12, t)
    t = 'val = i2e_data(ppc, val, oldval, \'bus\', 1)'
    tmp = ones(ppce['xbus'].shape)
    tmp[:, 5] = ppce['xbus'][:, 5]
    got = i2e_data(ppc, ex, tmp, 'bus', 1)
    t_is(got, ppce['xbus'], 12, t)

    t = 'val = e2i_data(ppc, val, \'gen\')'
    got = e2i_data(ppc, ppce['xgen'], 'gen')
    ex = ppce['xgen'][[3, 1, 0], :]
    t_is(got, ex, 12, t)
    t = 'val = i2e_data(ppc, val, oldval, \'gen\')'
    tmp = ones(ppce['xgen'].shape)
    tmp[2, :] = ppce['xgen'][2, :]
    got = i2e_data(ppc, ex, tmp, 'gen')
    t_is(got, ppce['xgen'], 12, t)

    t = 'val = e2i_data(ppc, val, \'gen\', 1)'
    got = e2i_data(ppc, ppce['xgen'], 'gen', 1)
    ex = ppce['xgen'][:, [3, 1, 0]]
    t_is(got, ex, 12, t)
    t = 'val = i2e_data(ppc, val, oldval, \'gen\', 1)'
    tmp = ones(ppce['xgen'].shape)
    tmp[:, 2] = ppce['xgen'][:, 2]
    got = i2e_data(ppc, ex, tmp, 'gen', 1)
    t_is(got, ppce['xgen'], 12, t)

    t = 'val = e2i_data(ppc, val, \'branch\')'
    got = e2i_data(ppc, ppce['xbranch'], 'branch')
    ex = ppce['xbranch']
    ex = delete(ex, 6, 0)
    t_is(got, ex, 12, t)
    t = 'val = i2e_data(ppc, val, oldval, \'branch\')'
    tmp = ones(ppce['xbranch'].shape)
    tmp[6, :] = ppce['xbranch'][6, :]
    got = i2e_data(ppc, ex, tmp, 'branch')
    t_is(got, ppce['xbranch'], 12, t)

    t = 'val = e2i_data(ppc, val, \'branch\', 1)'
    got = e2i_data(ppc, ppce['xbranch'], 'branch', 1)
    ex = ppce['xbranch']
    ex = delete(ex, 6, 1)
    t_is(got, ex, 12, t)
    t = 'val = i2e_data(ppc, val, oldval, \'branch\', 1)'
    tmp = ones(ppce['xbranch'].shape)
    tmp[:, 6] = ppce['xbranch'][:, 6]
    got = i2e_data(ppc, ex, tmp, 'branch', 1)
    t_is(got, ppce['xbranch'], 12, t)

    t = 'val = e2i_data(ppc, val, {\'branch\', \'gen\', \'bus\'})'
    got = e2i_data(ppc, ppce['xrows'], ['branch', 'gen', 'bus'])
    ex = r_[ppce['xbranch'][list(range(6)) + list(range(7, 10)), :4],
            ppce['xgen'][[3, 1, 0], :],
            ppce['xbus'][list(range(5)) + list(range(6, 10)), :4],
            -1 * ones((2, 4))]
    t_is(got, ex, 12, t)
    t = 'val = i2e_data(ppc, val, oldval, {\'branch\', \'gen\', \'bus\'})'
    tmp1 = ones(ppce['xbranch'][:, :4].shape)
    tmp1[6, :4] = ppce['xbranch'][6, :4]
    tmp2 = ones(ppce['xgen'].shape)
    tmp2[2, :] = ppce['xgen'][2, :]
    tmp3 = ones(ppce['xbus'][:, :4].shape)
    tmp3[5, :4] = ppce['xbus'][5, :4]
    tmp = r_[tmp1, tmp2, tmp3]
    got = i2e_data(ppc, ex, tmp, ['branch', 'gen', 'bus'])
    t_is(got, ppce['xrows'], 12, t)

    t = 'val = e2i_data(ppc, val, {\'branch\', \'gen\', \'bus\'}, 1)'
    got = e2i_data(ppc, ppce['xcols'], ['branch', 'gen', 'bus'], 1)
    ex = r_[ppce['xbranch'][list(range(6)) + list(range(7, 10)), :4],
            ppce['xgen'][[3, 1, 0], :],
            ppce['xbus'][list(range(5)) + list(range(6, 10)), :4],
            -1 * ones((2, 4))].T
    t_is(got, ex, 12, t)
    t = 'val = i2e_data(ppc, val, oldval, {\'branch\', \'gen\', \'bus\'}, 1)'
    tmp1 = ones(ppce['xbranch'][:, :4].shape)
    tmp1[6, :4] = ppce['xbranch'][6, :4]
    tmp2 = ones(ppce['xgen'].shape)
    tmp2[2, :] = ppce['xgen'][2, :]
    tmp3 = ones(ppce['xbus'][:, :4].shape)
    tmp3[5, :4] = ppce['xbus'][5, :4]
    tmp = r_[tmp1, tmp2, tmp3].T
    got = i2e_data(ppc, ex, tmp, ['branch', 'gen', 'bus'], 1)
    t_is(got, ppce['xcols'], 12, t)

    ##-----  ppc = e2i_field/i2e_field(ppc, field, ...)  -----
    t = 'ppc = e2i_field(ppc, field, \'bus\')'
    ppc = e2i_field(ppce)
    ex = ppce['xbus']
    ex = delete(ex, 5, 0)
    got = e2i_field(ppc, 'xbus', 'bus')
    t_is(got['xbus'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, field, \'bus\')'
    got = i2e_field(got, 'xbus', ordering='bus')
    t_is(got['xbus'], ppce['xbus'], 12, t)

    t = 'ppc = e2i_field(ppc, field, \'bus\', 1)'
    ex = ppce['xbus']
    ex = delete(ex, 5, 1)
    got = e2i_field(ppc, 'xbus', 'bus', 1)
    t_is(got['xbus'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, field, \'bus\', 1)'
    got = i2e_field(got, 'xbus', ordering='bus', dim=1)
    t_is(got['xbus'], ppce['xbus'], 12, t)

    t = 'ppc = e2i_field(ppc, field, \'gen\')'
    ex = ppce['xgen'][[3, 1, 0], :]
    got = e2i_field(ppc, 'xgen', 'gen')
    t_is(got['xgen'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, field, \'gen\')'
    got = i2e_field(got, 'xgen', ordering='gen')
    t_is(got['xgen'], ppce['xgen'], 12, t)

    t = 'ppc = e2i_field(ppc, field, \'gen\', 1)'
    ex = ppce['xgen'][:, [3, 1, 0]]
    got = e2i_field(ppc, 'xgen', 'gen', 1)
    t_is(got['xgen'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, field, \'gen\', 1)'
    got = i2e_field(got, 'xgen', ordering='gen', dim=1)
    t_is(got['xgen'], ppce['xgen'], 12, t)

    t = 'ppc = e2i_field(ppc, field, \'branch\')'
    ex = ppce['xbranch']
    ex = delete(ex, 6, 0)
    got = e2i_field(ppc, 'xbranch', 'branch')
    t_is(got['xbranch'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, field, \'branch\')'
    got = i2e_field(got, 'xbranch', ordering='branch')
    t_is(got['xbranch'], ppce['xbranch'], 12, t)

    t = 'ppc = e2i_field(ppc, field, \'branch\', 1)'
    ex = ppce['xbranch']
    ex = delete(ex, 6, 1)
    got = e2i_field(ppc, 'xbranch', 'branch', 1)
    t_is(got['xbranch'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, field, \'branch\', 1)'
    got = i2e_field(got, 'xbranch', ordering='branch', dim=1)
    t_is(got['xbranch'], ppce['xbranch'], 12, t)

    t = 'ppc = e2i_field(ppc, field, {\'branch\', \'gen\', \'bus\'})'
    ex = r_[ppce['xbranch'][list(range(6)) + list(range(7, 10)), :4],
            ppce['xgen'][[3, 1, 0], :],
            ppce['xbus'][list(range(5)) + list(range(6, 10)), :4],
            -1 * ones((2, 4))]
    got = e2i_field(ppc, 'xrows', ['branch', 'gen', 'bus'])
    t_is(got['xrows'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, field, {\'branch\', \'gen\', \'bus\'})'
    got = i2e_field(got, 'xrows', ordering=['branch', 'gen', 'bus'])
    t_is(got['xrows'], ppce['xrows'], 12, t)

    t = 'ppc = e2i_field(ppc, field, {\'branch\', \'gen\', \'bus\'}, 1)'
    ex = r_[ppce['xbranch'][list(range(6)) + list(range(7, 10)), :4],
            ppce['xgen'][[3, 1, 0], :],
            ppce['xbus'][list(range(5)) + list(range(6, 10)), :4],
            -1 * ones((2, 4))].T
    got = e2i_field(ppc, 'xcols', ['branch', 'gen', 'bus'], 1)
    t_is(got['xcols'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, field, {\'branch\', \'gen\', \'bus\'})'
    got = i2e_field(got, 'xcols', ordering=['branch', 'gen', 'bus'], dim=1)
    t_is(got['xcols'], ppce['xcols'], 12, t)

    t = 'ppc = e2i_field(ppc, {\'field1\', \'field2\'}, ordering)'
    ex = ppce['x']['more'][[3, 1, 0], :]
    got = e2i_field(ppc, ['x', 'more'], 'gen')
    t_is(got['x']['more'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, {\'field1\', \'field2\'}, ordering)'
    got = i2e_field(got, ['x', 'more'], ordering='gen')
    t_is(got['x']['more'], ppce['x']['more'], 12, t)

    t = 'ppc = e2i_field(ppc, {\'field1\', \'field2\'}, ordering, 1)'
    ex = ppce['x']['more'][:, [3, 1, 0]]
    got = e2i_field(ppc, ['x', 'more'], 'gen', 1)
    t_is(got['x']['more'], ex, 12, t)
    t = 'ppc = i2e_field(ppc, {\'field1\', \'field2\'}, ordering, 1)'
    got = i2e_field(got, ['x', 'more'], ordering='gen', dim=1)
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
    eVmQgcols = list(range(10, 20)) + list(range(24, 28))
    iVmQgcols = list(range(9, 18)) + list(range(21, 24))
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
