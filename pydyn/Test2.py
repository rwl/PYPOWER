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

from pylab import close, figure, xlabel, ylabel, hold, plot, axis, legend

from pydyn.Pdoption import Pdoption
from pydyn.rundyn import rundyn

def Test2():
    """ test script """
    pdopt = Pdoption
    pdopt[4] = 0     # no progress info
    pdopt[5] = 0     # no plots

    ## Fehlberg 1
    # Set options
    pdopt[0] = 3     # Runge-Kutta Fehlberg
    pdopt[1] = 1e-4  # tol = 1e-4
    pdopt[2] = 1e-4  # minimum step size = 1e-4

    # Run dynamic simulation
    print '> Runge-Kutta Fehlberg...'
    Angles1, Speeds, Eq_tr, Ed_tr, Efd, PM, Voltages, Stepsize1, Errest, Time1 = \
        rundyn('casestagg', 'casestaggdyn', 'staggevent', pdopt)

    ## Fehlberg 2
    # Set options
    pdopt[0] = 3     # Runge-Kutta Fehlberg
    pdopt[1] = 1e-3  # tol = 1e-3
    pdopt[2] = 1e-4  # minimum step size = 1e-4

    # Run dynamic simulation
    print 'Done.\n> Runge-Kutta Fehlberg...'
    Angles2, Speeds, Eq_tr, Ed_tr, Efd, PM, Voltages, Stepsize2, Errest, Time2 = \
        rundyn('casestagg', 'casestaggdyn', 'staggevent', pdopt)
    print 'Done.\n'

    ## Plots
    # Plot angles
    # close all
    figure
    hold(True)
    xlabel('Time [s]')
    ylabel('Generator angles [deg]')
    p1 = plot(Time1,Angles1,'b')
    p2 = plot(Time2,Angles2,'r--')
    Group1 = hggroup
    Group2 = hggroup
    set(p1,'Parent',Group1)
    set(p2,'Parent',Group2)
    set(get(get(Group1,'Annotation'), 'LegendInformation'),
        'IconDisplayStyle','on')
    set(get(get(Group2,'Annotation'), 'LegendInformation'),
        'IconDisplayStyle','on')
    legend('RK Fehlberg 1e-4','RK Fehlberg 1e-3')
    axis([0, Time1(-1), -1, 1])
    axis('auto y')

    figure
    hold(True)
    xlabel('Time [s]')
    ylabel('Step size')
    p1 = plot(Time1, Stepsize1, 'b')
    p2 = plot(Time2, Stepsize2, 'r--')
    Group1 = hggroup
    Group2 = hggroup
    set(p1,'Parent',Group1)
    set(p2,'Parent',Group2)
    set(get(get(Group1,'Annotation'),'LegendInformation'),
        'IconDisplayStyle','on')
    set(get(get(Group2,'Annotation'),'LegendInformation'),
        'IconDisplayStyle','on')
    legend('RK Fehlberg 1e-4','RK Fehlberg 1e-3')
    axis([0, Time1(-1), -1, 1])
    axis('auto y')
