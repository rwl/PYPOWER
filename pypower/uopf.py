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

"""Solves combined unit decommitment / optimal power flow.
"""

from time import time

from numpy import flatnonzero as find

from ppoption import ppoption
from isload import isload
from totcost import totcost
from fairmax import fairmax
from opf import opf

from idx_bus import PD
from idx_gen import GEN_STATUS, PG, QG, PMIN, MU_PMIN


def uopf(baseMVA, bus, gen, gencost, branch, areas, ppopt=None):
    """Solves combined unit decommitment / optimal power flow.

    Solves a combined unit decommitment and optimal power flow for a single
    time period. Uses an algorithm similar to dynamic programming. It proceeds
    through a sequence of stages, where stage C{N} has C{N} generators shut
    down, starting with C{N=0}. In each stage, it forms a list of candidates
    (gens at their C{Pmin} limits) and computes the cost with each one of them
    shut down. It selects the least cost case as the starting point for the
    next stage, continuing until there are no more candidates to be shut down
    or no more improvement can be gained by shutting something down.
    If C{verbose} in ppopt (see L{ppoption} is C{true}, it prints progress
    info, if it is > 1 it prints the output of each individual opf.

    @see: L{opf}, L{runuopf}

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## default arguments
    if ppopt is None:
        ppopt = ppoption()

    ## options
    verbose = ppopt["VERBOSE"]
    if verbose:      ## turn down verbosity one level for calls to opf
        ppopt = ppoption(ppopt, VERBOSE=verbose - 1)

    ##-----  do combined unit commitment/optimal power flow  -----
    t0 = time()                                 ## start timer

    ## check for sum(Pmin) > total load, decommit as necessary
    on   = find( (gen[:, GEN_STATUS] > 0) & ~isload(gen) )   ## gens in service
    onld = find( (gen[:, GEN_STATUS] > 0) &  isload(gen) )   ## disp loads in serv
    load_capacity = sum(bus[:, PD]) - sum(gen[onld, PMIN])   ## total load capacity
    Pmin = gen[on, PMIN]
    while sum(Pmin) > load_capacity:
        ## shut down most expensive unit
        avgPmincost = totcost(gencost[on, :], Pmin) / Pmin
        _, i = fairmax(avgPmincost)   ## pick one with max avg cost at Pmin
        i = on[i]                     ## convert to generator index

        if verbose:
            print 'Shutting down generator %d so all Pmin limits can be satisfied.\n' % i

        ## set generation to zero
        gen[i, [PG, QG, GEN_STATUS]] = 0

        ## update minimum gen capacity
        on  = find( (gen[:, GEN_STATUS] > 0) & ~isload(gen) )   ## gens in service
        Pmin = gen[on, PMIN]

    ## run initial opf
    bus, gen, branch, f, success, _, _ = opf(baseMVA, bus, gen, branch,
                                   areas, gencost, ppopt)

    ## best case so far
    bus1 = bus.copy()
    gen1 = gen.copy()
    branch1 = branch.copy()
    success1 = success
    f1 = f

    ## best case for this stage (ie. with n gens shut down, n=0,1,2 ...)
    bus0 = bus1.copy()
    gen0 = gen1.copy()
    branch0 = branch1.copy()
    success0 = success1
    f0 = f1

    while True:
        ## get candidates for shutdown
        candidates = find((gen0[:, MU_PMIN] > 0) & (gen0[:, PMIN] > 0))
        if len(candidates) == 0:
            break

        ## do not check for further decommitment unless we
        ##  see something better during this stage
        done = True

        for k in candidates:
            ## start with best for this stage
            gen = gen0.copy()

            ## shut down gen k
            gen[k, [PG, QG, GEN_STATUS]] = 0

            ## run opf
            bus, gen, branch, f, success, _, _ = opf(baseMVA, bus0, gen, branch0,
                                           areas, gencost, ppopt)

            ## something better?
            if success and (f < f1):
                bus1 = bus.copy()
                gen1 = gen.copy()
                branch1 = branch.copy()
                success1 = success
                f1 = f
                k1 = k
                done = False   ## make sure we check for further decommitment

        if done:
            ## decommits at this stage did not help, so let's quit
            break
        else:
            ## shutting something else down helps, so let's keep going
            if verbose:
                print 'Shutting down generator %d.\n' % k1

            bus0 = bus1.copy()
            gen0 = gen1.copy()
            branch0 = branch1.copy()
            success0 = success1
            f0 = f1

    ## compute elapsed time
    et = time() - t0

    return bus0, gen0, branch0, f0, success0, et
