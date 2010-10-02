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

from numpy import zeros, arange, exp

def SolveNetwork(Xgen, Pgen, invYbus, gbus, gentype):
    """ Solve the network.

    @param Xgen: state variables of generators
    @param Pgen: parameters of generators
    @param Ybus_lu: factorised augmented bus admittance matrix
    @param gbus: generator buses
    @param gentype: generator models
    @return: bus voltages

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Init
    ngen = len(gbus)
    Igen = zeros(ngen)

    s = len(invYbus)

    Ig = zeros(s,1)
    d = arange(len(gentype))

    ## Define generator types
    type1 = d[gentype == 1]
    type2 = d[gentype == 2]

    ## Generator type 1: classical model
    delta = Xgen[type1, 0]
    Eq_tr = Xgen[type1, 2]

    xd_tr = Pgen[type1, 6]

    # Calculate generator currents
    Igen[type1] = (Eq_tr * exp(1j * delta)) / (1j *xd_tr)

    ## Generator type 2: 4th order model
    delta = Xgen[type2, 0]
    Eq_tr = Xgen[type2, 2]
    Ed_tr = Xgen[type2, 3]

    xd_tr = Pgen[type2, 7]

    # Calculate generator currents
    Igen[type2] = (Eq_tr + 1j * Ed_tr) * exp(1j * delta) / (1j * xd_tr)  # Padiyar, p.417.

    ## Calculations
    # Generator currents
    Ig[gbus] = Igen

    # Calculate network voltages: U = Y/Ig
    U = invYbus.solve(Ig)

    return U
