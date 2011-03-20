# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
#
# PYDYN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYDYN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYDYN. If not, see <http://www.gnu.org/licenses/>.

from numpy import array, finfo, r_

from pydyn.models.exciters.Exciter import Exciter
from pydyn.models.governors.Governor import Governor
from pydyn.models.generators.Generator import Generator

from pydyn.SolveNetwork import SolveNetwork
from pydyn.MachineCurrents import MachineCurrents

EPS = finfo(float).eps

def RungeKuttaFehlberg(t0, Xgen0, Pgen, Vgen0, Xexc0, Pexc, Vexc0, Xgov0, Pgov,
        Vgov0, U0, invYbus, gbus, genmodel, excmodel, govmodel, tol, maxstepsize, stepsize):
    """ Runge-Kutta Fehlberg ODE solver

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ##
    # Init
    accept = False
    facmax = 4
    failed = 0

    ## Runge-Kutta coefficients

    # c = [0 1/4 3/8 12/13 1 1/2] not used
    a = array([0, 0, 0, 0, 0,
               1/4., 0, 0, 0, 0,
               3/32., 9/32., 0, 0, 0,
               1932/2197., -7200/2197., 7296/2197., 0, 0,
               439/216., -8, 3680/513., -845/4104., 0,
               -8/27., 2, -3544/2565., 1859/4104., -11/40.])
    b1 = array([25/216., 0, 1408/2565., 2197/4104., -1/5., 0])
    b2 = array([16/135., 0, 6656/12825., 28561/56430., -9/50., 2/55])

    ##
    i=0
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
        Xexc6 = Xexc0 + stepsize * (b1[0] * Kexc1 + b1[1] * Kexc2 + b1[2] * Kexc3 + b1[3] * Kexc4 + b1[4] * Kexc5 + b1[5] * Kexc6)

        # GOVERNORS
        Kgov6 = Governor(Xgov5, Pgov, Vgov5, govmodel)
        Xgov6 = Xgov0 + stepsize * (b1[0] * Kgov1 + b1[1] * Kgov2 + b1[2] * Kgov3 + b1[3] * Kgov4 + b1[4] * Kgov5 + b1[5] * Kgov6)

        # GENERATORS
        Kgen6 = Generator(Xgen5, Xexc6, Xgov6, Pgen, Vgen5, genmodel)
        Xgen6 = Xgen0 + stepsize * (b1[0] * Kgen1 + b1[1] * Kgen2 + b1[2] * Kgen3 + b1[3] * Kgen4 + b1[4] * Kgen5 + b1[5] * Kgen6)


        # Calculate system voltages
        U6 = SolveNetwork(Xgen6, Pgen, invYbus, gbus, genmodel)

        # Calculate machine currents and power
        Id6, Iq6, Pe6 = MachineCurrents(Xgen6, Pgen, U6[gbus], genmodel)

        # Update variables that have changed
        Vexc6 = abs(U6[gbus])
        Vgen6 = r_[Id6, Iq6, Pe6]
        Vgov6 = Xgen6[:, 1]


        ## Second, higher order solution

        Xexc62 = Xexc0 + stepsize * (b2[0] * Kexc1 + b2[1] * Kexc2 + b2[2] * Kexc3 + b2[3] * Kexc4 + b2[4] * Kexc5 + b2[5] * Kexc6)
        Xgov62 = Xgov0 + stepsize * (b2[0] * Kgov1 + b2[1] * Kgov2 + b2[2] * Kgov3 + b2[3] * Kgov4 + b2[4] * Kgov5 + b2[5] * Kgov6)
        Xgen62 = Xgen0 + stepsize * (b2[0] * Kgen1 + b2[1] * Kgen2 + b2[2] * Kgen3 + b2[3] * Kgen4 + b2[4] * Kgen5 + b2[5] * Kgen6)

        ## Error estimate

        Xexc = abs((Xexc62 - Xexc6).T)
        Xgov = abs((Xgov62 - Xgov6).T)
        Xgen = abs((Xgen62 - Xgen6).T)
        errest = max( [max(max(Xexc)), max(max(Xgov)), max(max(Xgen)) ])

        if errest < EPS:
            errest = EPS

        q = 0.84 * (tol / errest)**(1/4.)

        if errest < tol:
            accept = True

            U0 = U6

            Vgen0 = Vgen6
            Vgov0 = Vgov6
            Vexc0 = Vexc6

            Xgen0 = Xgen6
            Xexc0 = Xexc6
            Xgov0 = Xgov6

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

            stepsize = min(max(q, 0.1), facmax) * stepsize
            return Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, errest, failed, t, stepsize

        stepsize = min(max(q, 0.1), facmax) * stepsize

        if stepsize > maxstepsize:
            stepsize = maxstepsize

    return Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, errest, failed, t, stepsize
