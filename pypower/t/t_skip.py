# Copyright (C) 2004-2011 Power System Engineering Research Center (PSERC)
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

"""Skips a number of tests.
"""

from pypower.t.t_globals import TestGlobals


def t_skip(cnt, msg=''):
    """Skips a number of tests.

    Increments the global test count and skipped tests count. Prints
    'skipped tests x..y : ' followed by the C{msg}, unless the
    global variable t_quiet is true. Intended to be called between calls to
    C{t_begin} and C{t_end}.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    msg = ' : ' + msg

    TestGlobals.t_skip_cnt = TestGlobals.t_skip_cnt + cnt
    if not TestGlobals.t_quiet:
        print('skipped tests %d..%d%s' % (TestGlobals.t_counter,
                                            TestGlobals.t_counter + cnt - 1,
                                            msg))

    TestGlobals.t_counter = TestGlobals.t_counter + cnt
