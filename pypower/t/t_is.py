# Copyright (C) 2004-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

from numpy import max, abs, flatnonzero as find

from pypower.t.t_ok import t_ok

def t_is(got, expected, prec=5, msg=''):
    """Tests if two matrices are identical to some tolerance.

    Increments the global test count and if the maximum difference
    between corresponding elements of C{got} and C{expected} is less
    than 10**(-C{prec}) then it increments the passed tests count,
    otherwise increments the failed tests count. Prints 'ok' or 'not ok'
    followed by the MSG, unless the global variable t_quiet is true.
    Intended to be called between calls to C{t_begin} and C{t_end}.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    m, n = expected.shape
    if (got.shape == (m, n)) or ((m, n) == (0, 0)):
        got_minus_expected = got - expected
        max_diff = max(max(abs(got_minus_expected)))
        condition = ( max_diff < 10**(-prec) )
    else:
        condition = False
        max_diff = 0

    t_ok(condition, msg)
    if (not condition and not t_quiet):
        s = ''
        if max_diff != 0:
            i, j, v = find(abs(got_minus_expected) >= 10**(-prec)) # FIXME
            k = i + (j - 1) * m
            vv, kk = max(abs(got_minus_expected(k)))
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
            s += '             got: %d x %d\n' % got.shape
            s += '        expected: %d x %d\n\n' % expected.shape

        print s
