# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

"""Defines the PYPOWER case file format.

A PYPOWER case file is a Python file or MAT-file which defines the variables
baseMVA, bus, gen, branch, areas, and gencost. With the exception of baseMVA,
a scalar, each data variable is a matrix, where a row corresponds to a single
bus, branch, gen, etc. The format of the data is similar to the PTI format
described in

U{http://www.ee.washington.edu/research/pstca/formats/pti.txt}

PYPOWER Case Version Information:
=================================

The PYPOWER case file format defines the data matrices as individual variables.
Case files with OPF data also include an (unused) 'areas' variable.

See also L{idx_bus}, L{idx_brch}, L{idx_gen}, L{idx_area} and L{idx_cost}
regarding constants which can be used as named column indices for the data
matrices. Also described in the first three are additional results columns
that are added to the bus, branch and gen matrices by the power flow and OPF
solvers.

Bus Data Format
---------------

  1.   bus number (positive integer)
  2.   bus type
          - PQ bus          = 1
          - PV bus          = 2
          - reference bus   = 3
          - isolated bus    = 4
  3.   C{Pd}, real power demand (MW)
  4.   C{Qd}, reactive power demand (MVAr)
  5.   C{Gs}, shunt conductance (MW demanded at V = 1.0 p.u.)
  6.   C{Bs}, shunt susceptance (MVAr injected at V = 1.0 p.u.)
  7.   area number, (positive integer)
  8.   C{Vm}, voltage magnitude (p.u.)
  9.   C{Va}, voltage angle (degrees)
  10.  C{baseKV}, base voltage (kV)
  11.  C{zone}, loss zone (positive integer)
  12.  C{maxVm}, maximum voltage magnitude (p.u.)
  13.  C{minVm}, minimum voltage magnitude (p.u.)

Generator Data Format
---------------------

  1.   bus number
  2.   C{Pg}, real power output (MW)
  3.   C{Qg}, reactive power output (MVAr)
  4.   C{Qmax}, maximum reactive power output (MVAr)
  5.   C{Qmin}, minimum reactive power output (MVAr)
  6.   C{Vg}, voltage magnitude setpoint (p.u.)
  7.   C{mBase}, total MVA base of this machine, defaults to baseMVA
  8.   status,
           - C{>  0} - machine in service
           - C{<= 0} - machine out of service
  9.   C{Pmax}, maximum real power output (MW)
  10.  C{Pmin}, minimum real power output (MW)
  11.  C{Pc1}, lower real power output of PQ capability curve (MW)
  12.  C{Pc2}, upper real power output of PQ capability curve (MW)
  13.  C{Qc1min}, minimum reactive power output at Pc1 (MVAr)
  14.  C{Qc1max}, maximum reactive power output at Pc1 (MVAr)
  15.  C{Qc2min}, minimum reactive power output at Pc2 (MVAr)
  16.  C{Qc2max}, maximum reactive power output at Pc2 (MVAr)
  17.  ramp rate for load following/AGC (MW/min)
  18.  ramp rate for 10 minute reserves (MW)
  19.  ramp rate for 30 minute reserves (MW)
  20.  ramp rate for reactive power (2 sec timescale) (MVAr/min)
  21.  APF, area participation factor

Branch Data Format
------------------

  1.   C{f}, from bus number
  2.   C{t}, to bus number
  3.   C{r}, resistance (p.u.)
  4.   C{x}, reactance (p.u.)
  5.   C{b}, total line charging susceptance (p.u.)
  6.   C{rateA}, MVA rating A (long term rating)
  7.   C{rateB}, MVA rating B (short term rating)
  8.   C{rateC}, MVA rating C (emergency rating)
  9.   C{ratio}, transformer off nominal turns ratio ( = 0 for lines )
  10.  C{angle}, transformer phase shift angle (degrees), positive => delay
       (Gf, shunt conductance at from bus p.u.)
       (Bf, shunt susceptance at from bus p.u.)
       (Gt, shunt conductance at to bus p.u.)
       (Bt, shunt susceptance at to bus p.u.)
  11.  initial branch status, 1 - in service, 0 - out of service
  12.  minimum angle difference, angle(Vf) - angle(Vt) (degrees)
  13.  maximum angle difference, angle(Vf) - angle(Vt) (degrees)

Area Data Format
----------------

(this data is not used by PYPOWER and is no longer necessary for
version 2 case files with OPF data).
  1.   C{i}, area number
  2.   C{price_ref_bus}, reference bus for that area

Generator Cost Data Format
--------------------------

NOTE: If C{gen} has C{ng} rows, then the first C{ng} rows of gencost contain
the cost for active power produced by the corresponding generators.
If C{gencost} has 2*ng rows then rows C{ng+1} to C{2*ng} contain the reactive
power costs in the same format.

  1.   C{model}, 1 - piecewise linear, 2 - polynomial
  2.   C{startup}, startup cost in US dollars
  3.   C{shutdown}, shutdown cost in US dollars
  4.   C{N}, number of cost coefficients to follow for polynomial
       cost function, or number of data points for piecewise linear
  5.   and following, parameters defining total cost function C{f(p)},
       units of C{f} and C{p} are $/hr and MW (or MVAr), respectively.
       (MODEL = 1) : C{p0, f0, p1, f1, ..., pn, fn}
       where C{p0 < p1 < ... < pn} and the cost C{f(p)} is defined by
       the coordinates C{(p0,f0), (p1,f1), ..., (pn,fn)} of the
       end/break-points of the piecewise linear cost function
       (MODEL = 2) : C{cn, ..., c1, c0}
       C{n+1} coefficients of an C{n}-th order polynomial cost function,
       starting with highest order, where cost is
       C{f(p) = cn*p^n + ... + c1*p + c0}

@see: L{loadcase}, L{savecase}, L{idx_bus}, L{idx_brch}, L{idx_gen},
    L{idx_area} L{idx_cost}

@author: Ray Zimmerman (PSERC Cornell)
@author: Richard Lincoln
"""
