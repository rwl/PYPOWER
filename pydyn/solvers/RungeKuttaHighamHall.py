# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
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

from numpy import array, finfo, r_

from pydyn.models.exciters.Exciter import Exciter
from pydyn.models.governors.Governor import Governor
from pydyn.models.generators.Generator import Generator

from pydyn.SolveNetwork import SolveNetwork
from pydyn.MachineCurrents import MachineCurrents

EPS = finfo(float).eps

def RungeKuttaHighamHall(t0, Xgen0, Pgen, Vgen0, Xexc0, Pexc, Vexc0, Xgov0, Pgov, Vgov0,
            U0, invYbus, gbus, genmodel, excmodel, govmodel, tol, maxstepsize, stepsize):
    """ Runge-Kutta Higham and Hall ODE solver

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ##
    # Init
    accept = False
    facmax = 4
    failed = 0


    ## Runge-Kutta coefficients

    # c = [0 2/9 1/3 1/2 3/5 1 1] not used
    a = array([0, 0, 0, 0, 0, 0,
               2/9., 0, 0, 0, 0, 0,
               1/12., 1/4., 0, 0, 0, 0,
               1/8., 0, 3/8., 0, 0, 0,
               91/500., -27/100., 78/125., 8/125., 0, 0,
               -11/20., 27/20., 12/5., -36/5., 5, 0,
               1/12., 0, 27/32., -4/3., 125/96., 5/48.])
    b1 = array([1/12., 0, 27/32., -4/3., 125/96., 5/48., 0])
    b2 = array([2/15., 0, 27/80., -2/15., 25/48., 1/24., 1/10])

    ##
    i = 0
    while accept == False:
        i += 1

        ## K1

        # EXCITERS
        Kexc1 = Exciter(Xexc0, Pexc, Vexc0, excmodel)
        Xexc1 = Xexc0 + stepsize * a[1, 0] * Kexc1

        # GOVERNORS
        Kgov1 = Governor(Xgov0, Pgov, Vgov0, govmodel)
        Xgov1 = Xgov0 + stepsize * a[1, 0] * Kgov1

        # GENERATORS
        Kgen1 = Generator(Xgen0, Xexc1, Xgov1, Pgen, Vgen0, genmodel)
        Xgen1 = Xgen0 + stepsize * a[1, 0] * Kgen1


        # Calculate system voltages
        U1 = SolveNetwork(Xgen1, Pgen, invYbus, gbus, genmodel)

        # Calculate machine currents and power
        Id1, Iq1, Pe1 = MachineCurrents(Xgen1, Pgen, U1[gbus], genmodel)

        # Update variables that have changed
        Vexc1 = abs(U1[gbus])
        Vgen1 = r_[Id1, Iq1, Pe1]
        Vgov1 = Xgen1[:, 1]


        ## K2

        # EXCITERS
        Kexc2 = Exciter(Xexc1, Pexc, Vexc1, excmodel)
        Xexc2 = Xexc0 + stepsize * (a[2, 0] * Kexc1 + a[2, 1] * Kexc2 )

        # GOVERNORS
        Kgov2 = Governor(Xgov1, Pgov, Vgov1, govmodel)
        Xgov2 = Xgov0 + stepsize * (a[2, 0] * Kgov1 + a[2, 1] * Kgov2 )

        # GENERATORS
        Kgen2 = Generator(Xgen1, Xexc2, Xgov2, Pgen, Vgen1, genmodel)
        Xgen2 = Xgen0 + stepsize * (a[2, 0] * Kgen1 + a[2, 1] * Kgen2 )


        # Calculate system voltages
        U2 = SolveNetwork(Xgen2, Pgen, invYbus, gbus, genmodel)

        # Calculate machine currents and power
        Id2, Iq2, Pe2 = MachineCurrents(Xgen2, Pgen, U2[gbus], genmodel)

        # Update variables that have changed
        Vexc2 = abs(U2[gbus])
        Vgen2 = r_[Id2, Iq2, Pe2]
        Vgov2 = Xgen2[:, 1]


        ## K3

        # EXCITERS
        Kexc3 = Exciter(Xexc2, Pexc, Vexc2, excmodel)
        Xexc3 = Xexc0 + stepsize * (a[3, 0] * Kexc1 + a[3, 1] * Kexc2 + a[3, 2] * Kexc3)

        # GOVERNORS
        Kgov3 = Governor(Xgov2, Pgov, Vgov2, govmodel)
        Xgov3 = Xgov0 + stepsize * (a[3, 0] * Kgov1 + a[3, 1] * Kgov2 + a[3, 2] * Kgov3)

        # GENERATORS
        Kgen3 = Generator(Xgen2, Xexc3, Xgov3, Pgen, Vgen2, genmodel)
        Xgen3 = Xgen0 + stepsize * (a[3, 0] * Kgen1 + a[3, 1] * Kgen2 + a[3, 2] * Kgen3)


        # Calculate system voltages
        U3 = SolveNetwork(Xgen3, Pgen, invYbus, gbus, genmodel)

        # Calculate machine currents and power
        Id3, Iq3, Pe3 = MachineCurrents(Xgen3, Pgen, U3[gbus], genmodel)

        # Update variables that have changed
        Vexc3 = abs(U3[gbus])
        Vgen3 = r_[Id3, Iq3, Pe3]
        Vgov3 = Xgen3[:, 1]


        ## K4

        # EXCITERS
        Kexc4 = Exciter(Xexc3, Pexc, Vexc3, excmodel)
        Xexc4 = Xexc0 + stepsize * (a[4, 0] * Kexc1 + a[4, 1] * Kexc2 + a[4, 2] * Kexc3 + a[4, 3] * Kexc4)

        # GOVERNORS
        Kgov4 = Governor(Xgov3, Pgov, Vgov3, govmodel)
        Xgov4 = Xgov0 + stepsize * (a[4, 0] * Kgov1 + a[4, 1] * Kgov2 + a[4, 2] * Kgov3 + a[4, 3] * Kgov4)

        # GENERATORS
        Kgen4 = Generator(Xgen3, Xexc4, Xgov4, Pgen, Vgen3, genmodel)
        Xgen4 = Xgen0 + stepsize * (a[4, 0] * Kgen1 + a[4, 1] * Kgen2 + a[4, 2] * Kgen3 + a[4, 3] * Kgen4)

        # Calculate system voltages
        U4 = SolveNetwork(Xgen4, Pgen, invYbus, gbus, genmodel)

        # Calculate machine currents and power
        Id4, Iq4, Pe4 = MachineCurrents(Xgen4, Pgen, U4[gbus], genmodel)

        # Update variables that have changed
        Vexc4 = abs(U4[gbus])
        Vgen4 = r_[Id4, Iq4, Pe4]
        Vgov4 = Xgen4[:, 1]


        ## K5

        # EXCITERS
        Kexc5 = Exciter(Xexc4, Pexc, Vexc4, excmodel)
        Xexc5 = Xexc0 + stepsize * (a[5, 0] * Kexc1 + a[5, 1] * Kexc2 + a[5, 2] * Kexc3 + a[5, 3] * Kexc4 + a[5, 4] * Kexc5)

        # GOVERNORS
        Kgov5 = Governor(Xgov4, Pgov, Vgov4, govmodel)
        Xgov5 = Xgov0 + stepsize * (a[5, 0] * Kgov1 + a[5, 1] * Kgov2 + a[5, 2] * Kgov3 + a[5, 3] * Kgov4 + a[5, 4] * Kgov5)

        # GENERATORS
        Kgen5 = Generator(Xgen4, Xexc5, Xgov5, Pgen, Vgen4, genmodel)
        Xgen5 = Xgen0 + stepsize * (a[5, 0] * Kgen1 + a[5, 1] * Kgen2 + a[5, 2] * Kgen3 + a[5, 3] * Kgen4 + a[5, 4] * Kgen5)


        # Calculate system voltages
        U5 = SolveNetwork(Xgen5, Pgen, invYbus, gbus, genmodel)

        # Calculate machine currents and power
        Id5, Iq5, Pe5 = MachineCurrents(Xgen5, Pgen, U5[gbus], genmodel)

        # Update variables that have changed
        Vexc5 = abs(U5[gbus])
        Vgen5 = r_[Id5, Iq5, Pe5]
        Vgov5 = Xgen5[:, 1]

        ## K6

        # EXCITERS
        Kexc6 = Exciter(Xexc5, Pexc, Vexc5, excmodel)
        Xexc6 = Xexc0 + stepsize * (a[6, 0] * Kexc1 + a[6, 1] * Kexc2 + a[6, 2] * Kexc3 + a[6, 3] * Kexc4 + a[6, 4] * Kexc5 + a[6, 5] * Kexc6)

        # GOVERNORS
        Kgov6 = Governor(Xgov5, Pgov, Vgov5, govmodel)
        Xgov6 = Xgov0 + stepsize * (a[6, 0] * Kgov1 + a[6, 1] * Kgov2 + a[6, 2] * Kgov3 + a[6, 3] * Kgov4 + a[6, 4] * Kgov5 + a[6, 5] * Kgov6)

        # GENERATORS
        Kgen6 = Generator(Xgen5, Xexc6, Xgov6, Pgen, Vgen5, genmodel)
        Xgen6 = Xgen0 + stepsize * (a[6, 0] * Kgen1 + a[6, 1] * Kgen2 + a[6, 2] * Kgen3 + a[6, 3] * Kgen4 + a[6, 4] * Kgen5 + a[6, 5] * Kgen6)


        # Calculate system voltages
        U6 = SolveNetwork(Xgen6, Pgen, invYbus, gbus, genmodel)

        # Calculate machine currents and power
        Id6, Iq6, Pe6 = MachineCurrents(Xgen6, Pgen, U6[gbus], genmodel)

        # Update variables that have changed
        Vexc6 = abs(U6[gbus])
        Vgen6 = r_[Id6, Iq6, Pe6]
        Vgov6 = Xgen6[:, 1]


        ## K7

        # EXCITERS
        Kexc7 = Exciter(Xexc6, Pexc, Vexc6, excmodel)
        Xexc7 = Xexc0 + stepsize * (b1[0] * Kexc1 + b1[1] * Kexc2 + b1[2] * Kexc3 + b1[3] * Kexc4 + b1[4] * Kexc5 + b1[5] * Kexc6 + b1[6] * Kexc7)

        # GOVERNORS
        Kgov7 = Governor(Xgov6, Pgov, Vgov6, govmodel)
        Xgov7 = Xgov0 + stepsize * (b1[0] * Kgov1 + b1[1] * Kgov2 + b1[2] * Kgov3 + b1[3] * Kgov4 + b1[4] * Kgov5 + b1[5] * Kgov6 + b1[6] * Kgov7)

        # GENERATORS
        Kgen7 = Generator(Xgen6, Xexc7, Xgov7, Pgen, Vgen6, genmodel)
        Xgen7 = Xgen0 + stepsize * (b1[0] * Kgen1 + b1[1] * Kgen2 + b1[2] * Kgen3 + b1[3] * Kgen4 + b1[4] * Kgen5 + b1[5] * Kgen6 + b1[6] * Kgen7)


        # Calculate system voltages
        U7 = SolveNetwork(Xgen7, Pgen, invYbus, gbus, genmodel)

        # Calculate machine currents and power
        Id7, Iq7, Pe7 = MachineCurrents(Xgen7, Pgen, U7[gbus], genmodel)

        # Update variables that have changed
        Vexc7 = abs(U7[gbus])
        Vgen7 = r_[Id7, Iq7, Pe7]
        Vgov7 = Xgen7[:, 1]


        ## Second, higher order solution

        Xexc72 = Xexc0 + stepsize * (b2[0] * Kexc1 + b2[1] * Kexc2 + b2[2] * Kexc3 + b2[3] * Kexc4 + b2[4] * Kexc5 + b2[5] * Kexc6 + b2[6] * Kexc7)
        Xgov72 = Xgov0 + stepsize * (b2[0] * Kgov1 + b2[1] * Kgov2 + b2[2] * Kgov3 + b2[3] * Kgov4 + b2[4] * Kgov5 + b2[5] * Kgov6 + b2[6] * Kgov7)
        Xgen72 = Xgen0 + stepsize * (b2[0] * Kgen1 + b2[1] * Kgen2 + b2[2] * Kgen3 + b2[3] * Kgen4 + b2[4] * Kgen5 + b2[5] * Kgen6 + b2[6] * Kgen7)

        ## Error estimate

        Xexc = abs((Xexc72 - Xexc7).T)
        Xgov = abs((Xgov72 - Xgov7).T)
        Xgen = abs((Xgen72 - Xgen7).T)
        errest = max( [max(max(Xexc)), max(max(Xgov)), max(max(Xgen)) ])

        if errest < EPS:
            errest = EPS

        q = 0.84 * (tol / errest)**(1/4.)

        if errest < tol:
            accept = True

            U0 = U7

            Vgen0 = Vgen7
            Vgov0 = Vgov7
            Vexc0 = Vexc7

            Xgen0 = Xgen7
            Xexc0 = Xexc7
            Xgov0 = Xgov7

            Pgen0 = Pgen
            Pexc0 = Pexc
            Pgov0 = Pgov

            t = t0
        else:
            failed += 1
            facmax = 1

            t = t0
            Pgen0 = Pgen
            Pexc0 = Pexc
            Pgov0 = Pgov

            stepsize = min(max(q, 0.1), facmax)*stepsize
            return Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, errest, failed, t, stepsize

        stepsize = min(max(q, 0.1), facmax) * stepsize

        if (stepsize > maxstepsize):
            stepsize = maxstepsize

    return Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, errest, failed, t, stepsize
