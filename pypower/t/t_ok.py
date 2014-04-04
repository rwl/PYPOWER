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

"""Tests if a condition is true.
"""

from pypower.t.t_globals import TestGlobals


def t_ok(cond, msg=''):
    """Tests if a condition is true.

    Increments the global test count and if the C{expr}
    is true it increments the passed tests count, otherwise increments
    the failed tests count. Prints 'ok' or 'not ok' followed by the
    C{msg}, unless the global variable t_quiet is true. Intended to be
    called between calls to C{t_begin} and C{t_end}.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    if msg:
        if isinstance(msg, list):
            msg = "".join(msg)
        msg = ' - ' + msg

    s = ''
    if cond:
        TestGlobals.t_ok_cnt += 1
    else:
        TestGlobals.t_not_ok_cnt += 1
        if not TestGlobals.t_quiet:
            s += 'not '

    if not TestGlobals.t_quiet:
        s += 'ok %3d%s' % (TestGlobals.t_counter, msg)
        print(s)

    TestGlobals.t_counter += 1
