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
        print '1..%d' % num_of_tests
