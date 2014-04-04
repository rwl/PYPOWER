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
    @author: Richard Lincoln
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
