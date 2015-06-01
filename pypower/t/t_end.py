# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Finish running tests and print statistics.
"""

import sys

from time import time

from pypower.t.t_globals import TestGlobals


def t_end():
    """Finish running tests and print statistics.

    Checks the global counters that were updated by calls to C{t_ok}
    and C{t_is} and prints out a summary of the test results.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    TestGlobals.t_counter -= 1

    if (TestGlobals.t_counter == TestGlobals.t_num_of_tests) and \
        (TestGlobals.t_counter == TestGlobals.t_ok_cnt + TestGlobals.t_skip_cnt) and \
        (TestGlobals.t_not_ok_cnt == 0):
        all_ok = True
    else:
        all_ok = False

    s = ''
    if TestGlobals.t_quiet:
        if all_ok:
            s += 'ok'
            if TestGlobals.t_skip_cnt:
                s += ' (%d of %d skipped)' % \
                    (TestGlobals.t_skip_cnt, TestGlobals.t_num_of_tests)
        else:
            s += 'not ok\n'
            s += '\t#####  Ran %d of %d tests: %d passed, %d failed' % \
                (TestGlobals.t_counter, TestGlobals.t_num_of_tests,
                 TestGlobals.t_ok_cnt, TestGlobals.t_not_ok_cnt)
            if TestGlobals.t_skip_cnt:
                s += ', %d skipped' % TestGlobals.t_skip_cnt
        s += '\n'
    else:
        if all_ok:
            if TestGlobals.t_skip_cnt:
                s += 'All tests successful (%d passed, %d skipped of %d)' % \
                    (TestGlobals.t_ok_cnt, TestGlobals.t_skip_cnt,
                     TestGlobals.t_num_of_tests)
            else:
                s += 'All tests successful (%d of %d)' % \
                    (TestGlobals.t_ok_cnt, TestGlobals.t_num_of_tests)
        else:
            s += 'Ran %d of %d tests: %d passed, %d failed' % \
                (TestGlobals.t_counter, TestGlobals.t_num_of_tests,
                 TestGlobals.t_ok_cnt, TestGlobals.t_not_ok_cnt)
            if TestGlobals.t_skip_cnt:
                s += ', %d skipped' % TestGlobals.t_skip_cnt
        s += '\nElapsed time %.2f seconds.\n' % (time() - TestGlobals.t_clock)

    sys.stdout.write(s)
