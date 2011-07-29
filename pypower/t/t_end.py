# Copyright (C) 2004-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

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
