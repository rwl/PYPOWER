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

import sys

from numpy import flatnonzero as find

from pypower.idx_bus import *
from pypower.idx_gen import *
from pypower.idx_brch import *

def outputpfsoln(baseMVA, bus, gen, branch, converged, et, type_solver, iterNum):
    """Output power flow solution.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    fd = sys.stdout # output to screen

    ## sizes of things
    nb = bus.shape[0]      ## number of buses
    nl = branch.shape[0]   ## number of branches

    ## parameters
    ong  = find( gen[:, GEN_STATUS] > 0)
    nzld = find(bus[:, PD] | bus[:, QD])

    ## calculate losses
    loss = branch[:, PF] + 1j*branch[:, QF] + branch[:, PT] + 1j*branch[:, QT]

    ## ---output case and solver information
    fd.write('\n\n')
    if type_solver == 1: # newton's method
        fd.write('Newton''s method is chosen to solve Power Flow.\n')
    elif  type_solver == 2: # decoupled method
        fd.write('Decoupled method is chosen to solve Power Flow.\n')
    else:
        raise ValueError, "Error: unknown 'type_solver.\n"

    if converged:
        fd.write('\nConverged in %.2f seconds\n' % et)
    else:
        fd.write('\nDid not converge (%.2f seconds)\n' % et)

    fd.write('\n[iteration number]: %d\n' % iterNum)

    ## ---output generation information
    fd.write('\n================================================================================')
    fd.write('\n|     Generator Data                                                           |')
    fd.write('\n================================================================================')
    fd.write('\n Gen   Bus   Status     Pg        Qg   ')
    fd.write('\n  #     #              (MW)     (MVAr) ')
    fd.write('\n----  -----  ------  --------  --------')
    for i in ong:
        fd.write('\n%3d %6d     %2d ' % (i, gen[i, GEN_BUS], gen[i, GEN_STATUS]))
        if gen[i, GEN_STATUS] > 0 & (gen[i, PG] | gen[i, QG]):
            fd.write('%10.2f%10.2f' % (gen[i, PG], gen[i, QG]))
        else:
            fd.write('       -         -  ')

    fd.write('\n                     --------  --------')
    fd.write('\n            Total: %9.2f%10.2f' % (sum(gen[ong, PG]), sum(gen[ong, QG])))
    fd.write('\n')

    ## ---output bus information
    fd.write('\n================================================================================')
    fd.write('\n|     Bus Data                                                                 |')
    fd.write('\n================================================================================')
    fd.write('\n Bus      Voltage          Generation             Load        ')
    fd.write('\n  #   Mag(pu) Ang(deg)   P (MW)   Q (MVAr)   P (MW)   Q (MVAr)')
    fd.write('\n----- ------- --------  --------  --------  --------  --------')
    for i in range(nb):
        fd.write('\n%5d%7.3f%9.3f' % bus(i, [BUS_I, VM, VA]))
        g  = find(gen[:, GEN_STATUS] > 0 & gen[:, GEN_BUS] == bus[i, BUS_I])
        if len(g) > 0:
            fd.write('%10.2f%10.2f', sum(gen[g, PG]), sum(gen[g, QG]))
        else:
            fd.write('       -         -  ')
        if bus[i, PD] | bus[i, QD]:
            fd.write('%10.2f%10.2f ', bus[i, [PD, QD]])
        else:
            fd.write('       -         -   ')

    fd.write('\n                        --------  --------  --------  --------')
    fd.write('\n               Total: %9.2f %9.2f %9.2f %9.2f' % (
        sum(gen[ong, PG]), sum(gen[ong, QG]),
        sum(bus[nzld, PD]),
        sum(bus[nzld, QD])))
    fd.write('\n')

    ## ---output bus information
    fd.write('\n================================================================================')
    fd.write('\n|     Branch Data                                                              |')
    fd.write('\n================================================================================')
    fd.write('\nBrnch   From   To    From Bus Injection   To Bus Injection     Loss (I^2 * Z)  ')
    fd.write('\n  #     Bus    Bus    P (MW)   Q (MVAr)   P (MW)   Q (MVAr)   P (MW)   Q (MVAr)')
    fd.write('\n-----  -----  -----  --------  --------  --------  --------  --------  --------')
    for i in range(nl):
        fd.write('\n%4d%7d%7d%10.2f%10.2f%10.2f%10.2f%10.3f%10.2f' %
                (   i, branch[i, [F_BUS, T_BUS]],
                    branch[i, [PF, QF]], branch[i, [PT, QT]],
                    loss.real[i], loss.imag[i]
                ))
    fd.write('\n                                                             --------  --------')
    fd.write('\n                                                    Total:%10.3f%10.2f',
            sum(loss.real), sum(loss.imag))
    fd.write('\n')