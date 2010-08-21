# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2009-2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

""" Defines constants for named column indices to gen matrix.

See http://www.pserc.cornell.edu/matpower/ for more info.

Some examples of usage, after defining the constants using the line above,
are:

 Pg = gen(4, PG)   # get the real power output of generator 4
 gen(:, PMIN) = 0  # set to zero the minimum real power limit of all gens

The index, name and meaning of each column of the gen matrix is given
below:

columns 1-21 must be included in input matrix (in case file)
 1  GEN_BUS     bus number
 2  PG          Pg, real power output (MW)
 3  QG          Qg, reactive power output (MVAr)
 4  QMAX        Qmax, maximum reactive power output (MVAr)
 5  QMIN        Qmin, minimum reactive power output (MVAr)
 6  VG          Vg, voltage magnitude setpoint (p.u.)
 7  MBASE       mBase, total MVA base of machine, defaults to baseMVA
 8  GEN_STATUS  status, 1 - in service, 0 - out of service
 9  PMAX        Pmax, maximum real power output (MW)
 10 PMIN        Pmin, minimum real power output (MW)
 11 PC1         Pc1, lower real power output of PQ capability curve (MW)
 12 PC2         Pc2, upper real power output of PQ capability curve (MW)
 13 QC1MIN      Qc1min, minimum reactive power output at Pc1 (MVAr)
 14 QC1MAX      Qc1max, maximum reactive power output at Pc1 (MVAr)
 15 QC2MIN      Qc2min, minimum reactive power output at Pc2 (MVAr)
 16 QC2MAX      Qc2max, maximum reactive power output at Pc2 (MVAr)
 17 RAMP_AGC    ramp rate for load following/AGC (MW/min)
 18 RAMP_10     ramp rate for 10 minute reserves (MW)
 19 RAMP_30     ramp rate for 30 minute reserves (MW)
 20 RAMP_Q      ramp rate for reactive power (2 sec timescale) (MVAr/min)
 21 APF         area participation factor

columns 22-25 are added to matrix after OPF solution
they are typically not present in the input matrix
                (assume OPF objective function has units, u)
 22 MU_PMAX     Kuhn-Tucker multiplier on upper Pg limit (u/MW)
 23 MU_PMIN     Kuhn-Tucker multiplier on lower Pg limit (u/MW)
 24 MU_QMAX     Kuhn-Tucker multiplier on upper Qg limit (u/MVAr)
 25 MU_QMIN     Kuhn-Tucker multiplier on lower Qg limit (u/MVAr)
"""

# define the indices
GEN_BUS     = 1    # bus number
PG          = 2    # Pg, real power output (MW)
QG          = 3    # Qg, reactive power output (MVAr)
QMAX        = 4    # Qmax, maximum reactive power output at Pmin (MVAr)
QMIN        = 5    # Qmin, minimum reactive power output at Pmin (MVAr)
VG          = 6    # Vg, voltage magnitude setpoint (p.u.)
MBASE       = 7    # mBase, total MVA base of this machine, defaults to baseMVA
GEN_STATUS  = 8    # status, 1 - machine in service, 0 - machine out of service
PMAX        = 9    # Pmax, maximum real power output (MW)
PMIN        = 10   # Pmin, minimum real power output (MW)
PC1         = 11   # Pc1, lower real power output of PQ capability curve (MW)
PC2         = 12   # Pc2, upper real power output of PQ capability curve (MW)
QC1MIN      = 13   # Qc1min, minimum reactive power output at Pc1 (MVAr)
QC1MAX      = 14   # Qc1max, maximum reactive power output at Pc1 (MVAr)
QC2MIN      = 15   # Qc2min, minimum reactive power output at Pc2 (MVAr)
QC2MAX      = 16   # Qc2max, maximum reactive power output at Pc2 (MVAr)
RAMP_AGC    = 17   # ramp rate for load following/AGC (MW/min)
RAMP_10     = 18   # ramp rate for 10 minute reserves (MW)
RAMP_30     = 19   # ramp rate for 30 minute reserves (MW)
RAMP_Q      = 20   # ramp rate for reactive power (2 sec timescale) (MVAr/min)
APF         = 21   # area participation factor

# included in opf solution, not necessarily in input
# assume objective function has units, u
MU_PMAX     = 22   # Kuhn-Tucker multiplier on upper Pg limit (u/MW)
MU_PMIN     = 23   # Kuhn-Tucker multiplier on lower Pg limit (u/MW)
MU_QMAX     = 24   # Kuhn-Tucker multiplier on upper Qg limit (u/MVAr)
MU_QMIN     = 25   # Kuhn-Tucker multiplier on lower Qg limit (u/MVAr)

# Note: When a generator's PQ capability curve is not simply a box and the
# upper Qg limit is binding, the multiplier on this constraint is split into
# it's P and Q components and combined with the appropriate MU_Pxxx and
# MU_Qxxx values. Likewise for the lower Q limits.
