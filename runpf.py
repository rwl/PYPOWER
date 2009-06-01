# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

""" Runs a power flow.

    Ported from:
      D. Zimmerman, "runpf.m", MATPOWER, version 3.2,
      Power System Engineering Research Center (PSERC), 2004

    Enforcing of generator Q limits inspired by contributions from
    Mu Lin, Lincoln University, New Zealand.

    See http://www.pserc.cornell.edu/matpower/ for more info.
"""

def runpf(casename='case9', ppopt=ppoption, fname='', solvedcase=''):
    """ Runs a power flow.

        [baseMVA, bus, gen, branch, success, et] = ...
                runpf(casename, mpopt, fname, solvedcase)

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
