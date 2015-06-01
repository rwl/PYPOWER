# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Defines constants for named column indices to dcline matrix.

Some examples of usage, after defining the constants using the line above,
are:

  ppc.dcline(4, c['BR_STATUS']) = 0          take branch 4 out of service

The index, name and meaning of each column of the branch matrix is given
below:

columns 1-17 must be included in input matrix (in case file)
 1  F_BUS       f, "from" bus number
 2  T_BUS       t,  "to"  bus number
 3  BR_STATUS   initial branch status, 1 - in service, 0 - out of service
 4  PF          MW flow at "from" bus ("from" -> "to")
 5  PT          MW flow at  "to"  bus ("from" -> "to")
 6  QF          MVAr injection at "from" bus ("from" -> "to")
 7  QT          MVAr injection at  "to"  bus ("from" -> "to")
 8  VF          voltage setpoint at "from" bus (p.u.)
 9  VT          voltage setpoint at  "to"  bus (p.u.)
10  PMIN        lower limit on PF (MW flow at "from" end)
11  PMAX        upper limit on PF (MW flow at "from" end)
12  QMINF       lower limit on MVAr injection at "from" bus
13  QMAXF       upper limit on MVAr injection at "from" bus
14  QMINT       lower limit on MVAr injection at  "to"  bus
15  QMAXT       upper limit on MVAr injection at  "to"  bus
16  LOSS0       constant term of linear loss function (MW)
17  LOSS1       linear term of linear loss function (MW/MW)
                (loss = LOSS0 + LOSS1 * PF)

columns 18-23 are added to matrix after OPF solution
they are typically not present in the input matrix
                (assume OPF objective function has units, u)
18  MU_PMIN     Kuhn-Tucker multiplier on lower flow lim at "from" bus (u/MW)
19  MU_PMAX     Kuhn-Tucker multiplier on upper flow lim at "from" bus (u/MW)
20  MU_QMINF    Kuhn-Tucker multiplier on lower VAr lim at "from" bus (u/MVAr)
21  MU_QMAXF    Kuhn-Tucker multiplier on upper VAr lim at "from" bus (u/MVAr)
22  MU_QMINT    Kuhn-Tucker multiplier on lower VAr lim at  "to"  bus (u/MVAr)
23  MU_QMAXT    Kuhn-Tucker multiplier on upper VAr lim at  "to"  bus (u/MVAr)

@see: L{toggle_dcline}
"""

## define the indices
c = {
    'F_BUS':     0,     ## f, "from" bus number
    'T_BUS':     1,     ## t,  "to"  bus number
    'BR_STATUS': 2,     ## initial branch status, 1 - in service, 0 - out of service
    'PF':        3,     ## MW flow at "from" bus ("from" -> "to")
    'PT':        4,     ## MW flow at  "to"  bus ("from" -> "to")
    'QF':        5,     ## MVAr injection at "from" bus ("from" -> "to")
    'QT':        6,     ## MVAr injection at  "to"  bus ("from" -> "to")
    'VF':        7,     ## voltage setpoint at "from" bus (p.u.)
    'VT':        8,     ## voltage setpoint at  "to"  bus (p.u.)
    'PMIN':      9,     ## lower limit on PF (MW flow at "from" end)
    'PMAX':     10,     ## upper limit on PF (MW flow at "from" end)
    'QMINF':    11,     ## lower limit on MVAr injection at "from" bus
    'QMAXF':    12,     ## upper limit on MVAr injection at "from" bus
    'QMINT':    13,     ## lower limit on MVAr injection at  "to"  bus
    'QMAXT':    14,     ## upper limit on MVAr injection at  "to"  bus
    'LOSS0':    15,     ## constant term of linear loss function (MW)
    'LOSS1':    16,     ## linear term of linear loss function (MW)
    'MU_PMIN':  17,     ## Kuhn-Tucker multiplier on lower flow lim at "from" bus (u/MW)
    'MU_PMAX':  18,     ## Kuhn-Tucker multiplier on upper flow lim at "from" bus (u/MW)
    'MU_QMINF': 19,     ## Kuhn-Tucker multiplier on lower VAr lim at "from" bus (u/MVAr)
    'MU_QMAXF': 20,     ## Kuhn-Tucker multiplier on upper VAr lim at "from" bus (u/MVAr)
    'MU_QMINT': 21,     ## Kuhn-Tucker multiplier on lower VAr lim at  "to"  bus (u/MVAr)
    'MU_QMAXT': 22      ## Kuhn-Tucker multiplier on upper VAr lim at  "to"  bus (u/MVAr)
}
