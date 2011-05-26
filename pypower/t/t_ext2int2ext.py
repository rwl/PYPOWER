# Copyright (C) 2004-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
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

from numpy import ones

from pypower.loadcase import loadcase
from pypower.ext2int import ext2int
from pypower.int2ext import int2ext

from pypower.t.t_end import t_end
from pypower.t.t_is import t_is

def t_ext2int2ext(quiet=False):
    """Tests C{ext2int} and C{int2ext}.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    t_begin(85, quiet)

    verbose = not quiet

    ##-----  ppc = ext2int/int2ext(ppc)  -----
    t = 'ppc = ext2int(ppc) : '
    ppce = loadcase('t_case_ext')
    ppci = loadcase('t_case_int')
    ppc = ext2int(ppce)
    t_is(ppc.bus, ppci.bus, 12, [t, 'bus'])
    t_is(ppc.branch, ppci.branch, 12, [t, 'branch'])
    t_is(ppc.gen, ppci.gen, 12, [t, 'gen'])
    t_is(ppc.gencost, ppci.gencost, 12, [t, 'gencost'])
    t_is(ppc.areas, ppci.areas, 12, [t, 'areas'])
    t_is(ppc.A, ppci.A, 12, [t, 'A'])
    t_is(ppc.N, ppci.N, 12, [t, 'N'])
    t = 'ppc = ext2int(ppc) - repeat : '
    ppc = ext2int(ppc)
    t_is(ppc.bus, ppci.bus, 12, [t, 'bus'])
    t_is(ppc.branch, ppci.branch, 12, [t, 'branch'])
    t_is(ppc.gen, ppci.gen, 12, [t, 'gen'])
    t_is(ppc.gencost, ppci.gencost, 12, [t, 'gencost'])
    t_is(ppc.areas, ppci.areas, 12, [t, 'areas'])
    t_is(ppc.A, ppci.A, 12, [t, 'A'])
    t_is(ppc.N, ppci.N, 12, [t, 'N'])
    t = 'ppc = int2ext(ppc) : '
    ppc = int2ext(ppc)
    t_is(ppc.bus, ppce.bus, 12, [t, 'bus'])
    t_is(ppc.branch, ppce.branch, 12, [t, 'branch'])
    t_is(ppc.gen, ppce.gen, 12, [t, 'gen'])
    t_is(ppc.gencost, ppce.gencost, 12, [t, 'gencost'])
    t_is(ppc.areas, ppce.areas, 12, [t, 'areas'])
    t_is(ppc.A, ppce.A, 12, [t, 'A'])
    t_is(ppc.N, ppce.N, 12, [t, 'N'])

    ##-----  val = ext2int/int2ext(ppc, val, ...)  -----
    t = 'val = ext2int(ppc, val, \'bus\')'
    ppc = ext2int(ppce)
    got = ext2int(ppc, ppce.xbus, 'bus')
    ex = ppce.xbus
    ex[5, :] = []
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'bus\')'
    tmp = ones(ppce.xbus.shape)
    tmp[5, :] = ppce.xbus[5, :]
    got = int2ext(ppc, ex, tmp, 'bus')
    t_is(got, ppce.xbus, 12, t)

    t = 'val = ext2int(ppc, val, \'bus\', 2)'
    got = ext2int(ppc, ppce.xbus, 'bus', 2)
    ex = ppce.xbus
    ex[:, 5] = []
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'bus\', 2)'
    tmp = ones(ppce.xbus.shape)
    tmp[:, 5] = ppce.xbus[:, 5]
    got = int2ext(ppc, ex, tmp, 'bus', 2)
    t_is(got, ppce.xbus, 12, t)

    t = 'val = ext2int(ppc, val, \'gen\')'
    got = ext2int(ppc, ppce.xgen, 'gen')
    ex = ppce.xgen[[3, 1, 0], :]
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'gen\')'
    tmp = ones(ppce.xgen.shape)
    tmp[2, :] = ppce.xgen[2, :]
    got = int2ext(ppc, ex, tmp, 'gen')
    t_is(got, ppce.xgen, 12, t)

    t = 'val = ext2int(ppc, val, \'gen\', 2)'
    got = ext2int(ppc, ppce.xgen, 'gen', 2)
    ex = ppce.xgen[:, [3, 1, 0]]
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'gen\', 2)'
    tmp = ones(ppce.xgen.shape)
    tmp[:, 2] = ppce.xgen[:, 2]
    got = int2ext(ppc, ex, tmp, 'gen', 2)
    t_is(got, ppce.xgen, 12, t)

    t = 'val = ext2int(ppc, val, \'branch\')'
    got = ext2int(ppc, ppce.xbranch, 'branch')
    ex = ppce.xbranch
    ex[6, :] = []
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'branch\')'
    tmp = ones(ppce.xbranch)
    tmp[6, :] = ppce.xbranch[6, :]
    got = int2ext(ppc, ex, tmp, 'branch')
    t_is(got, ppce.xbranch, 12, t)

    t = 'val = ext2int(ppc, val, \'branch\', 2)'
    got = ext2int(ppc, ppce.xbranch, 'branch', 2)
    ex = ppce.xbranch
    ex[:, 6] = []
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, \'branch\', 2)'
    tmp = ones(ppce.xbranch)
    tmp[:, 6] = ppce.xbranch[:, 6]
    got = int2ext(ppc, ex, tmp, 'branch', 2)
    t_is(got, ppce.xbranch, 12, t)

    t = 'val = ext2int(ppc, val, {\'branch\', \'gen\', \'bus\'})'
    got = ext2int(ppc, ppce.xrows, ['branch', 'gen', 'bus'])
    ex = [ppce.xbranch[[range(6) + range(7, 10)], 0:4], ppce.xgen[[3, 1, 0], :], ppce.xbus[[range(5) + range(6, 10)], 0:4], -ones((2, 4))]
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, {\'branch\', \'gen\', \'bus\'})'
    tmp1 = ones(ppce.xbranch[:, 0:4].shape)
    tmp1[6, 0:4] = ppce.xbranch[6, 0:4]
    tmp2 = ones(ppce.xgen.shape)
    tmp2[2, :] = ppce.xgen[2, :]
    tmp3 = ones(ppce.xbus[:, 0:4].shape)
    tmp3[5, 0:4] = ppce.xbus[5, 0:4]
    tmp = r_[tmp1, tmp2, tmp3]
    got = int2ext(ppc, ex, tmp, ['branch', 'gen', 'bus'])
    t_is(got, ppce.xrows, 12, t)

    t = 'val = ext2int(ppc, val, {\'branch\', \'gen\', \'bus\'}, 2)'
    got = ext2int(ppc, ppce.xcols, ['branch', 'gen', 'bus'], 2)
    ex = r_[ppce.xbranch[range(6) + range(7, 10), 0:4], ppce.xgen[[3, 1, 0], :], ppce.xbus[range(5) + range(6, 10), 0:4], -ones((2, 4))]
    t_is(got, ex, 12, t)
    t = 'val = int2ext(ppc, val, oldval, {\'branch\', \'gen\', \'bus\'}, 2)'
    tmp1 = ones(ppce.xbranch[:, 0:4].shape)
    tmp1[6, range(4)] = ppce.xbranch[6, range(4)]
    tmp2 = ones(ppce.xgen.shape)
    tmp2[2, :] = ppce.xgen[2, :]
    tmp3 = ones(ppce.xbus[:, 0:4].shape)
    tmp3[5, 0:4] = ppce.xbus[5, 0:4]
    tmp = r_[tmp1, tmp2, tmp3]
    got = int2ext(ppc, ex, tmp, ['branch', 'gen', 'bus'], 2)
    t_is(got, ppce.xcols, 12, t)

    ##-----  ppc = ext2int/int2ext(ppc, field, ...)  -----
    t = 'ppc = ext2int(ppc, field, \'bus\')'
    ppc = ext2int(ppce)
    ex = ppce.xbus
    ex[5, :] = []
    got = ext2int(ppc, 'xbus', 'bus')
    t_is(got.xbus, ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'bus\')'
    got = int2ext(got, 'xbus', 'bus')
    t_is(got.xbus, ppce.xbus, 12, t)

    t = 'ppc = ext2int(ppc, field, \'bus\', 2)'
    ex = ppce.xbus
    ex[:, 5] = []
    got = ext2int(ppc, 'xbus', 'bus', 2)
    t_is(got.xbus, ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'bus\', 2)'
    got = int2ext(got, 'xbus', 'bus', 2)
    t_is(got.xbus, ppce.xbus, 12, t)

    t = 'ppc = ext2int(ppc, field, \'gen\')'
    ex = ppce.xgen[[3, 1, 0], :]
    got = ext2int(ppc, 'xgen', 'gen')
    t_is(got.xgen, ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'gen\')'
    got = int2ext(got, 'xgen', 'gen')
    t_is(got.xgen, ppce.xgen, 12, t)

    t = 'ppc = ext2int(ppc, field, \'gen\', 2)'
    ex = ppce.xgen[:, [3, 1, 0]]
    got = ext2int(ppc, 'xgen', 'gen', 2)
    t_is(got.xgen, ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'gen\', 2)'
    got = int2ext(got, 'xgen', 'gen', 2)
    t_is(got.xgen, ppce.xgen, 12, t)

    t = 'ppc = ext2int(ppc, field, \'branch\')'
    ex = ppce.xbranch
    ex[6, :] = []
    got = ext2int(ppc, 'xbranch', 'branch')
    t_is(got.xbranch, ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'branch\')'
    got = int2ext(got, 'xbranch', 'branch')
    t_is(got.xbranch, ppce.xbranch, 12, t)

    t = 'ppc = ext2int(ppc, field, \'branch\', 2)'
    ex = ppce.xbranch
    ex[:, 6] = []
    got = ext2int(ppc, 'xbranch', 'branch', 2)
    t_is(got.xbranch, ex, 12, t)
    t = 'ppc = int2ext(ppc, field, \'branch\', 2)'
    got = int2ext(got, 'xbranch', 'branch', 2)
    t_is(got.xbranch, ppce.xbranch, 12, t)

    t = 'ppc = ext2int(ppc, field, {\'branch\', \'gen\', \'bus\'})'
    ex = r_[ppce.xbranch[range(6) + range(7, 10), 0:4], ppce.xgen[[3, 1, 0], :], ppce.xbus[range(5) + range(6, 10), 0:4], -ones(2, 4)]
    got = ext2int(ppc, 'xrows', ['branch', 'gen', 'bus'])
    t_is(got.xrows, ex, 12, t)
    t = 'ppc = int2ext(ppc, field, {\'branch\', \'gen\', \'bus\'})'
    got = int2ext(got, 'xrows', ['branch', 'gen', 'bus'])
    t_is(got.xrows, ppce.xrows, 12, t)

    t = 'ppc = ext2int(ppc, field, {\'branch\', \'gen\', \'bus\'}, 2)'
    ex = r_[ppce.xbranch[range(6) + range(7, 10), 0:4], ppce.xgen[[3, 1, 0], :], ppce.xbus[range(5) + range(6, 10), 0:4], -ones(2, 4)]
    got = ext2int(ppc, 'xcols', ['branch', 'gen', 'bus'], 2)
    t_is(got.xcols, ex, 12, t)
    t = 'ppc = int2ext(ppc, field, {\'branch\', \'gen\', \'bus\'})'
    got = int2ext(got, 'xcols', ['branch', 'gen', 'bus'], 2)
    t_is(got.xcols, ppce.xcols, 12, t)

    t = 'ppc = ext2int(ppc, {\'field1\', \'field2\'}, ordering)'
    ex = ppce.x.more[[3, 1, 0], :]
    got = ext2int(ppc, ['x', 'more'], 'gen')
    t_is(got.x.more, ex, 12, t)
    t = 'ppc = int2ext(ppc, {\'field1\', \'field2\'}, ordering)'
    got = int2ext(got, ['x', 'more'], 'gen')
    t_is(got.x.more, ppce.x.more, 12, t)

    t = 'ppc = ext2int(ppc, {\'field1\', \'field2\'}, ordering, 2)'
    ex = ppce.x.more[:, [3, 1, 0]]
    got = ext2int(ppc, ['x', 'more'], 'gen', 2)
    t_is(got.x.more, ex, 12, t)
    t = 'ppc = int2ext(ppc, {\'field1\', \'field2\'}, ordering, 2)'
    got = int2ext(got, ['x', 'more'], 'gen', 2)
    t_is(got.x.more, ppce.x.more, 12, t)

    ##-----  more ppc = ext2int/int2ext(ppc)  -----
    t = 'ppc = ext2int(ppc) - bus/gen/branch only : '
    ppce = loadcase('t_case_ext')
    ppci = loadcase('t_case_int')
    del ppce.gencost
    del ppce.areas
    del ppce.A
    del ppce.N
    del ppci.gencost
    del ppci.areas
    del ppci.A
    del ppci.N
    ppc = ext2int(ppce)
    t_is(ppc.bus, ppci.bus, 12, [t, 'bus'])
    t_is(ppc.branch, ppci.branch, 12, [t, 'branch'])
    t_is(ppc.gen, ppci.gen, 12, [t, 'gen'])

    t = 'ppc = ext2int(ppc) - no areas/A : '
    ppce = loadcase('t_case_ext')
    ppci = loadcase('t_case_int')
    del ppce.areas
    del ppce.A
    del ppci.areas
    del ppci.A
    ppc = ext2int(ppce)
    t_is(ppc.bus, ppci.bus, 12, [t, 'bus'])
    t_is(ppc.branch, ppci.branch, 12, [t, 'branch'])
    t_is(ppc.gen, ppci.gen, 12, [t, 'gen'])
    t_is(ppc.gencost, ppci.gencost, 12, [t, 'gencost'])
    t_is(ppc.N, ppci.N, 12, [t, 'N'])

    t = 'ppc = ext2int(ppc) - Qg cost, no N : '
    ppce = loadcase('t_case_ext')
    ppci = loadcase('t_case_int')
    del ppce.N
    del ppci.N
    ppce.gencost = c_[ppce.gencost, ppce.gencost]
    ppci.gencost = c_[ppci.gencost, ppci.gencost]
    ppc = ext2int(ppce)
    t_is(ppc.bus, ppci.bus, 12, [t, 'bus'])
    t_is(ppc.branch, ppci.branch, 12, [t, 'branch'])
    t_is(ppc.gen, ppci.gen, 12, [t, 'gen'])
    t_is(ppc.gencost, ppci.gencost, 12, [t, 'gencost'])
    t_is(ppc.areas, ppci.areas, 12, [t, 'areas'])
    t_is(ppc.A, ppci.A, 12, [t, 'A'])

    t = 'ppc = ext2int(ppc) - A, N are DC sized : '
    ppce = loadcase('t_case_ext')
    ppci = loadcase('t_case_int')
    eVmQgcols = range(10, 20) + range(24, 28)
    iVmQgcols = range(9, 18) + range(21, 24)
    ppce.A[:, eVmQgcols] = []
    ppce.N[:, eVmQgcols] = []
    ppci.A[:, iVmQgcols] = []
    ppci.N[:, iVmQgcols] = []
    ppc = ext2int(ppce)
    t_is(ppc.bus, ppci.bus, 12, [t, 'bus'])
    t_is(ppc.branch, ppci.branch, 12, [t, 'branch'])
    t_is(ppc.gen, ppci.gen, 12, [t, 'gen'])
    t_is(ppc.gencost, ppci.gencost, 12, [t, 'gencost'])
    t_is(ppc.areas, ppci.areas, 12, [t, 'areas'])
    t_is(ppc.A, ppci.A, 12, [t, 'A'])
    t_is(ppc.N, ppci.N, 12, [t, 'N'])
    t = 'ppc = int2ext(ppc) - A, N are DC sized : '
    ppc = int2ext(ppc)
    t_is(ppc.bus, ppce.bus, 12, [t, 'bus'])
    t_is(ppc.branch, ppce.branch, 12, [t, 'branch'])
    t_is(ppc.gen, ppce.gen, 12, [t, 'gen'])
    t_is(ppc.gencost, ppce.gencost, 12, [t, 'gencost'])
    t_is(ppc.areas, ppce.areas, 12, [t, 'areas'])
    t_is(ppc.A, ppce.A, 12, [t, 'A'])
    t_is(ppc.N, ppce.N, 12, [t, 'N'])

    t_end
