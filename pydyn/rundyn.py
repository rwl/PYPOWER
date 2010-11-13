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

from time import time

from numpy import array, zeros, cos, sin, pi, copy, finfo, r_, c_
from numpy import flatnonzero as find

from pypower.ppoption import ppoption
from pypower.runpf import runpf

from pypower.idx_bus import VM, VA, PD, QD
from pypower.idx_gen import GEN_STATUS, GEN_BUS

from pydyn.Pdoption import Pdoption
from pydyn.Loaddyn import Loaddyn
from pydyn.Loadgen import Loadgen
from pydyn.Loadexc import Loadexc
from pydyn.Loadgov import Loadgov
from pydyn.Loadevents import Loadevents
from pydyn.AugYbus import AugYbus
from pydyn.MachineCurrents import MachineCurrents
from pydyn.SolveNetwork import SolveNetwork

from pydyn.models.generators.GeneratorInit import GeneratorInit
from pydyn.models.generators.Generator import Generator
from pydyn.models.exciters.ExciterInit import ExciterInit
from pydyn.models.exciters.Exciter import Exciter
from pydyn.models.governors.GovernorInit import GovernorInit
from pydyn.models.governors.Governor import Governor

from pydyn.solvers.ModifiedEuler import ModifiedEuler
from pydyn.solvers.RungeKutta import RungeKutta
from pydyn.solvers.RungeKuttaFehlberg import RungeKuttaFehlberg
from pydyn.solvers.RungeKuttaHighamHall import RungeKuttaHighamHall
from pydyn.solvers.ModifiedEuler2 import ModifiedEuler2

EPS = finfo(float).eps

