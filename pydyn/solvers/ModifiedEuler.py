# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
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

from numpy import copy, r_

from pydyn.models.exciters.Exciter import Exciter
from pydyn.models.governors.Governor import Governor
from pydyn.models.generators.Generator import Generator

from pydyn.SolveNetwork import SolveNetwork
from pydyn.MachineCurrents import MachineCurrents

def ModifiedEuler(t, Xgen0, Pgen, Vgen0, Xexc0, Pexc, Vexc0, Xgov0, Pgov,
        Vgov0, invYbus, gbus, genmodel, excmodel, govmodel, stepsize):
    """ Modified Euler ODE solver

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## First Euler step

    # EXCITERS
    dFexc0 = Exciter(Xexc0, Pexc, Vexc0, excmodel)
    Xexc1 = Xexc0 + stepsize * dFexc0

    # GOVERNORS
    dFgov0 = Governor(Xgov0, Pgov, Vgov0, govmodel)
    Xgov1 = Xgov0 + stepsize * dFgov0

    # GENERATORS
    dFgen0 = Generator(Xgen0, Xexc1, Xgov1, Pgen, Vgen0, genmodel)
    Xgen1 = Xgen0 + stepsize * dFgen0

    # Calculate system voltages
    U1 = SolveNetwork(Xgen1, Pgen, invYbus, gbus, genmodel)

    # Calculate machine currents and power
    Id1, Iq1, Pe1 = MachineCurrents(Xgen1, Pgen, U1(gbus), genmodel)

    # Update variables that have changed
    Vexc1 = abs(U1[gbus])
    Vgen1 = r_[Id1, Iq1, Pe1]
    Vgov1 = Xgen1[:, 1]


    ## Second Euler step

    # EXCITERS
    dFexc1 = Exciter(Xexc1, Pexc, Vexc1, excmodel)
    Xexc2 = Xexc0 + stepsize/2 * (dFexc0 + dFexc1)

    # GOVERNORS
    dFgov1 = Governor(Xgov1, Pgov, Vgov1, govmodel)
    Xgov2 = Xgov0 + stepsize/2 * (dFgov0 + dFgov1)

    # GENERATORS
    dFgen1 = Generator(Xgen1, Xexc2, Xgov2, Pgen, Vgen1, genmodel)
    Xgen2 = Xgen0 + stepsize/2 * (dFgen0 + dFgen1)

    # Calculate system voltages
    U2 = SolveNetwork(Xgen2, Pgen, invYbus, gbus, genmodel)

    # Calculate machine currents and power
    Id2, Iq2, Pe2 = MachineCurrents(Xgen2, Pgen, U2[gbus], genmodel)

    # Update variables that have changed
    Vgen2 = r_[Id2, Iq2, Pe2]
    Vexc2 = abs(U2[gbus])
    Vgov2 = Xgen2[:, 1]

    ## Update

    U0 = U2

    Vgen0 = Vgen2
    Vgov0 = Vgov2
    Vexc0 = Vexc2

    Xgen0 = Xgen2
    Xexc0 = Xexc2
    Xgov0 = Xgov2

    Pgen0 = Pgen
    Pexc0 = Pexc
    Pgov0 = Pgov

    return Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, t, stepsize
