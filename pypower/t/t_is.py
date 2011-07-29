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

"""Tests if two matrices are identical to some tolerance.
"""

from sys import stdout

from numpy import array, max, abs

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
    @author: Richard Lincoln
    """
    if isinstance(got, int) or isinstance(got, float):
        got = array([[got]], float)
    elif isinstance(got, list) or isinstance(got, tuple):
        got = array(got, float)

    if isinstance(expected, int) or isinstance(expected, float):
        expected = array([[expected]], float)
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

        if max_diff != 0:
            print got
            print expected
            print got_minus_expected
            stdout.write('max diff = %g (allowed tol = %g)\n\n' % (max_diff, 10**(-prec)))
        else:
            stdout.write('    dimension mismatch:\n')
            stdout.write('             got: %d x %d\n' % got.shape)
            stdout.write('        expected: %d x %d\n\n' % expected.shape)
