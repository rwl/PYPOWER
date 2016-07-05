# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Run all PYPOWER tests.
"""

from pypower.t.t_run_tests import t_run_tests

from pypower.util import have_fcn


def test_pypower(verbose=False):
    """Run all PYPOWER tests.

    Prints the details of the individual tests if verbose is true.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    tests = []

    ## PYPOWER base test
    tests.append('t_loadcase')
    # tests.append('t_ext2int2ext')
    tests.append('t_jacobian')
    tests.append('t_hessian')
    tests.append('t_totcost')
    tests.append('t_modcost')
    tests.append('t_hasPQcap')
    tests.append('t_savecase')

    # tests.append('t_pips')

    # tests.append('t_qps_pypower')
    # tests.append('t_pf')

    if have_fcn('gurobipy'):
        tests.append('t_opf_dc_gurobi')

    # tests.append('t_opf_pips')
    # tests.append('t_opf_pips_sc')

    if have_fcn('pyipopt'):
        tests.append('t_opf_ipopt')
        tests.append('t_opf_dc_ipopt')

    # tests.append('t_opf_dc_pips')
    # tests.append('t_opf_dc_pips_sc')

    if have_fcn('mosek'):
        tests.append('t_opf_dc_mosek')

    # tests.append('t_opf_userfcns')
    # tests.append('t_runopf_w_res')
    # tests.append('t_dcline')
    # tests.append('t_makePTDF')
    # tests.append('t_makeLODF')
    # tests.append('t_total_load')
    # tests.append('t_scale_load')

    ## smartmarket tests
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

    if have_fcn('gurobipy'):
        tests.append('t_opf_dc_gurobi')

    tests.append('t_opf_dc_pips')
    tests.append('t_opf_dc_pips_sc')

    tests.append('t_pips')

    tests.append('t_opf_pips')
    tests.append('t_opf_pips_sc')

    if have_fcn('pyipopt'):
        tests.append('t_opf_ipopt')
        tests.append('t_opf_dc_ipopt')

    if have_fcn('mosek'):
        tests.append('t_opf_dc_mosek')

    tests.append('t_runopf_w_res')

    tests.append('t_makePTDF')
    tests.append('t_makeLODF')
    tests.append('t_total_load')
    tests.append('t_scale_load')

    tests.extend(others)

    return t_run_tests(tests, verbose)


if __name__ == '__main__':
    test_pypower(verbose=True)
