# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
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

"""Defines constants for named column indices to branch matrix.

See http://www.pserc.cornell.edu/matpower/ for more info.

Some examples of usage, after defining the constants using the line above,
are:

 branch(3, BR_STATUS) = 0;              % take branch 4 out of service
 Ploss = branch(:, PF) + branch(:, PT); % compute real power loss vector

The index, name and meaning of each column of the branch matrix is given
below:

columns 0-10 must be included in input matrix (in case file)
 0  F_BUS       f, from bus number
 1  T_BUS       t, to bus number
 2  BR_R        r, resistance (p.u.)
 3  BR_X        x, reactance (p.u.)
 4  BR_B        b, total line charging susceptance (p.u.)
 5  RATE_A      rateA, MVA rating A (long term rating)
 6  RATE_B      rateB, MVA rating B (short term rating)
 7  RATE_C      rateC, MVA rating C (emergency rating)
 8  TAP         ratio, transformer off nominal turns ratio
 9  SHIFT       angle, transformer phase shift angle (degrees)
 10 BR_STATUS   initial branch status, 1 - in service, 0 - out of service
 11 ANGMIN      minimum angle difference, angle(Vf) - angle(Vt) (degrees)
 12 ANGMAX      maximum angle difference, angle(Vf) - angle(Vt) (degrees)

columns 13-16 are added to matrix after power flow or OPF solution
they are typically not present in the input matrix
 13 PF          real power injected at "from" bus end (MW)
 14 QF          reactive power injected at "from" bus end (MVAr)
 15 PT          real power injected at "to" bus end (MW)
 16 QT          reactive power injected at "to" bus end (MVAr)

columns 17-18 are added to matrix after OPF solution
they are typically not present in the input matrix
                (assume OPF objective function has units, u)
 17 MU_SF       Kuhn-Tucker multiplier on MVA limit at "from" bus (u/MVA)
 18 MU_ST       Kuhn-Tucker multiplier on MVA limit at "to" bus (u/MVA)

columns 19-20 are added to matrix after SCOPF solution
they are typically not present in the input matrix
                (assume OPF objective function has units, u)
 19 MU_ANGMIN   Kuhn-Tucker multiplier lower angle difference limit
 20 MU_ANGMAX   Kuhn-Tucker multiplier upper angle difference limit
"""

# define the indices
F_BUS       = 0    # f, from bus number
T_BUS       = 1    # t, to bus number
BR_R        = 2    # r, resistance (p.u.)
BR_X        = 3    # x, reactance (p.u.)
BR_B        = 4    # b, total line charging susceptance (p.u.)
RATE_A      = 5    # rateA, MVA rating A (long term rating)
RATE_B      = 6    # rateB, MVA rating B (short term rating)
RATE_C      = 7    # rateC, MVA rating C (emergency rating)
TAP         = 8    # ratio, transformer off nominal turns ratio
SHIFT       = 9    # angle, transformer phase shift angle (degrees)
BR_STATUS   = 10   # initial branch status, 1 - in service, 0 - out of service
ANGMIN      = 11   # minimum angle difference, angle(Vf) - angle(Vt) (degrees)
ANGMAX      = 12   # maximum angle difference, angle(Vf) - angle(Vt) (degrees)

# included in power flow solution, not necessarily in input
PF          = 13   # real power injected at "from" bus end (MW)
QF          = 14   # reactive power injected at "from" bus end (MVAr)
PT          = 15   # real power injected at "to" bus end (MW)
QT          = 16   # reactive power injected at "to" bus end (MVAr)

# included in opf solution, not necessarily in input
# assume objective function has units, u
MU_SF       = 17   # Kuhn-Tucker multiplier on MVA limit at "from" bus (u/MVA)
MU_ST       = 18   # Kuhn-Tucker multiplier on MVA limit at "to" bus (u/MVA)
MU_ANGMIN   = 19   # Kuhn-Tucker multiplier lower angle difference limit
MU_ANGMAX   = 20   # Kuhn-Tucker multiplier upper angle difference limit