def rundyn(casefile_pf, casefile_dyn, casefile_ev, pdopt=None):
    """ Runs dynamic simulation.

    @param casefile_pf: m-file with power flow data
    @param casefile_dyn: m-file with dynamic data
    @param casefile_ev: m-file with event data
    @param pdopt: options vector
    @rtype: tuple
    @return: (Angles = generator angles,
        Speeds = generator speeds,
        Eq_tr = q component of transient voltage behind reactance,
        Ed_tr = d component of transient voltage behind reactance,
        Efd = Excitation voltage,
        PM = mechanical power,
        Voltages = bus voltages,
        Stepsize = step size integration method,
        Errest = estimation of integration error,
        Failed = failed steps,
        Time = time points)

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Begin timing
    t0 = time()

    if pdopt is None:
        pdopt = Pdoption()

    method = pdopt[0]
    tol = pdopt[1]
    minstepsize = pdopt[2]
    maxstepsize = pdopt[3]
    output = bool(pdopt[4])
    plots = bool(pdopt[5])

    ## Load all data

    # Load dynamic simulation data
    if output:
        print '> Loading dynamic simulation data...'
    global freq
    freq, stepsize, stoptime = Loaddyn(casefile_dyn)

    # Load generator data
    Pgen0 = Loadgen(casefile_dyn, output)

    # Load exciter data
    Pexc0 = Loadexc(casefile_dyn)

    # Load governor data
    Pgov0 = Loadgov(casefile_dyn)

    # Load event data
    if len(casefile_ev) > 0:
        event, buschange, linechange = Loadevents(casefile_ev)
    else:
        event = array([])

    genmodel = Pgen0[:, 0]
    excmodel = Pgen0[:, 1]
    govmodel = Pgen0[:, 2]

    ## Initialization: Power Flow

    # Power flow options
    ppopt = ppoption()
    ppopt["VERBOSE"] = False
    ppopt["OUT_ALL"] = False

    # Run power flow
    baseMVA, bus, gen, branch, success = runpf(casefile_pf, ppopt)
    if not success:
        print '> Error: Power flow did not converge. Exiting...'
        return
    else:
        if output:
            print '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b> Power flow converged\n'

    U0 = bus[:, VM] * (cos(bus[:, VA] * pi / 180) + 1j * sin(bus[:, VA] * pi / 180 ))
    U00 = copy(U0)
    # Get generator info
    on = find(gen[:, GEN_STATUS] > 0)     ## which generators are on?
    gbus = gen[on, GEN_BUS]               ## what buses are they at?
    ngen = len(gbus)

    nbus = len(U0)

    ## Construct augmented Ybus
    if output:
        print '> Constructing augmented admittance matrix...'
    Pl = bus[:, PD] / baseMVA                  ## load power
    Ql = bus[:, QD] / baseMVA

    xd_tr = zeros(ngen)
    xd_tr[genmodel == 2] = Pgen0[genmodel == 2, 7] # 4th order model: xd_tr column 7
    xd_tr[genmodel == 1] = Pgen0[genmodel == 1, 6] # classical model: xd_tr column 6

    invYbus = AugYbus(baseMVA, bus, branch, xd_tr, gbus, Pl, Ql, U0)

    ## Calculate Initial machine state
    if output:
        print '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b> Calculating initial state...\n'
    Efd0, Xgen0 = GeneratorInit(Pgen0, U0(gbus), gen, baseMVA, genmodel)

    omega0 = Xgen0[:, 0]

    Id0, Iq0, Pe0 = MachineCurrents(Xgen0, Pgen0, U0[gbus], genmodel)
    Vgen0 = r_[Id0, Iq0, Pe0]

    ## Exciter initial conditions
    Vexc0 = abs(U0[gbus])
    Xexc0, Pexc0 = ExciterInit(Efd0, Pexc0, Vexc0, excmodel)

    ## Governor initial conditions
    Pm0 = copy(Pe0)
    Xgov0, Pgov0 = GovernorInit(Pm0, Pgov0, omega0, govmodel)
    Vgov0 = copy(omega0)

    ## Check Steady-state
    Fexc0 = Exciter(Xexc0, Pexc0, Vexc0, excmodel)
    Fgov0 = Governor(Xgov0, Pgov0, Vgov0, govmodel)
    Fgen0 = Generator(Xgen0, Xexc0, Xgov0, Pgen0, Vgen0, genmodel)

    # Check Generator Steady-state
    if sum(sum(abs(Fgen0))) > 1e-6:
        print '> Error: Generator not in steady-state\n> Exiting...\n'
        return
    # Check Exciter Steady-state
    if sum(sum(abs(Fexc0))) > 1e-6:
        print '> Error: Exciter not in steady-state\n> Exiting...\n'
        return
    # Check Governor Steady-state
    if sum(sum(abs(Fgov0))) > 1e-6:
        print '> Error: Governor not in steady-state\n> Exiting...\n'
        return

    if output:
        print '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b> System in steady-state\n'

    ## Initialization of main stability loop
    t = -0.02 # simulate 0.02s without applying events
    errest = 0
    failed = 0
    eulerfailed = 0

    if method == 3 | method == 4:
        stepsize = minstepsize

    if not output:
        print '                   '

    ev = 1
    eventhappened = False
    i = 0

    ## Allocate memory for variables

    if output:
        print '> Allocate memory...\n'
    chunk = 5000

    Time = zeros(chunk); Time[0, :] = t
    Errest = zeros(chunk); Errest[0, :] = errest
    Stepsize = zeros(chunk); Stepsize[0, :] = stepsize

    # System variables
    Voltages = zeros(chunk, len(U0)); Voltages[0, :] = U0

    # Generator
    Angles = zeros(chunk, ngen); Angles[0, :] = Xgen0[:, 0] * 180 / pi
    Speeds = zeros(chunk, ngen); Speeds[0, :] = Xgen0[:, 2] / (2 * pi * freq)
    Eq_tr = zeros(chunk, ngen); Eq_tr[0, :] = Xgen0[:, 2]
    Ed_tr = zeros(chunk, ngen); Ed_tr[0, :] = Xgen0[:, 3]

    # Exciter and governor
    Efd = zeros(chunk,ngen); Efd[0, :] = Efd0[:, 0]
    PM = zeros(chunk, ngen); PM[0, :] = Pm0[:, 0]

    ## Main stability loop
    while t < stoptime + stepsize:

        ## Output
        i += 1
        if i % 45 == 0 & output:
            print '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b> %6.2f## completed' % t / stoptime * 100

        ## Numerical Method
        if method == 1:
            Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, t, newstepsize = \
                ModifiedEuler(t, Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, invYbus, gbus, genmodel, excmodel, govmodel, stepsize)
        elif method == 2:
            Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, t, newstepsize = \
                RungeKutta(t, Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, invYbus, gbus, genmodel, excmodel, govmodel, stepsize)
        elif method == 3:
            Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, errest, failed, t, newstepsize = \
                RungeKuttaFehlberg(t, Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, invYbus, gbus, genmodel, excmodel, govmodel, tol, maxstepsize, stepsize)
        elif method == 4:
            Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, errest, failed, t, newstepsize = \
                RungeKuttaHighamHall(t, Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, invYbus, gbus, genmodel, excmodel, govmodel, tol, maxstepsize, stepsize)
        elif method == 5:
            Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, U0, t, eulerfailed, newstepsize = \
                ModifiedEuler2(t, Xgen0, Pgen0, Vgen0, Xexc0, Pexc0, Vexc0, Xgov0, Pgov0, Vgov0, invYbus, gbus, genmodel, excmodel, govmodel, stepsize)

        if eulerfailed:
            print '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b> Error: No solution found. Try lowering tolerance or increasing maximum number of iterations in ModifiedEuler2. Exiting... \n'
            return

        if failed:
            t -= stepsize

        # End exactly at stop time
        if t + newstepsize > stoptime:
            newstepsize = stoptime - t
        elif stepsize < minstepsize:
            print '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b> Error: No solution found with minimum step size. Exiting... \n'
            return

        ## Allocate new memory chunk if matrices are full
        if i > Time.shape[0]:
            Stepsize = c_[Stepsize, zeros(chunk)];
            Errest = c_[Errest, zeros(chunk)]
            Time = c_[Time, zeros(chunk)]
            Voltages = c_[Voltages, zeros(chunk, len(U0))]
            Efd = c_[Efd, zeros(chunk, ngen)]
            PM = c_[PM, zeros(chunk, ngen)]
            Angles = c_[Angles, zeros(chunk,ngen)]
            Speeds = c_[Speeds, zeros(chunk,ngen)]
            Eq_tr = c_[Eq_tr, zeros(chunk,ngen)]
            Ed_tr = c_[Ed_tr, zeros(chunk,ngen)]

        ## Save values
        Stepsize[i, :] = stepsize.T
        Errest[i, :] = errest.T
        Time[i, :] = t

        Voltages[i, :] = U0.T

        # exc
        Efd[i, :] = Xexc0[:, 0] * (genmodel > 1) # Set Efd to zero when using classical generator model

        # gov
        PM[i, :] = Xgov0[:, 0]

        # gen
        Angles[i, :] = Xgen0[:, 0] * 180 / pi
        Speeds[i, :] = Xgen0[:, 1] / (2 * pi * freq)
        Eq_tr[i, :] = Xgen0[:, 2]
        Ed_tr[i, :] = Xgen0[:, 3]

        ## Adapt step size if event will occur in next step
        if len(event) > 0 & ev <= event.shape[0] & (method == 3 | method == 4):
            if t + newstepsize >= event[ev, 0]:
                if event[ev, 0] - t < newstepsize:
                    newstepsize = event[ev, 0] - t

        ## Check for events
        if len(event) > 0 & ev <= event.shape[0]:

            for k in range(ev, event.shape[0]): # cycle through all events ..
                if abs(t - event[ev, 0]) > 10 * EPS | ev > event.shape[0]: #.. that happen on time t
                    break
                else:
                    eventhappened = True

                    if event[ev, 1] == 1:
                        bus[buschange[ev, 1], buschange[ev, 2]] = buschange[ev, 3]
                    if event[ev, 1] == 2:
                        branch[linechange[ev, 1], linechange[ev, 2]] = linechange[ev, 3]
                    ev += 1

            if eventhappened:
                # Refactorise
                invYbus = AugYbus(baseMVA, bus, branch, xd_tr, gbus, bus[:, PD] / baseMVA, bus[:, QD] / baseMVA, U00)
                U0 = SolveNetwork(Xgen0, Pgen0, invYbus, gbus, genmodel)

                Id0, Iq0, Pe0 = MachineCurrents(Xgen0, Pgen0, U0(gbus), genmodel)
                Vgen0 = Id0,Iq0,Pe0
                Vexc0 = abs(U0[gbus])

                # decrease stepsize after event occured
                if method == 3 | method == 4:
                    newstepsize = minstepsize

                i += 1 # if event occurs, save values at t- and t+

                ## Save values
                Stepsize[i, :] = stepsize.T
                Errest[i, :] = errest.T
                Time[i, :] = t

                Voltages[i, :] = U0.T

                # exc
                Efd[i, :] = Xexc0[:, 0] * (genmodel > 1) # Set Efd to zero when using classical generator model

                # gov
                PM[i, :] = Xgov0[:, 0]

                # gen
                Angles[i, :] = Xgen0[:, 0] * 180 / pi
                Speeds[i, :] = Xgen0[:, 1] / (2 * pi * freq)
                Eq_tr[i, :] = Xgen0[:, 2]
                Ed_tr[i, :] = Xgen0[:, 3]

                eventhappened = False

        ## Advance time
        stepsize = newstepsize
        t += stepsize

    # end of main stability loop


    ## Output
    if output:
        print '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b> 100## completed'
    else:
        print '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b'

    simulationtime = t0 - time()
    if output:
        print '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b> Simulation completed in %5.2f seconds\n' % simulationtime

    # Save only the first i elements
    Angles = Angles[:i, :]
    Speeds = Speeds[:i, :]
    Eq_tr = Eq_tr[:i, :]
    Ed_tr = Ed_tr[:i, :]

    Efd = Efd[:i, :]
    PM = PM[:i, :]

    Voltages = Voltages[:i, :]

    Stepsize = Stepsize[:i, :]
    Errest = Errest[:i, :]
    Time = Time[:i, :]

    ## Plot
    if plots:
        from pylab import close, figure, xlabel, ylabel, hold, plot, axis

        close('all')

        figure
        xlabel('Time [s]')
        ylabel('Angle [deg]')
        hold(True)
        plot(Time,Angles)
        axis([0, Time(-1), -1, 1])
        axis('auto y')

        figure
        xlabel('Time [s]')
        ylabel('Speed [pu]')
        hold(True)
        plot(Time,Speeds)
        axis([0, Time(-1), -1, 1])
        axis('auto y')

        figure
        xlabel('Time [s]')
        ylabel('Voltage [pu]')
        hold(True)
        plot(Time, abs(Voltages))
        axis([0, Time(-1), -1, 1])
        axis('auto y')

        figure
        xlabel('Time [s]')
        ylabel('Excitation voltage [pu]')
        hold(True)
        plot(Time, Efd)
        axis([0, Time(-1), -1, 1])
        axis('auto y')

        figure
        xlabel('Time [s]')
        ylabel('Turbine Power [pu]')
        hold(True)
        plot(Time, PM)
        axis([0, Time(-1), -1, 1])
        axis('auto y')

        figure
        hold(True)
        xlabel('Time [s]')
        ylabel('Step size')
        plot(Time, Stepsize, '-o')
        axis([0, Time(-1), -1, 1])
        axis('auto y')

    return Angles, Speeds, Eq_tr, Ed_tr, Efd, PM, Voltages, Stepsize, Errest, Time
