# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
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
