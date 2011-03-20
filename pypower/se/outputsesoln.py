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

import sys

def outputsesoln(idx, sigma, z, z_est, error_sqrsum):
    """Output state estimation solution.

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """

    fd = sys.stdout # output to screen

    fd.write('\n================================================================================')
    fd.write('\n|     Comparison of measurements and their estimations                         |')
    fd.write('\n|     NOTE: In the order of PF, PT, PG, Va, QF, QT, QG, Vm (if applicable)     |')
    fd.write('\n================================================================================')
    fd.write('\n    Type        Index      Measurement   Estimation')
    fd.write('\n                 (#)         (pu)          (pu)    ')
    fd.write('\n -----------  -----------  -----------   ----------')
    cnt = 0
    l = len(idx["idx_zPF"])
    for i in range(l):
        fd.write('\n      PF        %3d      %10.4f     %10.4f' % (idx["idx_zPF"][i], z[i+cnt], z_est[i+cnt]))

    cnt = cnt + l
    len = len(idx["idx_zPT"])
    for i in range(l):
        fd.write('\n      PT        %3d      %10.4f     %10.4f' % (idx["idx_zPT"][i], z[i+cnt], z_est[i+cnt]))

    cnt = cnt + l
    l = len(idx["idx_zPG"])
    for i in range(l):
        fd.write('\n      PG        %3d      %10.4f     %10.4f' % (idx["idx_zPG"][i], z[i+cnt], z_est[i+cnt]))

    cnt = cnt + l
    l = len(idx["idx_zVa"])
    for i in range(l):
        fd.write('\n      Va        %3d      %10.4f     %10.4f' % (idx["idx_zVa"][i], z[i+cnt], z_est[i+cnt]))

    cnt = cnt + l
    l = len(idx["idx_zQF"])
    for i in range(l):
        fd.write('\n      QF        %3d      %10.4f     %10.4f' % (idx["idx_zQF"][i], z[i+cnt], z_est[i+cnt]))

    cnt = cnt + l
    l = len(idx["idx_zQT"])
    for i in range(l):
        fd.write('\n      QT        %3d      %10.4f     %10.4f' % (idx["idx_zQT"][i], z[i+cnt], z_est[i+cnt]))

    cnt = cnt + l
    l = len(idx["idx_zQG"])
    for i in range(l):
        fd.write('\n      QG        %3d      %10.4f     %10.4f' % (idx["idx_zQG"][i], z[i+cnt], z_est[i+cnt]))

    cnt = cnt + l
    l = len(idx["idx_zVm"])
    for i in range(l):
        fd.write('\n      Vm        %3d      %10.4f     %10.4f' % (idx["idx_zVm"][i], z[i+cnt], z_est[i+cnt]))

    fd.write('\n\n[Weighted sum of error squares]:\t%f\n' % error_sqrsum)
