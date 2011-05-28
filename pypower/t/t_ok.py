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

def t_ok(cond, msg=''):
    """Tests if a condition is true.

    Increments the global test count and if the C{expr}
    is true it increments the passed tests count, otherwise increments
    the failed tests count. Prints 'ok' or 'not ok' followed by the
    C{msg}, unless the global variable t_quiet is true. Intended to be
    called between calls to C{t_begin} and C{t_end}.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    global t_quiet
    global t_counter
    global t_ok_cnt
    global t_not_ok_cnt

    if msg:
        msg = ' - ' + msg

    s = ''
    if cond:
        t_ok_cnt = t_ok_cnt + 1
    else:
        t_not_ok_cnt = t_not_ok_cnt + 1
        if not t_quiet:
            s += 'not '

    if not t_quiet:
        s += 'ok %d%s\n' % (t_counter, msg)
        print s

    t_counter = t_counter + 1
