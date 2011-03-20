# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
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

from numpy import array

from pypower.se.run_se import run_se

def test_se():
    """Test state estimation.

    Using data in Problem 6.7 in book 'Computational
    Methods for Electric Power Systems' by Mariesa Crow

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## specify measurements
    measure = {}
    measure["PF"] = array([0.12, 0.10])
    measure["PT"] = array([-0.04])
    measure["PG"] = array([0.58, 0.30, 0.14])
    measure["Va"] = array(array([]))
    measure["QF"] = array([])
    measure["QT"] = array([])
    measure["QG"] = array([])
    measure["Vm"] = array([1.04, 0.98])

    ## specify measurement variances
    sigma = {}
    sigma["sigma_PF"] = array([0.02])
    sigma["sigma_PT"] = array([0.02])
    sigma["sigma_PG"] = array([0.015])
    sigma["sigma_Va"] = array([])
    sigma["sigma_QF"] = array([])
    sigma["sigma_QT"] = array([])
    sigma["sigma_QG"] = array([])
    sigma["sigma_Vm"] = array([0.01])

    ## which measurements are available
    idx = {}
    idx["idx_zPF"] = array([1, 2])
    idx["idx_zPT"] = array([3])
    idx["idx_zPG"] = array([1, 2, 3])
    idx["idx_zVa"] = array([])
    idx["idx_zQF"] = array([])
    idx["idx_zQT"] = array([])
    idx["idx_zQG"] = array([])
    idx["idx_zVm"] = array([2, 3])

    ## run state estimation
    casename = 'case3bus_P6_6.m'
    type_initialguess = 2 # flat start
    baseMVA, bus, gen, branch, success, et, z, z_est, error_sqrsum = \
        run_se(casename, measure, idx, sigma, type_initialguess)
