# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

import logging

from numpy import zeros, ones
from numpy import flatnonzero as find

from scipy.sparse import csr_matrix

from isload import isload

from idx_bus import PD, QD, BUS_AREA, BUS_I
from idx_gen import QMAX, QMIN, GEN_BUS, GEN_STATUS, PMIN

logger = logging.getLogger(__name__)

def total_load(bus, gen, load_zone, which_type='BOTH'):
    """ Returns vector of total load in each load zone.

    @param bus: standard BUS matrix with nb rows, where the fixed active
        and reactive loads are specified in columns PD and QD
    @param gen: (optional) standard GEN matrix with ng rows, where the
        dispatchable loads are specified by columns PG, QG, PMIN,
        QMIN and QMAX (in rows for which ISLOAD(GEN) returns true).
        If GEN is empty, it assumes there are no dispatchable loads.
    @param load_zone: (optional) nb element vector where the value of
        each element is either zero or the index of the load zone
        to which the corresponding bus belongs. If LOAD_ZONE(b) = k
        then the loads at bus b will added to the values of PD(k) and
        QD(k). If LOAD_ZONE is empty, the default is defined as the areas
        specified in the BUS matrix, i.e. LOAD_ZONE = BUS(:, BUS_AREA)
        and load will have dimension = MAX(BUS(:, BUS_AREA)). If
        LOAD_ZONE = 'all', the result is a scalar with the total system
        load.
    @param whic_type: (default is 'BOTH' if GEN is provided, else 'FIXED')
        'FIXED'        : sum only fixed loads
        'DISPATCHABLE' : sum only dispatchable loads
        'BOTH'         : sum both fixed and dispatchable loads

    @see: L{scale_load}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    nb = bus.shape[0]       ## number of buses

    ## fill out and check which_type
    if len(gen) == 0:
        which_type = 'FIXED'

    if len(which_type) == 0 and len(gen) > 0:
        which_type = 'BOTH'     ## 'FIXED', 'DISPATCHABLE' or 'BOTH'

    if which_type[0] != 'F' and which_type[0] != 'D' and which_type[0] != 'B':
        logger.error("total_load: which_type should be 'FIXED, 'DISPATCHABLE or 'BOTH'")

    want_Q      = True
    want_fixed  = (which_type[0] == 'B' | which_type[0] == 'F')
    want_disp   = (which_type[0] == 'B' | which_type[0] == 'D')

    ## initialize load_zone
    if isinstance(load_zone, basestring) & load_zone == 'all':
        load_zone = ones(nb)           ## make a single zone of all buses
    elif len(load_zone) == 0:
        load_zone = bus[:, BUS_AREA]   ## use areas defined in bus data as zones

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
        is_ld = isload(gen) & gen[:, GEN_STATUS] > 0
        ld = find(is_ld)

        ## create map of external bus numbers to bus indices
        i2e = bus[:, BUS_I]
        e2i = csr_matrix((max(i2e), 1))
        e2i[i2e] = range(nb)

        Cld = csr_matrix((is_ld, (e2i[gen[: GEN_BUS]], range(ng))), (nb, ng))
        Pdd = -Cld * gen[:, PMIN]      ## real power
        if want_Q:
            Q = zeros(ng)
            Q[ld] = (gen[ld, QMIN] == 0) * gen[ld, QMAX] + \
                    (gen(ld, QMAX) == 0) * gen[ld, QMIN]
            Qdd = -Cld * Q             ## reactive power
    else:
        Pdd = zeros(nb)
        if want_Q:
            Qdd = zeros(nb)

    ## compute load sums
    Pd = zeros(nz)
    if want_Q:
        Qd = zeros(nz)

    for k in range(nz):
        idx = find( load_zone == k )
        Pd[k] = sum(Pdf[idx]) + sum(Pdd[idx])
        if want_Q:
            Qd[k] = sum(Qdf[idx]) + sum(Qdd[idx])

    return Pd, Qd
