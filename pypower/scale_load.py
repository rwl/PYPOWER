# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

from sys import stderr

from numpy import array, zeros, arange, in1d, ix_
from numpy import flatnonzero as find

from scipy.sparse import csr_matrix as sparse

from isload import isload

from idx_bus import PD, QD, BUS_AREA, BUS_I
from idx_gen import PG, QG, QMAX, QMIN, GEN_BUS, GEN_STATUS, PMIN


def scale_load(load, bus, gen=None, load_zone=None, opt=None):
    """ Scales fixed and/or dispatchable loads.

    @param load: Each element specifies the amount of scaling for the
        corresponding load zone, either as a direct scale factor
        or as a target quantity. If there are nz load zones this
        vector has nz elements.
    @param bus: Standard BUS matrix with nb rows, where the fixed active
        and reactive loads available for scaling are specified in
        columns PD and QD
    @param gen: (optional) standard GEN matrix with ng rows, where the
        dispatchable loads available for scaling are specified by
        columns PG, QG, PMIN, QMIN and QMAX (in rows for which
        ISLOAD(GEN) returns true). If GEN is empty, it assumes
        there are no dispatchable loads.
    @param load_zone: (optional) nb element vector where the value of
        each element is either zero or the index of the load zone
        to which the corresponding bus belongs. If LOAD_ZONE(b) = k
        then the loads at bus b will be scaled according to the
        value of LOAD(k). If LOAD_ZONE(b) = 0, the loads at bus b
        will not be modified. If LOAD_ZONE is empty, the default is
        determined by the dimensions of the LOAD vector. If LOAD is
        a scalar, a single system-wide zone including all buses is
        used, i.e. LOAD_ZONE = ONES(nb, 1). If LOAD is a vector, the
        default LOAD_ZONE is defined as the areas specified in the
        BUS matrix, i.e. LOAD_ZONE = BUS(:, BUS_AREA), and LOAD
        should have dimension = MAX(BUS(:, BUS_AREA)).
    @param opt: (optional) struct with three possible fields, 'scale',
        'pq' and 'which' that determine the behavior as follows:

        OPT.scale (default is 'FACTOR')
            'FACTOR'   : LOAD consists of direct scale factors, where
                         LOAD(k) = scale factor R(k) for zone k
            'QUANTITY' : LOAD consists of target quantities, where
                         LOAD(k) = desired total active load in MW for
                         zone k after scaling by an appropriate R(k)

        OPT.pq    (default is 'PQ')
            'PQ' : scale both active and reactive loads
            'P'  : scale only active loads

        OPT.which (default is 'BOTH' if GEN is provided, else 'FIXED')
            'FIXED'        : scale only fixed loads
            'DISPATCHABLE' : scale only dispatchable loads
            'BOTH'         : scale both fixed and dispatchable loads

    Assumes consecutive bus numbering when dealing with dispatchable loads.

    @see: L{total_load}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """

    nb = bus.shape[0]   ## number of buses

    ##-----  process inputs  -----
    if gen is None:
        gen = array([])
    if load_zone is None:
        load_zone = array([], int)
    if opt is None:
        opt = {}

    ## fill out and check opt
    if len(gen) == 0:
        opt["which"] = 'FIXED'
    if 'pq' not in opt:
        opt["pq"] = 'PQ'          ## 'PQ' or 'P'
    if 'which' not in opt:
        opt["which"] = 'BOTH'     ## 'FIXED', 'DISPATCHABLE' or 'BOTH'
    if 'scale' not in opt:
        opt["scale"] = 'FACTOR'   ## 'FACTOR' or 'QUANTITY'
    if (opt["pq"] != 'P') and (opt["pq"] != 'PQ'):
        stderr.write("scale_load: opt['pq'] must equal 'PQ' or 'P'\n")
    if (opt["which"][0] != 'F') and (opt["which"][0] != 'D') and (opt["which"][0] != 'B'):
        stderr.write("scale_load: opt.which should be 'FIXED, 'DISPATCHABLE or 'BOTH'\n")
    if (opt["scale"][0] != 'F') and (opt["scale"][0] != 'Q'):
        stderr.write("scale_load: opt.scale should be 'FACTOR or 'QUANTITY'\n")
    if (len(gen) > 0) and (opt["which"][0] != 'F'):
        stderr.write('scale_load: need gen matrix to scale dispatchable loads\n')

    ## create dispatchable load connection matrix
    if len(gen) > 0:
        ng = gen.shape[0]
        is_ld = isload(gen) & (gen[:, GEN_STATUS] > 0)
        ld = find(is_ld)

        ## create map of external bus numbers to bus indices
        i2e = bus[:, BUS_I].astype(int)
        e2i = zeros(max(i2e) + 1, int)
        e2i[i2e] = arange(nb)

        gbus = gen[:, GEN_BUS].astype(int)
        Cld = sparse((is_ld, (e2i[gbus], arange(ng))), (nb, ng))
    else:
        ng = 0
        ld = array([])

    if len(load_zone) == 0:
        if len(load) == 1:        ## make a single zone of all load buses
            load_zone = zeros(nb, int)             ## initialize
            load_zone[bus[:, PD] != 0] = 1         ## FIXED loads
            if len(gen) > 0:
                gbus = gen[ld, GEN_BUS].astype(int)
                load_zone[e2i[gbus]] = 1    ## DISPATCHABLE loads
        else:                        ## use areas defined in bus data as zones
            load_zone = bus[:, BUS_AREA]

    ## check load_zone to make sure it's consistent with size of load vector
    if max(load_zone) > len(load):
        stderr.write('scale_load: load vector must have a value for each load zone specified\n')

    ##-----  compute scale factors for each zone  -----
    scale = load.copy()
    Pdd = zeros(nb)     ## dispatchable P at each bus
    if opt["scale"][0] == 'Q':  ## 'QUANTITY'
        ## find load capacity from dispatchable loads
        if len(gen) > 0:
            Pdd = -Cld * gen[:, PMIN]

        ## compute scale factors
        for k in range(len(load)):
            idx = find(load_zone == k + 1)
            fixed = sum(bus[idx, PD])
            dispatchable = sum(Pdd[idx])
            total = fixed + dispatchable
            if opt["which"][0] == 'B':      ## 'BOTH'
                if total != 0:
                    scale[k] = load[k] / total
                elif load[k] == total:
                    scale[k] = 1
                else:
                    stderr.write('scale_load: impossible to make zone %d load equal %g by scaling non-existent loads\n' % (k, load[k]))
            elif opt["which"][0] == 'F':    ## 'FIXED'
                if fixed != 0:
                    scale[k] = (load[k] - dispatchable) / fixed
                elif load[k] == dispatchable:
                    scale[k] = 1
                else:
                    stderr.write('scale_load: impossible to make zone %d load equal %g by scaling non-existent fixed load\n' % (k, load[k]))
            elif opt["which"][0] == 'D':    ## 'DISPATCHABLE'
                if dispatchable != 0:
                    scale[k] = (load[k] - fixed) / dispatchable
                elif load[k] == fixed:
                    scale[k] = 1
                else:
                    stderr.write('scale_load: impossible to make zone %d load equal %g by scaling non-existent dispatchable load\n' % (k, load[k]))

    ##-----  do the scaling  -----
    ## fixed loads
    if opt["which"][0] != 'D':      ## includes 'FIXED', not 'DISPATCHABLE' only
        for k in range(len(scale)):
            idx = find(load_zone == k + 1)
            bus[idx, PD] = bus[idx, PD] * scale[k]
            if opt["pq"] == 'PQ':
                bus[idx, QD] = bus[idx, QD] * scale[k]

    ## dispatchable loads
    if opt["which"][0] != 'F':      ## includes 'DISPATCHABLE', not 'FIXED' only
        for k in range(len(scale)):
            idx = find(load_zone == k + 1)
            i = find( in1d(gen[ld, GEN_BUS], idx) )
            ig = ld[i]

            gen[ix_(ig, [PG, PMIN])] = gen[ix_(ig, [PG, PMIN])] * scale[k]
            if opt["pq"] == 'PQ':
                gen[ix_(ig, [QG, QMIN, QMAX])] = gen[ix_(ig, [QG, QMIN, QMAX])] * scale[k]

    return bus, gen
