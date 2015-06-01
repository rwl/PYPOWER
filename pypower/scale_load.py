# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Scales fixed and/or dispatchable loads.
"""

from sys import stderr

from numpy import array, zeros, arange, in1d, ix_
from numpy import flatnonzero as find

from scipy.sparse import csr_matrix as sparse

from pypower.isload import isload

from pypower.idx_bus import PD, QD, BUS_AREA, BUS_I
from pypower.idx_gen import PG, QG, QMAX, QMIN, GEN_BUS, GEN_STATUS, PMIN


def scale_load(load, bus, gen=None, load_zone=None, opt=None):
    """Scales fixed and/or dispatchable loads.

    Assumes consecutive bus numbering when dealing with dispatchable loads.

    @param load: Each element specifies the amount of scaling for the
        corresponding load zone, either as a direct scale factor
        or as a target quantity. If there are C{nz} load zones this
        vector has C{nz} elements.
    @param bus: Standard C{bus} matrix with C{nb} rows, where the fixed active
        and reactive loads available for scaling are specified in
        columns C{PD} and C{QD}
    @param gen: (optional) standard C{gen} matrix with C{ng} rows, where the
        dispatchable loads available for scaling are specified by
        columns C{PG}, C{QG}, C{PMIN}, C{QMIN} and C{QMAX} (in rows for which
        C{isload(gen)} returns C{true}). If C{gen} is empty, it assumes
        there are no dispatchable loads.
    @param load_zone: (optional) C{nb} element vector where the value of
        each element is either zero or the index of the load zone
        to which the corresponding bus belongs. If C{load_zone[b] = k}
        then the loads at bus C{b} will be scaled according to the
        value of C{load[k]}. If C{load_zone[b] = 0}, the loads at bus C{b}
        will not be modified. If C{load_zone} is empty, the default is
        determined by the dimensions of the C{load} vector. If C{load} is
        a scalar, a single system-wide zone including all buses is
        used, i.e. C{load_zone = ones(nb)}. If C{load} is a vector, the
        default C{load_zone} is defined as the areas specified in the
        C{bus} matrix, i.e. C{load_zone = bus[:, BUS_AREA]}, and C{load}
        should have dimension C{= max(bus[:, BUS_AREA])}.
    @param opt: (optional) dict with three possible fields, 'scale',
        'pq' and 'which' that determine the behavior as follows:
            - C{scale} (default is 'FACTOR')
                - 'FACTOR'   : C{load} consists of direct scale factors, where
                C{load[k] =} scale factor C{R[k]} for zone C{k}
                - 'QUANTITY' : C{load} consists of target quantities, where
                C{load[k] =} desired total active load in MW for
                zone C{k} after scaling by an appropriate C{R(k)}
            - C{pq}    (default is 'PQ')
                - 'PQ' : scale both active and reactive loads
                - 'P'  : scale only active loads
            - C{which} (default is 'BOTH' if GEN is provided, else 'FIXED')
                - 'FIXED'        : scale only fixed loads
                - 'DISPATCHABLE' : scale only dispatchable loads
                - 'BOTH'         : scale both fixed and dispatchable loads

    @see: L{total_load}

    @author: Ray Zimmerman (PSERC Cornell)
    """
    nb = bus.shape[0]   ## number of buses

    ##-----  process inputs  -----
    bus = bus.copy()
    if gen is None:
        gen = array([])
    else:
        gen = gen.copy()
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
    if (len(gen) == 0) and (opt["which"][0] != 'F'):
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
        ld = array([], int)

    if len(load_zone) == 0:
        if len(load) == 1:        ## make a single zone of all load buses
            load_zone = zeros(nb, int)             ## initialize
            load_zone[bus[:, PD] != 0 or bus[:, QD] != 0] = 1  ## FIXED loads
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
                    raise ScalingError('scale_load: impossible to make zone %d load equal %g by scaling non-existent loads\n' % (k, load[k]))
            elif opt["which"][0] == 'F':    ## 'FIXED'
                if fixed != 0:
                    scale[k] = (load[k] - dispatchable) / fixed
                elif load[k] == dispatchable:
                    scale[k] = 1
                else:
                    raise ScalingError('scale_load: impossible to make zone %d load equal %g by scaling non-existent fixed load\n' % (k, load[k]))
            elif opt["which"][0] == 'D':    ## 'DISPATCHABLE'
                if dispatchable != 0:
                    scale[k] = (load[k] - fixed) / dispatchable
                elif load[k] == fixed:
                    scale[k] = 1
                else:
                    raise ScalingError('scale_load: impossible to make zone %d load equal %g by scaling non-existent dispatchable load\n' % (k, load[k]))

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
            gbus = gen[ld, GEN_BUS].astype(int)
            i = find( in1d(e2i[gbus], idx) )
            ig = ld[i]

            gen[ix_(ig, [PG, PMIN])] = gen[ix_(ig, [PG, PMIN])] * scale[k]
            if opt["pq"] == 'PQ':
                gen[ix_(ig, [QG, QMIN, QMAX])] = gen[ix_(ig, [QG, QMIN, QMAX])] * scale[k]

    return bus, gen


class ScalingError(Exception):
    pass
