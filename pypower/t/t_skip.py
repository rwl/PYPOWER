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

"""Skips a number of tests.
"""

from pypower.t.t_globals import TestGlobals


def t_skip(cnt, msg=''):
    """Skips a number of tests.

    Increments the global test count and skipped tests count. Prints
    'skipped tests x..y : ' followed by the C{msg}, unless the
    global variable t_quiet is true. Intended to be called between calls to
    C{t_begin} and C{t_end}.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    msg = ' : ' + msg

    TestGlobals.t_skip_cnt = TestGlobals.t_skip_cnt + cnt
    if not TestGlobals.t_quiet:
        print 'skipped tests %d..%d%s' % (TestGlobals.t_counter,
                                            TestGlobals.t_counter + cnt - 1,
                                            msg)

    TestGlobals.t_counter = TestGlobals.t_counter + cnt
