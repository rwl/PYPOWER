# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Global test counters initialization.
"""

from time import time

from pypower.t.t_globals import TestGlobals


def t_begin(num_of_tests, quiet=False):
    """Initializes the global test counters, setting everything up to
    execute C{num_of_tests} tests using C{t_ok} and C{t_is}. If C{quiet}
    is true, it will not print anything for the individual tests, only a
    summary when C{t_end} is called.

    @author: Ray Zimmerman (PSERC Cornell)
    """

    TestGlobals.t_quiet = quiet
    TestGlobals.t_num_of_tests = num_of_tests
    TestGlobals.t_counter = 1
    TestGlobals.t_ok_cnt = 0
    TestGlobals.t_not_ok_cnt = 0
    TestGlobals.t_skip_cnt = 0
    TestGlobals.t_clock = time()

    if not TestGlobals.t_quiet:
        print('1..%d' % num_of_tests)
