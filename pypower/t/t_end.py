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
    @author: Richard Lincoln
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
