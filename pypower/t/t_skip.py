# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

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
    """
    msg = ' : ' + msg

    TestGlobals.t_skip_cnt = TestGlobals.t_skip_cnt + cnt
    if not TestGlobals.t_quiet:
        print('skipped tests %d..%d%s' % (TestGlobals.t_counter,
                                            TestGlobals.t_counter + cnt - 1,
                                            msg))

    TestGlobals.t_counter = TestGlobals.t_counter + cnt
