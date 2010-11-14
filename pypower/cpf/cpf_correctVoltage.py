# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

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