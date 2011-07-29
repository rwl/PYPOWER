# Copyright (C) 2004-2011 Power System Engineering Research Center
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
        print s

    TestGlobals.t_counter += 1
