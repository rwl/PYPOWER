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

"""Run all PYPOWER tests.
"""

from pypower.t.t_run_tests import t_run_tests


def test_pypower(verbose=False):
    """Run all PYPOWER tests.

    Prints the details of the individual tests if verbose is true.
    """
    tests = []

    ## PYPOWER base test
    tests.append('t_loadcase')
    tests.append('t_ext2int2ext')
    tests.append('t_jacobian')
    tests.append('t_hessian')
    tests.append('t_totcost')
    tests.append('t_modcost')
    tests.append('t_hasPQcap')

    tests.append('t_pips')

    tests.append('t_qps_pypower')
    tests.append('t_pf')

    tests.append('t_opf_pips')
    tests.append('t_opf_pips_sc')

#    try:
#        import pyipopt  #@UnusedImport
#        tests.append('t_opf_ipopt')
#        tests.append('t_opf_dc_ipopt')
#    except ImportError:
#        pass

    tests.append('t_opf_dc_pips')
    tests.append('t_opf_dc_pips_sc')

#    try:
#        import mosek  #@UnusedImport
#        tests.append('t_opf_dc_mosek')
#    except ImportError:
#        pass

    tests.append('t_opf_userfcns')
    tests.append('t_runopf_w_res')
    tests.append('t_makePTDF')
    tests.append('t_makeLODF')
    tests.append('t_total_load')
    tests.append('t_scale_load')

#    ## smartmarket tests
#    tests.append('t_off2case')
#    tests.append('t_auction_mips')
#    tests.append('t_runmarket')

    t_run_tests(tests, verbose)


def test_pf(verbose=False):
    tests = []

    tests.append('t_loadcase')
    tests.append('t_ext2int2ext')
    tests.append('t_jacobian')
    tests.append('t_pf')

    return t_run_tests(tests, verbose)


def test_opf(verbose=False, *others):
    tests = []

    tests.append('t_loadcase')
    tests.append('t_ext2int2ext')
    tests.append('t_hessian')
    tests.append('t_totcost')
    tests.append('t_modcost')
    tests.append('t_hasPQcap')

    tests.append('t_qps_pypower')

    tests.append('t_opf_dc_pips')
    tests.append('t_opf_dc_pips_sc')

    tests.append('t_pips')

    tests.append('t_opf_pips')
    tests.append('t_opf_pips_sc')

    tests.append('t_runopf_w_res')

    tests.append('t_makePTDF')
    tests.append('t_makeLODF')
    tests.append('t_total_load')
    tests.append('t_scale_load')

    tests.extend(others)

    return t_run_tests(tests, verbose)


if __name__ == '__main__':
    test_pypower(verbose=True)
