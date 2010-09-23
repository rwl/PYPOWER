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

from numpy import copy

from pypower.bustypes import bustypes
from pypower.ppoption import ppoption
from pypower.newtonpf import newtonpf
from pypower.makeSbus import makeSbus
from pypower.idx_bus import PD, QD

def cpf_correctVoltage(baseMVA, bus, gen, Ybus, V_predicted, lmbda_predicted,
                       initQPratio, loadvarloc):
    """Do correction for predicted voltage in cpf.

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """

    ## get bus index lists of each type of bus
    ref, pv, pq = bustypes(bus, gen)

    ## set load as lmbda indicates
    lmbda = copy(lmbda_predicted)
    bus[loadvarloc, PD] = lmbda * baseMVA
    bus[loadvarloc, QD] = lmbda * baseMVA * initQPratio

    ## compute complex bus power injections (generation - load)
    SbusInj = makeSbus(baseMVA, bus, gen)

    ## prepare initial guess
    V0 = copy(V_predicted) # use predicted voltage to set the initial guess

    ## run power flow to get solution of the current point
    ppopt = ppoption(VERBOSE=0)
    ## run NR's power flow solver
    V, success, iterNum = newtonpf(Ybus, SbusInj, V0, ref, pv, pq, ppopt)

    return V, lmbda, success, iterNum
