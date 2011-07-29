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

"""Run all PYPOWER tests.
"""

from pypower.t.t_run_tests import t_run_tests


def test_pypower(verbose=False):
    """Run all PYPOWER tests.

    Prints the details of the individual tests if verbose is true.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    tests = []

    ## PYPOWER base test
    tests.append('t_loadcase')
    tests.append('t_jacobian')
    tests.append('t_hasPQcap')
    tests.append('t_pf')
    tests.append('t_opf_dc')
    tests.append('t_opf_ipopt')
    tests.append('t_makePTDF')

#    ## smartmarket tests
#    tests.append('t_off2case')
#    tests.append('t_auction_mips')
#    tests.append('t_runmarket')

    t_run_tests(tests, verbose)


def test_pf(verbose=False):
    tests = []

    tests.append('t_loadcase')
    tests.append('t_jacobian')
    tests.append('t_pf')

    return t_run_tests(tests, verbose)


def test_opf(verbose=False, *others):
    tests = []

    tests.append('t_loadcase')
    tests.append('t_hasPQcap')

    tests.append('t_opf_dc')

    tests.append('t_opf_pdipm')

    tests.append('t_makePTDF')

    tests.extend(others)

    return t_run_tests(tests, verbose)


if __name__ == '__main__':
    test_pypower(verbose=True)
