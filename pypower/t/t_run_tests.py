# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Run a series of tests.
"""

import sys

from time import time

from numpy import zeros

from pypower.t.t_globals import TestGlobals


def t_run_tests(test_names, verbose=False):
    """Run a series of tests.

    Runs a set of tests whose names
    are given in the list C{test_names}. If the optional parameter
    C{verbose} is true, it prints the details of the individual tests.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    ## figure out padding for printing
    if not verbose:
        length = zeros(len(test_names), int)
        for k in range(len(test_names)):
            length[k] = len(test_names[k])
        maxlen = max(length)

    ## initialize statistics
    num_of_tests = 0
    counter = 0
    ok_cnt = 0
    not_ok_cnt = 0
    skip_cnt = 0

    t0 = time()
    for k in range(len(test_names)):
        if verbose:
            sys.stdout.write('\n----------  %s  ----------\n' % test_names[k])
        else:
            pad = maxlen + 4 - len(test_names[k])
            s = '%s' % test_names[k]
            for _ in range(pad): s += '.'
            sys.stdout.write(s)


        tname = test_names[k]
        __import__('pypower.t.'+tname)
        mod = sys.modules['pypower.t.'+tname]  #@PydevCodeAnalysisIgnore
        eval('mod.%s(not verbose)' % tname)

        num_of_tests    = num_of_tests  + TestGlobals.t_num_of_tests
        counter         = counter       + TestGlobals.t_counter
        ok_cnt          = ok_cnt        + TestGlobals.t_ok_cnt
        not_ok_cnt      = not_ok_cnt    + TestGlobals.t_not_ok_cnt
        skip_cnt        = skip_cnt      + TestGlobals.t_skip_cnt

    s = ''
    status = 0
    if verbose:
        s += '\n\n----------  Summary  ----------\n'

    if (counter == num_of_tests) and (counter == ok_cnt + skip_cnt) and (not_ok_cnt == 0):
        if skip_cnt:
            s += 'All tests successful (%d passed, %d skipped of %d)' % \
                (ok_cnt, skip_cnt, num_of_tests)
            status = 0
        else:
            s += 'All tests successful (%d of %d)' % (ok_cnt, num_of_tests)
            status = 0
    else:
        s += 'Ran %d of %d tests: %d passed, %d failed' % \
            (counter, num_of_tests, ok_cnt, not_ok_cnt)
        if skip_cnt:
            s += ', %d skipped' % skip_cnt
        status = 1

    s += '\nElapsed time %.2f seconds.\n' % (time() - t0)
    sys.stdout.write(s)

    return status
