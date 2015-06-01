# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Global test counters.
"""

class TestGlobals(object):
    t_quiet = False
    t_num_of_tests = 0
    t_counter = 0
    t_ok_cnt = 0
    t_not_ok_cnt = 0
    t_skip_cnt = 0
    t_clock = 0.0
