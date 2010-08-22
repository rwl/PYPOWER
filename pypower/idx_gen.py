# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

Some examples of usage, after defining the constants using the line above,
are:

 Pg = gen(3, PG)   # get the real power output of generator 4
 gen(:, PMIN) = 0  # set to zero the minimum real power limit of all gens

The index, name and meaning of each column of the gen matrix is given
below:

columns 0-20 must be included in input matrix (in case file)
 0  GEN_BUS     bus number
 1  PG          Pg, real power output (MW)
 2  QG          Qg, reactive power output (MVAr)
 3  QMAX        Qmax, maximum reactive power output (MVAr)
 4  QMIN        Qmin, minimum reactive power output (MVAr)
 5  VG          Vg, voltage magnitude setpoint (p.u.)
 6  MBASE       mBase, total MVA base of machine, defaults to baseMVA
 7  GEN_STATUS  status, 1 - in service, 0 - out of service
 8  PMAX        Pmax, maximum real power output (MW)
 9  PMIN        Pmin, minimum real power output (MW)
 10 PC1         Pc1, lower real power output of PQ capability curve (MW)
 11 PC2         Pc2, upper real power output of PQ capability curve (MW)
 12 QC1MIN      Qc1min, minimum reactive power output at Pc1 (MVAr)
 13 QC1MAX      Qc1max, maximum reactive power output at Pc1 (MVAr)
 14 QC2MIN      Qc2min, minimum reactive power output at Pc2 (MVAr)
 15 QC2MAX      Qc2max, maximum reactive power output at Pc2 (MVAr)
 16 RAMP_AGC    ramp rate for load following/AGC (MW/min)
 17 RAMP_10     ramp rate for 10 minute reserves (MW)
 18 RAMP_30     ramp rate for 30 minute reserves (MW)
 19 RAMP_Q      ramp rate for reactive power (2 sec timescale) (MVAr/min)
 20 APF         area participation factor

columns 21-24 are added to matrix after OPF solution
they are typically not present in the input matrix
                (assume OPF objective function has units, u)
 21 MU_PMAX     Kuhn-Tucker multiplier on upper Pg limit (u/MW)
 22 MU_PMIN     Kuhn-Tucker multiplier on lower Pg limit (u/MW)
 23 MU_QMAX     Kuhn-Tucker multiplier on upper Qg limit (u/MVAr)
 24 MU_QMIN     Kuhn-Tucker multiplier on lower Qg limit (u/MVAr)

@see: U{http://www.pserc.cornell.edu/matpower/}
"""

# define the indices
GEN_BUS     = 0    # bus number
PG          = 1    # Pg, real power output (MW)
QG          = 2    # Qg, reactive power output (MVAr)
QMAX        = 3    # Qmax, maximum reactive power output at Pmin (MVAr)
QMIN        = 4    # Qmin, minimum reactive power output at Pmin (MVAr)
VG          = 5    # Vg, voltage magnitude setpoint (p.u.)
MBASE       = 6    # mBase, total MVA base of this machine, defaults to baseMVA
GEN_STATUS  = 7    # status, 1 - machine in service, 0 - machine out of service
PMAX        = 8    # Pmax, maximum real power output (MW)
PMIN        = 9    # Pmin, minimum real power output (MW)
PC1         = 10   # Pc1, lower real power output of PQ capability curve (MW)
PC2         = 11   # Pc2, upper real power output of PQ capability curve (MW)
QC1MIN      = 12   # Qc1min, minimum reactive power output at Pc1 (MVAr)
QC1MAX      = 13   # Qc1max, maximum reactive power output at Pc1 (MVAr)
QC2MIN      = 14   # Qc2min, minimum reactive power output at Pc2 (MVAr)
QC2MAX      = 15   # Qc2max, maximum reactive power output at Pc2 (MVAr)
RAMP_AGC    = 16   # ramp rate for load following/AGC (MW/min)
RAMP_10     = 17   # ramp rate for 10 minute reserves (MW)
RAMP_30     = 18   # ramp rate for 30 minute reserves (MW)
RAMP_Q      = 19   # ramp rate for reactive power (2 sec timescale) (MVAr/min)
APF         = 20   # area participation factor

# included in opf solution, not necessarily in input
# assume objective function has units, u
MU_PMAX     = 21   # Kuhn-Tucker multiplier on upper Pg limit (u/MW)
MU_PMIN     = 22   # Kuhn-Tucker multiplier on lower Pg limit (u/MW)
MU_QMAX     = 23   # Kuhn-Tucker multiplier on upper Qg limit (u/MVAr)
MU_QMIN     = 24   # Kuhn-Tucker multiplier on lower Qg limit (u/MVAr)

# Note: When a generator's PQ capability curve is not simply a box and the
# upper Qg limit is binding, the multiplier on this constraint is split into
# it's P and Q components and combined with the appropriate MU_Pxxx and
# MU_Qxxx values. Likewise for the lower Q limits.
