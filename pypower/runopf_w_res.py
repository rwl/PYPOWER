# Copyright (C) 2008-2011 Power System Engineering Research Center
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

"""Runs an optimal power flow with fixed zonal reserves.
"""

from pypower.loadcase import loadcase
from pypower.toggle_reserves import toggle_reserves
from pypower.runopf import runopf


def runopf_w_res(*args):
    """Runs an optimal power flow with fixed zonal reserves.

    Runs an optimal power flow with the addition of reserve requirements
    specified as a set of fixed zonal reserves. See L{runopf} for a
    description of the input and output arguments, which are the same,
    with the exception that the case file or dict C{casedata} must define
    a 'reserves' field, which is a dict with the following fields:
        - C{zones}   C{nrz x ng}, C{zone(i, j) = 1}, if gen C{j} belongs
        to zone C{i} 0, otherwise
        - C{req}     C{nrz x 1}, zonal reserve requirement in MW
        - C{cost}    (C{ng} or C{ngr}) C{x 1}, cost of reserves in $/MW
        - C{qty}     (C{ng} or C{ngr}) C{x 1}, max quantity of reserves
        in MW (optional)
    where C{nrz} is the number of reserve zones and C{ngr} is the number of
    generators belonging to at least one reserve zone and C{ng} is the total
    number of generators.

    In addition to the normal OPF output, the C{results} dict contains a
    new 'reserves' field with the following fields, in addition to those
    provided in the input:
        - C{R}       - C{ng x 1}, reserves provided by each gen in MW
        - C{Rmin}    - C{ng x 1}, lower limit on reserves provided by
        each gen, (MW)
        - C{Rmax}    - C{ng x 1}, upper limit on reserves provided by
        each gen, (MW)
        - C{mu.l}    - C{ng x 1}, shadow price on reserve lower limit, ($/MW)
        - C{mu.u}    - C{ng x 1}, shadow price on reserve upper limit, ($/MW)
        - C{mu.Pmax} - C{ng x 1}, shadow price on C{Pg + R <= Pmax}
        constraint, ($/MW)
        - C{prc}     - C{ng x 1}, reserve price for each gen equal to
        maximum of the shadow prices on the zonal requirement constraint
        for each zone the generator belongs to

    See L{t.t_case30_userfcns} for an example case file with fixed reserves,
    and L{toggle_reserves} for the implementation.

    Calling syntax options::
        results = runopf_w_res(casedata)
        results = runopf_w_res(casedata, ppopt)
        results = runopf_w_res(casedata, ppopt, fname)
        results = runopf_w_res(casedata, [popt, fname, solvedcase)
        results, success = runopf_w_res(...)

    Example::
        results = runopf_w_res('t_case30_userfcns')

    @see: L{runopf}, L{toggle_reserves}, L{t.t_case30_userfcns}
    """
    ppc = loadcase(args[0])
    ppc = toggle_reserves(ppc, 'on')

    r = runopf(ppc, *args[1:])
    r = toggle_reserves(r, 'off')

    return r
