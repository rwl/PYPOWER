# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Total load in each load zone.
"""

from sys import stderr

from numpy import zeros, ones, array, arange
from numpy import flatnonzero as find

from scipy.sparse import csr_matrix as sparse

from pypower._compat import PY2
from pypower.isload import isload

from pypower.idx_bus import PD, QD, BUS_AREA, BUS_I
from pypower.idx_gen import QMAX, QMIN, GEN_BUS, GEN_STATUS, PMIN


if not PY2:
    basestring = str


def total_load(bus, gen=None, load_zone=None, which_type=None):
    """Returns vector of total load in each load zone.

    @param bus: standard C{bus} matrix with C{nb} rows, where the fixed active
    and reactive loads are specified in columns C{PD} and C{QD}

    @param gen: (optional) standard C{gen} matrix with C{ng} rows, where the
    dispatchable loads are specified by columns C{PG}, C{QG}, C{PMIN},
    C{QMIN} and C{QMAX} (in rows for which C{isload(GEN)} returns C{True}).
    If C{gen} is empty, it assumes there are no dispatchable loads.

    @param load_zone: (optional) C{nb} element vector where the value of
    each element is either zero or the index of the load zone
    to which the corresponding bus belongs. If C{load_zone(b) = k}
    then the loads at bus C{b} will added to the values of C{Pd[k]} and
    C{Qd[k]}. If C{load_zone} is empty, the default is defined as the areas
    specified in the C{bus} matrix, i.e. C{load_zone =  bus[:, BUS_AREA]}
    and load will have dimension C{= max(bus[:, BUS_AREA])}. If
    C{load_zone = 'all'}, the result is a scalar with the total system
    load.

    @param which_type: (default is 'BOTH' if C{gen} is provided, else 'FIXED')
        - 'FIXED'        : sum only fixed loads
        - 'DISPATCHABLE' : sum only dispatchable loads
        - 'BOTH'         : sum both fixed and dispatchable loads

    @see: L{scale_load}

    @author: Ray Zimmerman (PSERC Cornell)
    """
    nb = bus.shape[0]       ## number of buses

    if gen is None:
        gen = array([])
    if load_zone is None:
        load_zone = array([], int)

    ## fill out and check which_type
    if len(gen) == 0:
        which_type = 'FIXED'

    if (which_type == None) and (len(gen) > 0):
        which_type = 'BOTH'     ## 'FIXED', 'DISPATCHABLE' or 'BOTH'

    if (which_type[0] != 'F') and (which_type[0] != 'D') and (which_type[0] != 'B'):
        stderr.write("total_load: which_type should be 'FIXED, 'DISPATCHABLE or 'BOTH'\n")

    want_Q      = True
    want_fixed  = (which_type[0] == 'B') | (which_type[0] == 'F')
    want_disp   = (which_type[0] == 'B') | (which_type[0] == 'D')

    ## initialize load_zone
    if isinstance(load_zone, basestring) and (load_zone == 'all'):
        load_zone = ones(nb, int)                  ## make a single zone of all buses
    elif len(load_zone) == 0:
        load_zone = bus[:, BUS_AREA].astype(int)   ## use areas defined in bus data as zones

    nz = max(load_zone)    ## number of load zones

    ## fixed load at each bus, & initialize dispatchable
    if want_fixed:
        Pdf = bus[:, PD]       ## real power
        if want_Q:
            Qdf = bus[:, QD]   ## reactive power
    else:
        Pdf = zeros(nb)     ## real power
        if want_Q:
            Qdf = zeros(nb) ## reactive power

    ## dispatchable load at each bus
    if want_disp:            ## need dispatchable
        ng = gen.shape[0]
        is_ld = isload(gen) & (gen[:, GEN_STATUS] > 0)
        ld = find(is_ld)

        ## create map of external bus numbers to bus indices
        i2e = bus[:, BUS_I].astype(int)
        e2i = zeros(max(i2e) + 1)
        e2i[i2e] = arange(nb)

        gbus = gen[:, GEN_BUS].astype(int)
        Cld = sparse((is_ld, (e2i[gbus], arange(ng))), (nb, ng))
        Pdd = -Cld * gen[:, PMIN]      ## real power
        if want_Q:
            Q = zeros(ng)
            Q[ld] = (gen[ld, QMIN] == 0) * gen[ld, QMAX] + \
                    (gen[ld, QMAX] == 0) * gen[ld, QMIN]
            Qdd = -Cld * Q             ## reactive power
    else:
        Pdd = zeros(nb)
        if want_Q:
            Qdd = zeros(nb)

    ## compute load sums
    Pd = zeros(nz)
    if want_Q:
        Qd = zeros(nz)

    for k in range(1, nz + 1):
        idx = find(load_zone == k)
        Pd[k - 1] = sum(Pdf[idx]) + sum(Pdd[idx])
        if want_Q:
            Qd[k - 1] = sum(Qdf[idx]) + sum(Qdd[idx])

    return Pd, Qd
