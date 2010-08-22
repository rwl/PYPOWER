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

from bustypes import bustypes
from ext2int import ext2int
from loadcase import loadcase

def runpf(casename='case9', ppopt=None, fname='', solvedcase=''):
    """ Runs a power flow.

    [baseMVA, bus, gen, branch, success, et] = ...
            runpf(casename, ppopt, fname, solvedcase)

    Runs a power flow (full AC Newton's method by default) and optionally
    returns the solved values in the data matrices, a flag which is true if
    the algorithm was successful in finding a solution, and the elapsed
    time in seconds. All input arguments are optional. If casename is
    provided it specifies the name of the input data file or struct
    containing the power flow data. The default value is 'case9'.

    If the ppopt is provided it overrides the default PYPOWER options
    vector and can be used to specify the solution algorithm and output
    options among other things. If the 3rd argument is given the pretty
    printed output will be appended to the file whose name is given in
    fname. If solvedcase is specified the solved case will be written to a
    case file in MATPOWER format with the specified name. If solvedcase
    ends with '.mat' it saves the case as a MAT-file otherwise it saves it
    as an M-file.

    If the ENFORCE_Q_LIMS options is set to true (default is false) then if
    any generator reactive power limit is violated after running the AC
    power flow, the corresponding bus is converted to a PQ bus, with Qg at
    the limit, and the case is re-run. The voltage magnitude at the bus
    will deviate from the specified value in order to satisfy the reactive
    power limit. If the reference bus is converted to PQ, the first
    remaining PV bus will be used as the slack bus for the next iteration.
    This may result in the real power output at this generator being
    slightly off from the specified values.
    """

    # options
    verbose = ppopt["VERBOSE"]
    qlim = ppopt["ENFORCE_Q_LIMS"]
    dc = ppopt["PF_DC"]

    # read data & convert to internal bus numbering
    baseMVA, bus, gen, branch = loadcase(casename)
    i2e, bus, gen, branch = ext2int(bus, gen, branch)

    # get bus index lists of each type of bus
    ref, pv, pq = bustypes(bus, gen)

    return baseMVA, bus, gen, branch, success, et
