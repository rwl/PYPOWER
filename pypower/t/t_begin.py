# Copyright (C) 2004-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

from time import time

t_quiet = False
t_num_of_tests = 0
t_counter = 0
t_ok_cnt = 0
t_not_ok_cnt = 0
t_skip_cnt = 0
t_clock = 0.0

def t_begin(num_of_tests, quiet=False):
    """Initializes the global test counters, setting everything up to
    execute C{num_of_tests} tests using C{t_ok} and C{t_is}. If C{quiet}
    is true, it will not print anything for the individual tests, only a
    summary when C{t_end} is called.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    global t_quiet, t_num_of_tests, t_counter, t_ok_cnt, t_not_ok_cnt, t_skip_cnt, t_clock

    t_quiet = quiet
    t_num_of_tests = num_of_tests
    t_counter = 1
    t_ok_cnt = 0
    t_not_ok_cnt = 0
    t_skip_cnt = 0
    t_clock = time()

    if not t_quiet:
        print '1..%d\n' % num_of_tests
