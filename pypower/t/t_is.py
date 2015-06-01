# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests if two matrices are identical to some tolerance.
"""

from numpy import array, max, abs, nonzero, argmax, zeros

from pypower.t.t_ok import t_ok
from pypower.t.t_globals import TestGlobals


def t_is(got, expected, prec=5, msg=''):
    """Tests if two matrices are identical to some tolerance.

    Increments the global test count and if the maximum difference
    between corresponding elements of C{got} and C{expected} is less
    than 10**(-C{prec}) then it increments the passed tests count,
    otherwise increments the failed tests count. Prints 'ok' or 'not ok'
    followed by the MSG, unless the global variable t_quiet is true.
    Intended to be called between calls to C{t_begin} and C{t_end}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    if isinstance(got, int) or isinstance(got, float):
        got = array([got], float)
    elif isinstance(got, list) or isinstance(got, tuple):
        got = array(got, float)

    if isinstance(expected, int) or isinstance(expected, float):
        expected = array([expected], float)
    elif isinstance(expected, list) or isinstance(expected, tuple):
        expected = array(expected, float)

    if (got.shape == expected.shape) or (expected.shape == (0,)):
        got_minus_expected = got - expected
        max_diff = max(max(abs(got_minus_expected)))
        condition = ( max_diff < 10**(-prec) )
    else:
        condition = False
        max_diff = 0

    t_ok(condition, msg)
    if (not condition and not TestGlobals.t_quiet):
        s = ''
        if max_diff != 0:
            idx = nonzero(not abs(got_minus_expected) < 10**(-prec))
            if len(idx) == 1:  # 1D array
                idx = (idx[0], zeros( len(got_minus_expected) ))
            i, j = idx

            k = i + (j-1) * expected.shape[0]

            got = got.flatten()
            expected = expected.flatten()
            got_minus_expected = got_minus_expected.flatten()

            kk = argmax( abs(got_minus_expected[ k.astype(int) ]) )

            s += '  row     col          got             expected          got - exp\n'
            s += '-------  ------  ----------------  ----------------  ----------------'
            for u in range(len(i)):
                s += '\n%6d  %6d  %16g  %16g  %16g' % \
                    (i[u], j[u], got[k[u]], expected[k[u]], got_minus_expected[k[u]])
                if u == kk:
                    s += '  *'
            s += '\nmax diff @ (%d,%d) = %g > allowed tol of %g\n\n' % \
                (i[kk], j[kk], max_diff, 10**(-prec))
        else:
            s += '    dimension mismatch:\n'

            if len(got.shape) == 1:  # 1D array
                s += '             got: %d\n' % got.shape
            else:
                s += '             got: %d x %d\n' % got.shape

            if len(expected.shape) == 1:  # 1D array
                s += '        expected: %d\n' % expected.shape
            else:
                s += '        expected: %d x %d\n' % expected.shape

        print(s)

if __name__ == '__main__':
    a = array([[1,2,3], [4,5,6]])
    b = array([[2,3,4], [5,6,7]])
    TestGlobals.t_quiet = False
    t_is(a, b)
