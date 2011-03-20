# Copyright (C) 2009-2011 Rui Bo <eeborui@hotmail.com>
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

import sys

from numpy import array

from pypower.se.checkDataIntegrity import checkDataIntegrity
from pypower.se.run_se import run_se

def test_se_14bus_err():
    """Test state estimation on IEEE 14-bus system.

    NOTE: This test shows system can be not observable due to measurement
    issues.

    NOTE:
        1) all eight members of 'idx', 'measure' and 'sigma' must be
        defined. They should be null vectors([]) if they do not have data
        2) all data used in this code are for testing purpose only
        which measurements are available
    """
    idx = dict()
    idx["idx_zPF"] = array([0, 2, 7, 8, 9, 12, 14, 18])
    idx["idx_zPT"] = array([3, 4, 6, 10])
    idx["idx_zPG"] = array([0, 1])
    idx["idx_zVa"] = array([])
    idx["idx_zQF"] = array([0, 2, 7, 8, 9, 12, 14, 18])
    idx["idx_zQT"] = array([3, 4, 6, 10])
    idx["idx_zQG"] = array([0, 1])
    idx["idx_zVm"] = array([1, 2])

    ## specify measurements
    measure = dict()
    measure["PF"] = array([1.5708, 0.734, 0.2707, 0.1546, 0.4589, 0.1834, 0.2707, 0.0188])
    measure["PT"] = array([-0.5427, -0.4081, 0.6006, -0.0816])
    measure["PG"] = array([2.32, 0.4])
    measure["Va"] = array([])
    measure["QF"] = array([-0.1748, 0.0594, -0.154, -0.0264, -0.2084, 0.0998, 0.148, 0.0141])
    measure["QT"] = array([0.0213, -0.0193, -0.1006, -0.0864])
    measure["QG"] = array([-0.169, 0.424])
    measure["Vm"] = array([1, 1], float)

    ## specify measurement variances
    sigma = dict();
    sigma["sigma_PF"] = 0.02;
    sigma["sigma_PT"] = 0.02;
    sigma["sigma_PG"] = 0.015;
    sigma["sigma_Va"] = None;
    sigma["sigma_QF"] = 0.02;
    sigma["sigma_QT"] = 0.02;
    sigma["sigma_QG"] = 0.015;
    sigma["sigma_Vm"] = 0.01;

    ## check input data integrity
    nbus = 14;
    success, measure, idx, sigma = checkDataIntegrity(measure, idx, sigma, nbus)
    if not success:
        sys.stderr.write('State Estimation input data are not complete or sufficient!')

    ## run state estimation
    casename = 'case14.m'
    type_initialguess = 2  # flat start
    baseMVA, bus, gen, branch, success, et, z, z_est, error_sqrsum = \
        run_se(casename, measure, idx, sigma, type_initialguess)
