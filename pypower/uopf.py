# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Solves combined unit decommitment / optimal power flow.
"""

from time import time

from copy import deepcopy

from numpy import flatnonzero as find

from pypower.opf_args import opf_args2
from pypower.ppoption import ppoption
from pypower.isload import isload
from pypower.totcost import totcost
from pypower.fairmax import fairmax
from pypower.opf import opf

from pypower.idx_bus import PD
from pypower.idx_gen import GEN_STATUS, PG, QG, PMIN, MU_PMIN


def uopf(*args):
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
    """
    ##----- initialization -----
    t0 = time()                                 ## start timer

    ## process input arguments
    ppc, ppopt = opf_args2(*args)

    ## options
    verbose = ppopt["VERBOSE"]
    if verbose:      ## turn down verbosity one level for calls to opf
        ppopt = ppoption(ppopt, VERBOSE=verbose - 1)

    ##-----  do combined unit commitment/optimal power flow  -----

    ## check for sum(Pmin) > total load, decommit as necessary
    on   = find( (ppc["gen"][:, GEN_STATUS] > 0) & ~isload(ppc["gen"]) )   ## gens in service
    onld = find( (ppc["gen"][:, GEN_STATUS] > 0) &  isload(ppc["gen"]) )   ## disp loads in serv
    load_capacity = sum(ppc["bus"][:, PD]) - sum(ppc["gen"][onld, PMIN])   ## total load capacity
    Pmin = ppc["gen"][on, PMIN]
    while sum(Pmin) > load_capacity:
        ## shut down most expensive unit
        avgPmincost = totcost(ppc["gencost"][on, :], Pmin) / Pmin
        _, i = fairmax(avgPmincost)   ## pick one with max avg cost at Pmin
        i = on[i]                     ## convert to generator index

        if verbose:
            print('Shutting down generator %d so all Pmin limits can be satisfied.\n' % i)

        ## set generation to zero
        ppc["gen"][i, [PG, QG, GEN_STATUS]] = 0

        ## update minimum gen capacity
        on  = find( (ppc["gen"][:, GEN_STATUS] > 0) & ~isload(ppc["gen"]) )   ## gens in service
        Pmin = ppc["gen"][on, PMIN]

    ## run initial opf
    results = opf(ppc, ppopt)

    ## best case so far
    results1 = deepcopy(results)

    ## best case for this stage (ie. with n gens shut down, n=0,1,2 ...)
    results0 = deepcopy(results1)
    ppc["bus"] = results0["bus"].copy()     ## use these V as starting point for OPF

    while True:
        ## get candidates for shutdown
        candidates = find((results0["gen"][:, MU_PMIN] > 0) & (results0["gen"][:, PMIN] > 0))
        if len(candidates) == 0:
            break

        ## do not check for further decommitment unless we
        ##  see something better during this stage
        done = True

        for k in candidates:
            ## start with best for this stage
            ppc["gen"] = results0["gen"].copy()

            ## shut down gen k
            ppc["gen"][k, [PG, QG, GEN_STATUS]] = 0

            ## run opf
            results = opf(ppc, ppopt)

            ## something better?
            if results['success'] and (results["f"] < results1["f"]):
                results1 = deepcopy(results)
                k1 = k
                done = False   ## make sure we check for further decommitment

        if done:
            ## decommits at this stage did not help, so let's quit
            break
        else:
            ## shutting something else down helps, so let's keep going
            if verbose:
                print('Shutting down generator %d.\n' % k1)

            results0 = deepcopy(results1)
            ppc["bus"] = results0["bus"].copy()     ## use these V as starting point for OPF

    ## compute elapsed time
    et = time() - t0

    ## finish preparing output
    results0['et'] = et

    return results0
