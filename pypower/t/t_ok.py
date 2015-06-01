# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

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
