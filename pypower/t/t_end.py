# Copyright (C) 2004-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
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

def t_end():
    """Finish running tests and print statistics.

    Checks the global counters that were updated by calls to C{t_ok}
    and C{t_is} and prints out a summary of the test results.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    global t_quiet
    global t_num_of_tests
    global t_counter
    global t_ok_cnt
    global t_not_ok_cnt
    global t_skip_cnt
    global t_clock

    t_counter = t_counter - 1

    if (t_counter == t_num_of_tests) and (t_counter == t_ok_cnt + t_skip_cnt) and (t_not_ok_cnt == 0):
        all_ok = True
    else:
        all_ok = False

    s = ''
    if t_quiet:
        if all_ok:
            s += 'ok'
            if t_skip_cnt:
                s += ' (%d of %d skipped)' % (t_skip_cnt, t_num_of_tests)
        else:
            s += 'not ok\n'
            s += '\t#####  Ran %d of %d tests: %d passed, %d failed' % (t_counter, t_num_of_tests, t_ok_cnt, t_not_ok_cnt)
            if t_skip_cnt:
                s += ', %d skipped' % t_skip_cnt
        s += '\n'
    else:
        if all_ok:
            if t_skip_cnt:
                s += 'All tests successful (%d passed, %d skipped of %d)' % (t_ok_cnt, t_skip_cnt, t_num_of_tests)
            else:
                s += 'All tests successful (%d of %d)' % (t_ok_cnt, t_num_of_tests)
        else:
            s += 'Ran %d of %d tests: %d passed, %d failed' % (t_counter, t_num_of_tests, t_ok_cnt, t_not_ok_cnt)
            if t_skip_cnt:
                s += ', %d skipped' % t_skip_cnt
        s += '\nElapsed time %.2f seconds.\n' % (time() - t_clock)

    print s
