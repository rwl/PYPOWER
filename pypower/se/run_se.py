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

from time import time

from pypower.loadcase import loadcase
from pypower.ext2int import ext2int
from pypower.bustypes import bustypes
from pypower.makeYbus import makeYbus
from pypower.pfsoln import pfsoln
from pypower.int2ext import int2ext

from pypower.se.getV0 import getV0
from pypower.se.doSE import doSE
from pypower.se.outputpfsoln import outputpfsoln
from pypower.se.outputsesoln import outputsesoln

def run_se(casename, measure, idx, sigma, type_initialguess, V0=None):
    """Run state estimation.

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## read data & convert to internal bus numbering
    baseMVA, bus, gen, branch = loadcase(casename)
    i2e, bus, gen, branch = ext2int(bus, gen, branch)

    ## get bus index lists of each type of bus
    ref, pv, pq = bustypes(bus, gen)

    ## build admittance matrices
    Ybus, Yf, Yt = makeYbus(baseMVA, bus, branch)

    ## prepare initial guess
    if V0 is None:
        V0 = getV0(bus, gen, type_initialguess)
    else:
        V0 = getV0(bus, gen, type_initialguess, V0)

    ## run state estimation
    t0 = time()
    V, success, iterNum, z, z_est, error_sqrsum = \
        doSE(baseMVA, bus, gen, branch, Ybus, Yf, Yt, V0, ref, pv, pq, measure, idx, sigma)
    ## update data matrices with solution, ie, V
    # bus, gen, branch = updatepfsoln(baseMVA, bus, gen, branch, Ybus, V, ref, pv, pq)
    bus, gen, branch = pfsoln(baseMVA, bus, gen, branch, Ybus, Yf, Yt, V, ref, pv, pq)
    et = time() - t0

    ##-----  output results  -----
    ## convert back to original bus numbering & print results
    bus, gen, branch = int2ext(i2e, bus, gen, branch)
    ## output power flow solution
    outputpfsoln(baseMVA, bus, gen, branch, success, et, 1, iterNum)
    ## output state estimation solution
    outputsesoln(idx, sigma, z, z_est, error_sqrsum)

    return baseMVA, bus, gen, branch, success, et, z, z_est, error_sqrsum
