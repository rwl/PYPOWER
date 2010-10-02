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
