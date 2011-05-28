# Copyright (C) 2004-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
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

from time import time

from numpy import zeros

def t_run_tests(test_names, verbose=False):
    """Run a series of tests.

    Runs a set of tests whose names
    are given in the list C{test_names}. If the optional parameter
    C{verbose} is true, it prints the details of the individual tests.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    global t_num_of_tests
    global t_counter
    global t_ok_cnt
    global t_not_ok_cnt
    global t_skip_cnt

    ## figure out padding for printing
    if not verbose:
        len = zeros(len(test_names))
        for k in range(len(test_names)):
            len[k] = len(test_names[k])
        maxlen = max(len)

    ## initialize statistics
    num_of_tests = 0
    counter = 0
    ok_cnt = 0
    not_ok_cnt = 0
    skip_cnt = 0

    t0 = time()
    s = ''
    for k in range(len(test_names)):
        if verbose:
            s += '\n----------  %s  ----------\n' % test_names[k]
        else:
            pad = maxlen + 4 - len(test_names[k])
            s += '%s' % test_names[k]
            for m in range(pad): s += '.'

        eval( test_names[k], not verbose )

        num_of_tests    = num_of_tests  + t_num_of_tests
        counter         = counter       + t_counter
        ok_cnt          = ok_cnt        + t_ok_cnt
        not_ok_cnt      = not_ok_cnt    + t_not_ok_cnt
        skip_cnt        = skip_cnt      + t_skip_cnt

    if verbose:
        s += '\n\n----------  Summary  ----------\n'

    if (counter == num_of_tests) and (counter == ok_cnt + skip_cnt) and (not_ok_cnt == 0):
        if skip_cnt:
            s += 'All tests successful (%d passed, %d skipped of %d)' % \
                (ok_cnt, skip_cnt, num_of_tests)
        else:
            s += 'All tests successful (%d of %d)' % ok_cnt, num_of_tests
    else:
        s += 'Ran %d of %d tests: %d passed, %d failed' % \
            (counter, num_of_tests, ok_cnt, not_ok_cnt)
        if skip_cnt:
            s += ', %d skipped' % skip_cnt

    s += '\nElapsed time %.2f seconds.\n' % (time() - t0)
    print s
