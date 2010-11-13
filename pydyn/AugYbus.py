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

from numpy import zeros
from scipy.sparse.linalg import splu

from pypower.makeYbus import makeYbus

def AugYbus(baseMVA, bus, branch, xd_tr, gbus, P, Q, U0):
    """ Constructs augmented bus admittance matrix Ybus.

    @param baseMVA: power base
    @param bus: bus data
    @param branch: branch data
    @param xd_tr: d component of transient reactance
    @param gbus: generator buses
    @param P: load active power
    @param Q: load reactive power
    @param U0: steady-state bus voltages
    @return: factorised augmented bus admittance matrix

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    # Calculate bus admittance matrix
    Ybus, _, _ = makeYbus(baseMVA, bus, branch)

    # Calculate equivalent load admittance
    yload = (P - 1j * Q) / (abs(U0)**2)

    # Calculate equivalent generator admittance
    ygen = zeros(Ybus.shape[0])
    ygen[gbus] = 1 / (1j * xd_tr)

    # Add equivalent load and generator admittance to Ybus matrix
    for i in range(Ybus.shape[0]):
        Ybus[i, i] = Ybus[i, i] + ygen[i] + yload[i]

    # Factorise
    return splu(Ybus)
