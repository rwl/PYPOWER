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

def ModifiedEuler2(t, Xgen0, Pgen, Vgen0, Xexc0, Pexc, Vexc0, Xgov0, Pgov, Vgov0,
                   invYbus, gbus, genmodel, excmodel, govmodel, stepsize):
    """ Modified Euler ODE solver with check on interface errors

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Set up
    eulerfailed = False

    tol = 1e-8
    maxit = 20

    ## First Prediction Step

    # EXCITERS
    dFexc0 = Exciter(Xexc0, Pexc, Vexc0, excmodel)
    Xexc_new = Xexc0 + stepsize * dFexc0

    # GOVERNORS
    dFgov0 = Governor(Xgov0, Pgov, Vgov0, govmodel)
    Xgov_new = Xgov0 + stepsize * dFgov0

    # GENERATORS
    dFgen0 = Generator(Xgen0, Xexc_new, Xgov_new, Pgen, Vgen0, genmodel)
    Xgen_new = Xgen0 + stepsize * dFgen0

    Vexc_new = copy(Vexc0)
    Vgov_new = copy(Vgov0)
    Vgen_new = copy(Vgen0)

    for i in range(maxit):
        Xexc_old = copy(Xexc_new)
        Xgov_old = copy(Xgov_new)
        Xgen_old = copy(Xgen_new)

        Vexc_old = copy(Vexc_new)
        Vgov_old = copy(Vgov_new)
        Vgen_old = copy(Vgen_new)

        # Calculate system voltages
        U_new = SolveNetwork(Xgen_new, Pgen, invYbus, gbus, genmodel)

        # Calculate machine currents and power
        Id_new, Iq_new, Pe_new = MachineCurrents(Xgen_new, Pgen, U_new[gbus], genmodel)

        # Update variables that have changed
        Vgen_new = r_[Id_new, Iq_new, Pe_new]
        Vexc_new = abs(U_new[gbus])
        Vgov_new = Xgen_new[:, 1]

        # Correct the prediction, and find new values of x
        # EXCITERS
        dFexc1 = Exciter(Xexc_old, Pexc, Vexc_new, excmodel)
        Xexc_new = Xexc0 + stepsize/2 * (dFexc0 + dFexc1)

        # GOVERNORS
        dFgov1 = Governor(Xgov_old, Pgov, Vgov_new, govmodel)
        Xgov_new = Xgov0 + stepsize/2 * (dFgov0 + dFgov1)

        # GENERATORS
        dFgen1 = Generator(Xgen_old, Xexc_new, Xgov_new, Pgen, Vgen_new, genmodel)
        Xgen_new = Xgen0 + stepsize/2 * (dFgen0 + dFgen1)


        # Calculate error
        Xexc_d = abs((Xexc_new - Xexc_old).T)
        Xgov_d = abs((Xgov_new - Xgov_old).T)
        Xgen_d = abs((Xgen_new - Xgen_old).T)

        Vexc_d = abs((Vexc_new - Vexc_old).T)
        Vgov_d = abs((Vgov_new - Vgov_old).T)
        Vgen_d = abs((Vgen_new - Vgen_old).T)

        errest = max( [max(max(Vexc_d)), max(max(Vgov_d)), max(max(Vgen_d)),
                       max(max(Xexc_d)), max(max(Xgov_d)), max(max(Xgen_d)) ])

        if errest < tol:
            break    # solution found
        else:
            if i == maxit:
                U0 = copy(U_new)
                Vexc0 = copy(Vexc_new); Vgov0 = copy(Vgov_new); Vgen0 = copy(Vgen_new)
                Xgen0 = copy(Xgen_new); Xexc0 = copy(Xexc_new); Xgov0 = copy(Xgov_new)
                Pgen0 = copy(Pgen); Pexc0 = copy(Pexc); Pgov0 = copy(Pgov)
                eulerfailed = True
                return Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, t, eulerfailed, stepsize

    ## Update

    U0 = U_new

    Vexc0 = Vexc_new
    Vgov0 = Vgov_new
    Vgen0 = Vgen_new

    Xgen0 = Xgen_new
    Xexc0 = Xexc_new
    Xgov0 = Xgov_new

    Pgen0 = Pgen
    Pexc0 = Pexc
    Pgov0 = Pgov

    return Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, t, eulerfailed, stepsize
