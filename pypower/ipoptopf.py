# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

from time import time

from numpy import \
    array, ones, zeros, argsort, arange, r_, c_, pi, arctan2, sin, cos, \
    linalg, finfo, delete, Inf, exp, conj, asarray

from numpy import flatnonzero as find

from scipy.sparse import vstack, hstack, csc_matrix as sparse
from scipy.sparse import issparse, eye as speye

from pypower.ppoption import ppoption
from pypower.loadcase import loadcase
from pypower.ext2int import ext2int
from pypower.bustypes import bustypes
from pypower.isload import isload
from pypower.hasPQcap import hasPQcap
from pypower.makeAy import makeAy
from pypower.makeYbus import makeYbus
from pypower.int2ext import int2ext
from pypower.printpf import printpf
from pypower.costfmin import eval_f, eval_grad_f
from pypower.consfmin import eval_g, eval_jac_g

from pypower.idx_bus import MU_VMIN, MU_VMAX, BUS_TYPE, REF, LAM_P, LAM_Q, VMIN, VMAX, VA, VM

from pypower.idx_gen import \
    GEN_STATUS, GEN_BUS, QMIN, QMAX, QG, PG, PMIN, QC1MAX, QC2MAX, \
    PC2, PC1, QC2MIN, QC1MIN, PMAX, VG, MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN

from pypower.idx_brch import MU_ANGMAX, MU_ANGMIN, BR_STATUS, ANGMIN, ANGMAX, F_BUS, T_BUS, PF, QF, PT, QT, MU_SF, MU_ST

from pypower.idx_cost import MODEL, PW_LINEAR


EPS = finfo(float).eps


def ipoptopf(*args):
    """Solves an AC optimal power flow.

    bus, gen, branch, f, success = ipoptopf(casefile, ppopt)

    bus, gen, branch, f, success = ipoptopf(casefile, A, l, u, ppopt)

    bus, gen, branch, f, success = ipoptopf(baseMVA, bus, gen, branch,
                                   areas, gencost, ppopt)

    bus, gen, branch, f, success = ipoptopf(baseMVA, bus, gen, branch,
                                   areas, gencost, A, l, u, ppopt)

    bus, gen, branch, f, success = ipoptopf(baseMVA, bus, gen, branch,
                                   areas, gencost, A, l, u, ppopt,
                                   N, fparm, H, Cw)

    bus, gen, branch, f, success = ipoptopf(baseMVA, bus, gen, branch,
                                   areas, gencost, A, l, u, ppopt,
                                   N, fparm, H, Cw, z0, zl, zu)

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Richard Lincoln
    """
    import pyipopt

    nargin = len(args)

    # Sort out input arguments
    t1 = time()
    # passing filename or dict
    if isinstance(args[0], basestring) or isinstance(args[0], dict):
        #---- ipoptopf(baseMVA,  bus, gen, branch, areas, gencost, Au,    lbu, ubu, ppopt, N,  fparm, H, Cw, z0, zl, zu)
        # 12  ipoptopf(casefile, Au,  lbu, ubu,    ppopt, N,       fparm, H,   Cw,  z0,    zl, zu)
        # 9   ipoptopf(casefile, Au,  lbu, ubu,    ppopt, N,       fparm, H,   Cw)
        # 5   ipoptopf(casefile, Au,  lbu, ubu,    ppopt)
        # 4   ipoptopf(casefile, Au,  lbu, ubu)
        # 2   ipoptopf(casefile, ppopt)
        # 1   ipoptopf(casefile)
        if nargin in [1, 2, 4, 5, 9, 12]:
            casefile = args[0]
            if nargin == 12:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu,  ubu, ppopt,  N, fparm = args
                zu    = fparm
                zl    = N
                z0    = ppopt
                Cw    = ubu
                H     = lbu
                fparm = Au
                N     = gencost
                ppopt = areas
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 9:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu = args
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = ubu
                H     = lbu
                fparm = Au
                N     = gencost
                ppopt = areas
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 5:
                baseMVA, bus, gen, branch, areas = args
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = array([])
                fparm = array([])
                N     = array([])
                ppopt = areas
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 4:
                baseMVA, bus, gen, branch = args
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = array([])
                fparm = array([])
                N     = array([])
                ppopt = ppoption()
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 2:
                baseMVA, bus = args
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = array([])
                fparm = array([])
                N     = array([])
                ppopt = bus
                ubu   = array([])
                lbu   = array([])
                Au    = array([])
            elif nargin == 1:
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = array([])
                fparm = array([])
                N     = array([])
                ppopt = ppoption()
                ubu   = array([])
                lbu   = array([])
                Au    = array([])
        else:
            raise ValueError, 'ipoptopf: Incorrect input arg order, number or type\n'

        baseMVA, bus, gen, branch, areas, gencost = loadcase(casefile)
    else:    # passing individual data matrices
        #---- ipoptopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 17  ipoptopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 14  ipoptopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu, ppopt, N, fparm, H, Cw)
        # 10  ipoptopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu, ppopt)
        # 9   ipoptopf(baseMVA, bus, gen, branch, areas, gencost, Au,   lbu, ubu)
        # 7   ipoptopf(baseMVA, bus, gen, branch, areas, gencost, ppopt)
        # 6   ipoptopf(baseMVA, bus, gen, branch, areas, gencost)
        if nargin in [6, 7, 9, 10, 14, 17]:
            if nargin == 17:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt,  N, fparm, H, Cw, z0, zl, zu = args
            elif nargin == 14:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt,  N, fparm, H, Cw = args
                zu = array([])
                zl = array([])
                z0 = array([])
            elif nargin == 10:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt = args
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = array([])
                fparm = array([])
                N = array([])
            elif nargin == 9:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu = args
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = array([])
                fparm = array([])
                N = array([])
                ppopt = ppoption()
            elif nargin == 7:
                baseMVA, bus, gen, branch, areas, gencost, ppopt = args
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = array([])
                fparm = array([])
                N = array([])
                ubu = array([])
                lbu = array([])
                Au = array([])
            elif nargin == 6:
                baseMVA, bus, gen, branch, areas, gencost = args
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = array([])
                fparm = array([])
                N = array([])
                ppopt = ppoption()
                ubu = array([])
                lbu = array([])
                Au = array([])
        else:
            raise ValueError, 'ipoptopf: Incorrect input arg order, number or type\n'

    if N.shape[0] > 0:
        if N.shape[0] != fparm.shape[0] or N.shape[0] != H.shape[0] or \
                N.shape[0] != H.shape[1] or N.shape[0] != len(Cw):
            raise ValueError, 'ipoptopf: wrong dimensions in generalized cost parameters'

        if Au.shape[0] > 0 and N.shape[1] != Au.shape[1]:
            raise ValueError, 'ipoptopf: A and N must have the same number of columns'

    if len(ppopt) == 0:
        ppopt = ppoption()

    # If tables do not have multiplier/extra columns, append zero cols.
    # Update whenever the data format changes!
    if bus.shape[1] < MU_VMIN + 1:
        bus = c_[ bus, zeros((bus.shape[0], MU_VMIN + 1 - bus.shape[1])) ]

    if gen.shape[1] < MU_QMIN + 1:
        gen = c_[ gen, zeros((gen.shape[0], MU_QMIN + 1 - gen.shape[1])) ]

    if branch.shape[1] < MU_ANGMAX + 1:
        branch = c_[ branch, zeros((branch.shape[0], MU_ANGMAX + 1 - branch.shape[1])) ]

    # Filter out inactive generators and branches; save original bus & branch

    comgen = find(gen[:,GEN_STATUS] > 0)
    offgen = find(gen[:,GEN_STATUS] <= 0)
    onbranch  = find(branch[:, BR_STATUS] != 0)
    offbranch = find(branch[:, BR_STATUS] == 0)
    genorg = gen.copy()
    branchorg = branch.copy()
    ng = gen.shape[0]         # original size(gen), at least temporally
    gen = gen[comgen, :]
    branch = branch[onbranch, :]
    if gencost.shape[0] == ng:
        gencost = gencost[comgen, :]
    else:
        gencost = gencost[ r_[comgen, comgen + ng], :]

    # Renumber buses consecutively
    i2e, bus, gen, branch, areas = ext2int(bus, gen, branch, areas)
    ref, pv, pq = bustypes(bus, gen)

    # Sort generators in order of increasing bus number;
    ng = gen.shape[0]
    igen = argsort(gen[:, GEN_BUS])
    inv_gen_ord = argsort(igen)  # save for inverse reordering at the end
    gen = gen[igen, :].copy()
    if ng == gencost.shape[0]:
        gencost = gencost[igen, :]
    else:
        gencost = gencost[ r_[igen, igen + ng], :]

    # Print a warning if there is more than one reference bus
    if find(bus[:, BUS_TYPE] == REF).shape[0] > 1:
        errstr = '\nipoptopf: Warning: more than one reference bus detected in bus table data.\n' \
                 '      For a system with islands, a reference bus in each island\n' \
                 '      might help convergence but in a fully connected system such\n' \
                 '      a situation is probably not reasonable.\n\n'
        print errstr

    # Find out if any of these "generators" are actually dispatchable loads.
    # (see 'help isload' for details on what constitutes a dispatchable load)
    # Dispatchable loads are modeled as generators with an added constant
    # power factor constraint. The power factor is derived from the original
    # value of Pmin and either Qmin (for inductive loads) or Qmax (for capacitive
    # loads). If both Qmin and Qmax are zero, this implies a unity power factor
    # without the need for an additional constraint.
    vload = find( isload(gen) & ((gen[:, QMIN] != 0) | (gen[:, QMAX] != 0)) )
    # At least one of the Q limits must be zero (corresponding to Pmax == 0)
    if any( (gen[vload, QMIN] != 0) & (gen[vload, QMAX] != 0) ):
        raise ValueError, 'ipoptopf: Either Qmin or Qmax must be equal to zero for each dispatchable load.'

    # Initial values of PG and QG must be consistent with specified power factor
    # This is to prevent a user from unknowingly using a case file which would
    # have defined a different power factor constraint under a previous version
    # which used PG and QG to define the power factor.
    Qlim = (gen[vload, QMIN] == 0) * gen[vload, QMAX] + \
        (gen[vload, QMAX] == 0) * gen[vload, QMIN]
    if any( abs( gen[vload, QG] - gen[vload, PG] * Qlim / gen[vload, PMIN] ) > 1e-4 ):
        errstr = '%s\n' \
            'For a dispatchable load, PG and QG must be consistent' \
            'with the power factor defined by PMIN and the Q limits.'
        raise ValueError, errstr

    # Find out which generators require additional linear constraints
    # (as opposed to simple box constraints) on (Pg,Qg) to correctly
    # model their PQ capability curves
    ipqh = find( hasPQcap(gen, 'U') )
    ipql = find( hasPQcap(gen, 'L') )

    # Find out which branches require angle constraints
    if ppopt['OPF_IGNORE_ANG_LIM']:
        nang = 0
    else:
        iang = find((branch[:, ANGMIN] > -360) | (branch[:, ANGMAX] < 360))
        iangl = find(branch[iang, ANGMIN])
        iangh = find(branch[iang, ANGMAX])
        nang = len(iang)

    # Find out problem dimensions
    nb = bus.shape[0]                              # buses
    ng = gen.shape[0]                              # variable injections
    nl = branch.shape[0]                           # branches
    iycost = find(gencost[:, MODEL] == PW_LINEAR)  # y variables for pwl cost
    ny    = iycost.shape[0]
    neqc  = 2 * nb                                 # nonlinear equalities
    nusr  = Au.shape[0]                            # # linear user constraints
    nx    = 2*nb + 2*ng                            # control variables
    nvl   = vload.shape[0]                         # dispatchable loads
    npqh  = ipqh.shape[0]                          # general pq capability curves
    npql  = ipql.shape[0]
    if Au is None or (not issparse(Au) and len(Au) == 0):
        nz = 0
        Au = zeros((0, nx))
        if N is not None and issparse(N):   # still need to check number of columns of N
            if N.shape[1] != nx:
                raise ValueError, 'ipoptopf: user supplied N matrix must have %d columns.' % nx
    else:
        nz = Au.shape[1] - nx                       # additional linear variables
        if nz < 0:
            raise ValueError, 'ipoptopf: user supplied A matrix must have at least %d columns.' % nx
    nxyz = nx + ny + nz                             # total # of vars of all types

    # Definition of indexes into optimization variable vector and constraint
    # vector.
    thbas = 0;                thend    = thbas + nb
    vbas     = thend;         vend     = vbas + nb
    pgbas    = vend;          pgend    = pgbas + ng
    qgbas    = pgend;         qgend    = qgbas + ng
    ybas     = qgend;         yend     = ybas + ny
    zbas     = yend;          zend     = zbas + nz

    pmsmbas = 0;              pmsmend = pmsmbas + nb
    qmsmbas = pmsmend;        qmsmend = qmsmbas + nb
    sfbas   = qmsmend;        sfend   = sfbas + nl
    stbas   = sfend;          stend   = stbas + nl
    usrbas  = stend;          usrend  = usrbas + nusr # warning: nusr could be 0
    pqhbas  = usrend;         pqhend  = pqhbas + npqh # warning: npqh could be 0
    pqlbas  = pqhend;         pqlend  = pqlbas + npql # warning: npql could be 0
    vlbas   = pqlend;         vlend   = vlbas + nvl   # warning: nvl could be 0
    angbas  = vlend;          angend  = angbas + nang # # of Ay constraints.

    # Let makeAy deal with any y-variable for piecewise-linear convex costs.
    # note that if there are z variables then Ay doesn't have the columns
    # that would span the z variables, so we append them.
    if ny > 0:
        Ay, by = makeAy(baseMVA, ng, gencost, pgbas, qgbas, ybas)
        if nz > 0:
            Ay = hstack([ Ay, sparse((Ay.shape[0], nz)) ])
    else:
        Ay = array([])
        by = array([])

    ncony = Ay.shape[0]
    yconbas = angend;       yconend = yconbas + ncony # finally done with constraint indexing

    # Make Aang, lang, uang for branch angle difference limits
    if nang > 0:
        ii = r_[arange(nang), arange(nang)]
        jj = r_[branch[iang, F_BUS], branch[iang, T_BUS]]
        Aang = sparse((r_[ones(nang), -ones(nang)], (ii, jj)), (nang, nxyz))
        uang = 1e10 * ones(nang)
        lang = -uang;
        lang[iangl] = branch[iang[iangl], ANGMIN] * pi / 180
        uang[iangh] = branch[iang[iangh], ANGMAX] * pi / 180
    else:
        Aang = array([])
        lang = array([])
        uang = array([])

    # Make Avl, lvl, uvl in case there is a need for dispatchable loads
    if nvl > 0:
        xx = gen[vload, PMIN]
        yy = Qlim
        pftheta = arctan2(yy, xx)
        pc = sin(pftheta)
        qc = -cos(pftheta)
        ii = r_[ arange(nvl), arange(nvl) ]
        jj = r_[ pgbas + vload - 1, qgbas + vload - 1 ]
        Avl = sparse((r_[pc, qc], (ii, jj)), (nvl, nxyz))
        lvl = zeros(nvl, 1)
        uvl = lvl;
    else:
        Avl = array([])
        lvl = array([])
        uvl = array([])

    # Make Apqh if there is a need to add general PQ capability curves;
    # use normalized coefficient rows so multipliers have right scaling
    # in $$/pu
    if npqh > 0:
        Apqhdata = c_[gen[ipqh, QC1MAX] - gen[ipqh, QC2MAX],
                      gen[ipqh, PC2] - gen[ipqh, PC1]]
        ubpqh = (gen[ipqh, QC1MAX] - gen[ipqh, QC2MAX]) * gen[ipqh, PC1] + \
                (gen[ipqh, PC2] - gen[ipqh, PC1]) * gen[ipqh, QC1MAX]
        for i in range(npqh):
            tmp = linalg.norm(Apqhdata[i, :])
            Apqhdata[i, :] = Apqhdata[i, :] / tmp
            ubpqh[i] = ubpqh[i] / tmp

        Apqh = sparse((Apqhdata.flatten('F'),
                       (r_[arange(npqh), arange(npqh)], r_[(pgbas - 1) + ipqh, (qgbas - 1) + ipqh])),
                      (npqh, nxyz))
        ubpqh = ubpqh / baseMVA
        lbpqh = -1e10 * ones(npqh)
    else:
        Apqh = array([])
        ubpqh = array([])
        lbpqh = array([])

    # similarly Apql
    if npql > 0:
        Apqldata = c_[gen[ipql, QC2MIN] - gen[ipql, QC1MIN],
                      gen[ipql, PC1] - gen[ipql, PC2]]
        ubpql = (gen[ipql, QC2MIN] - gen[ipql, QC1MIN]) * gen[ipql, PC1] - \
                (gen[ipql, PC2] - gen[ipql, PC1]) * gen[ipql, QC1MIN]
        for i in range(npql):
            tmp = linalg.norm(Apqldata[i, :])
            Apqldata[i, :] = Apqldata[i, :] / tmp
            ubpql[i] = ubpql[i] / tmp

        Apql = sparse((Apqldata.flatten('F'),
                       (r_[arange(npql), arange(npql)], r_[(pgbas - 1) + ipql, (qgbas - 1) + ipql])),
                      (npql, nxyz))

        ubpql = ubpql / baseMVA
        lbpql = -1e10 * ones(npql)
    else:
        Apql = array([])
        ubpql = array([])
        lbpql = array([])

    # # reorder columns of Au and N according to new gen ordering
    # if ~isempty(Au)
    #   if nz > 0
    #     Au = Au(:, [[1:vend]'; vend+[igen; ng+igen]; qgend+[1:nz]'])
    #   else
    #     Au = Au(:, [[1:vend]'; vend+[igen; ng+igen]])
    #   end
    # end
    # if ~isempty(N)
    #   if nz > 0
    #     N =  N(:, [[1:vend]'; vend+[igen; ng+igen]; qgend+[1:nz]'])
    #   else
    #     N =  N(:, [[1:vend]'; vend+[igen; ng+igen]])
    #   end
    # end

    # Insert y columns in Au and N as necessary
    if ny > 0:
        if nz > 0:
            Au = hstack([ Au[:, :qgend], sparse((nusr, ny)), Au[:, qgend + arange(nz)] ])
            if N is not None and issparse(N):
                N = hstack([ N[:, :qgend], sparse((N.shape[0], ny)), N[:, qgend + arange(nz)] ])
        else:
            if nusr:
                Au = hstack([ Au, sparse((nusr, ny)) ])
            if N is not None and issparse(N):
                N = hstack([ N, sparse((N.shape[0], ny)) ])

    # Now form the overall linear restriction matrix;
    # note the order of the constraints.

    if (ncony > 0):
        As = [ Au,
               Apqh,
               Apql,
               Avl,
               Aang,
               Ay,
               sparse((ones(ny), (zeros(ny), arange(ybas, yend))), (1, nxyz)) ]  # "linear" cost

        A = vstack([a for a in As if a.shape[0] > 0])
        l = r_[ lbu,
                lbpqh,
                lbpql,
                lvl,
                lang,
                -1e10 * ones(ncony + 1) ]
        u = r_[ ubu,
                ubpqh,
                ubpql,
                uvl,
                uang,
                by,
                1e10 ]
    else:
        As = [ Au, Apqh, Apql, Avl, Aang ]
        if len([a for a in As if a.shape[0] > 0]) > 0:
            A = vstack([a for a in As if a.shape[0] > 0])
        else:
            A = array([])
        l = r_[ lbu, lbpqh, lbpql, lvl, lang ]
        u = r_[ ubu, ubpqh, ubpql, uvl, uang ]

    # So, can we do anything good about lambda initialization?
    if all(bus[:, LAM_P] == 0):
        bus[:, LAM_P] = (10) * ones(nb)

    # --------------------------------------------------------------
    # Up to this point, the setup is MINOS-like.  We now adapt
    # things for pyipopt.

    # Form a dict with basic info to pass on as a parameter
    parms = {
        'nb': nb,
        'ng': ng,
        'nl': nl,
        'ny': ny,
        'nx': nx,
        'nvl': nvl,
        'nz': nz,
        'nxyz': nxyz,
        'thbas': thbas,
        'thend': thend,
        'vbas': vbas,
        'vend': vend,
        'pgbas': pgbas,
        'pgend': pgend,
        'qgbas': qgbas,
        'qgend': qgend,
        'ybas': ybas,
        'yend': yend,
        'zbas': zbas,
        'zend': zend,
        'pmsmbas': pmsmbas,
        'pmsmend': pmsmend,
        'qmsmbas': qmsmbas,
        'qmsmend': qmsmend,
        'sfbas': sfbas,
        'sfend': sfend,
        'stbas': stbas,
        'stend': stend
    }

    # If there are y variables the last row of A is a linear cost vector
    # of length nxyz. Let us excise it from A explicitly if it exists;
    # otherwise it is zero.
    if ny > 0:
        nn = A.shape[0]
        A = A.tolil()
        ccost = A[nn - 1, :].todense()
        ccost = asarray(ccost).flatten()
        A = A[:nn - 1, :].tocoo()
        l = delete(l, nn - 1)
        u = delete(u, nn - 1)
    else:
        ccost = zeros((1, nxyz))

    # Divide l <= A*x <= u into less than, equal to, greater than, doubly-bounded
    # sets.
    ieq = find( abs(u - l) <= EPS )
    igt = find( u >=  1e10 )  # unlimited ceiling
    ilt = find( l <= -1e10 )  # unlimited bottom
    ibx = find( (abs(u - l) > EPS) & (u < 1e10) & (l > -1e10))
#    Af  = hstack([ A[ilt, :], -A[igt, :], A[ibx, :], -A[ibx, :] ])
#    bf  = r_[ u[ilt], -l[igt], u[ibx], -l[ibx]]
#    Afeq = A[ieq, :]
#    bfeq = u[ieq]

    # bounds on optimization vars; y vars unbounded
    UB = Inf * ones(nxyz)
    LB = -UB
    LB[thbas + ref] = bus[ref, VA] * pi / 180
    UB[thbas + ref] = bus[ref, VA] * pi / 180
    LB[vbas:vend]   = bus[:, VMIN]
    UB[vbas:vend]   = bus[:, VMAX]
    LB[pgbas:pgend] = gen[:, PMIN] / baseMVA
    UB[pgbas:pgend] = gen[:, PMAX] / baseMVA
    LB[qgbas:qgend] = gen[:, QMIN] / baseMVA
    UB[qgbas:qgend] = gen[:, QMAX] / baseMVA
    if len(zl) > 0:
        LB[zbas:zend] = zl
    if len(zu) > 0:
        UB[zbas:zend] = zu

    # Compute initial vector
    x0 = zeros(nxyz)
    x0[thbas:thend] = bus[:, VA] * pi / 180
    x0[vbas:vend]   = bus[:, VM]
    # buses w. gens init V from gen data
    x0[vbas + gen[:, GEN_BUS].astype(int)] = gen[:, VG]
    x0[pgbas:pgend] = gen[:, PG] / baseMVA
    x0[qgbas:qgend] = gen[:, QG] / baseMVA
    # no ideas to initialize y variables
    if len(z0) > 0:
        x0[zbas:zend] = z0

    # build admittance matrices
    Ybus, Yf, Yt = makeYbus(baseMVA, bus, branch)

    # Tolerances
    if ppopt['CONSTR_MAX_IT'] == 0:   ## number of iterations
        ppopt['CONSTR_MAX_IT'] = 150 + 2*nb

    # basic optimset options needed for fmincon
    # fmoptions = optimset('GradObj', 'on', 'Hessian', 'on', 'LargeScale', 'on', ...
    #                    'GradConstr', 'on')
#    fmoptions = optimset('GradObj', 'on', 'LargeScale', 'off', 'GradConstr', 'on')
#    fmoptions = optimset(fmoptions, 'MaxIter', ppopt(19), 'TolCon', ppopt(16) )
#    fmoptions = optimset(fmoptions, 'TolX', ppopt(17), 'TolFun', ppopt(18) )
#    fmoptions.MaxFunEvals = 4 * fmoptions.MaxIter

#    else:
#        fmoptions.Display = 'iter'

#    Af = Af.todense()
#    Afeq = Afeq.todense()

    ## build Jacobian structure
    nA = A.shape[0]                ## number of original linear constraints
    n = len(x0)
    f = branch[:, F_BUS]                           ## list of "from" buses
    t = branch[:, T_BUS]                           ## list of "to" buses
    Cf = sparse((ones(nl), (arange(nl), f)), (nl, nb))      ## connection matrix for line & from buses
    Ct = sparse((ones(nl), (arange(nl), t)), (nl, nb))      ## connection matrix for line & to buses
    Cl = Cf + Ct
    Cb = Cl.T * Cl + speye(nb, nb)
    Cg = sparse((ones(ng), (gen[:, GEN_BUS], arange(ng))), (nb, ng))
    nzz = ny + nz
    if nzz > 0:
        Js = vstack([
            hstack([Cb, Cb, Cg,                 Cg, sparse((nb, nzz))]),
            hstack([Cb, Cb, Cg,                 Cg, sparse((nb, nzz))]),
    #        hstack([Cb, Cb, Cg,                 sparse((nb, ng)), sparse((nb, nzz))]),
    #        hstack([Cb, Cb, sparse((nb,   ng)), Cg,               sparse((nb, nzz))]),
            hstack([Cl, Cl, sparse((nl, 2*ng)),     sparse((nl, nzz))]),
            hstack([Cl, Cl, sparse((nl, 2*ng)),     sparse((nl, nzz))])
        ], 'coo')
    else:
        Js = vstack([
            hstack([Cb, Cb, Cg,                 Cg]),
            hstack([Cb, Cb, Cg,                 Cg]),
#            hstack([Cb, Cb, Cg,                 sparse((nb, ng))]),
#            hstack([Cb, Cb, sparse((nb,   ng)), Cg,             ]),
            hstack([Cl, Cl, sparse((nl, 2*ng)),   ]),
            hstack([Cl, Cl, sparse((nl, 2*ng)),   ])
        ], 'coo')
    if A is not None and issparse(A):
        Js = vstack([Js, A])

    ## number of equality constraints
    neqnln = 2 * nb
    ## number of inequality constraints
    niqnln = 2 * nl
    ## total number of constraints
    m = Js.shape[0] #neqnln + niqnln + nA
    assert Js.shape[0] == (neqnln + niqnln + nA)
    ## lower bound of constraint
    gl = r_[zeros(neqnln), -Inf * ones(niqnln), l]
    ## upper bound of constraints
    gu = r_[zeros(neqnln),       zeros(niqnln), u]
    ## number of nonzeros in Jacobi matrix
    nnzj = Js.nnz

    ## number of non-zeros in Hessian matrix
    nnzh = 0  ## Hessian approximation

    nlp = pyipopt.create(n, LB, UB, m, gl, gu, nnzj, nnzh,
                         eval_f, eval_grad_f, eval_g, eval_jac_g)

    user_data = {'baseMVA': baseMVA, 'bus': bus, 'gen': gen, 'branch': branch,
        'areas': areas, 'gencost': gencost, 'Ybus': Ybus, 'Yf': Yf, 'Yt': Yt,
        'ppopt': ppopt, 'parms': parms,
        'ccost': ccost, 'N': N, 'fparm': fparm, 'H': H, 'Cw': Cw,
        'Js': Js, 'A': A}

    ## set IPOPT options
    if ppopt['VERBOSE'] >= 0:
        nlp.int_option('print_level', ppopt['VERBOSE'] * 5)
    nlp.num_option('tol', ppopt['OPF_VIOLATION'])
    nlp.num_option('constr_viol_tol', ppopt['CONSTR_TOL_X'])
    nlp.int_option('max_iter', ppopt['CONSTR_MAX_IT'])

    # Possible values:
    #  - ma27                    [use the Harwell routine MA27]
    #  - ma57                    [use the Harwell routine MA57]
    #  - pardiso                 [use the Pardiso package]
    #  - wsmp                    [use WSMP package]
    #  - mumps                   [use MUMPS package]
    #  - custom                  [use custom linear solver]
    nlp.str_option('linear_solver', 'mumps')

#    for k, v in kw_args.iteritems():
#        if isinstance(v, int):
#            nlp.int_option(k, v)
#        elif isinstance(v, basestring):
#            nlp.str_option(k, v)
#        else:
#            nlp.num_option(k, v)


    result = nlp.solve(x0, m, user_data)

    ## final values for the primal variables
    x = result[0]
    ## final values for the lower bound multipliers
    zl = result[1]
    ## final values for the upper bound multipliers
    zu = result[2]
    ## final value of the objective
    f = result[3]
    ## status of the algorithm
    status = result[4]
    ## final multipliers for constraints
    zg = result[5]

    nlp.close()

    eqnonlin = zg[:neqnln]
    ineqnonlin = zg[neqnln:neqnln + niqnln]

    info = status
    success = (status == 0)

    # Unpack optimal x
    bus[:, VA] = x[thbas:thend] * 180 / pi
    bus[:, VM] = x[vbas:vend]
    gen[:, PG] = baseMVA * x[pgbas:pgend]
    gen[:, QG] = baseMVA * x[qgbas:qgend]
    gen[:, VG] = bus[gen[:, GEN_BUS].astype(int), VM]

    # reconstruct voltages
    Va = x[thbas:thend]
    Vm = x[vbas:vend]
    V = Vm * exp(1j * Va)

    ## compute branch injections
    Sf = V[branch[:, F_BUS].astype(int)] * conj(Yf * V)  ## cplx pwr at "from" bus, p.u.
    St = V[branch[:, T_BUS].astype(int)] * conj(Yt * V)  ## cplx pwr at "to" bus, p.u.
    branch[:, PF] = Sf.real * baseMVA
    branch[:, QF] = Sf.imag * baseMVA
    branch[:, PT] = St.real * baseMVA
    branch[:, QT] = St.imag * baseMVA

    # Put in Lagrange multipliers
    gen[:, MU_PMAX]  = zu[pgbas:pgend] / baseMVA
    gen[:, MU_PMIN]  = zl[pgbas:pgend] / baseMVA
    gen[:, MU_QMAX]  = zu[qgbas:qgend] / baseMVA
    gen[:, MU_QMIN]  = zl[qgbas:qgend] / baseMVA
    bus[:, LAM_P]    = eqnonlin[:nb] / baseMVA
    bus[:, LAM_Q]    = eqnonlin[nb:2 * nb] / baseMVA
    bus[:, MU_VMAX]  = zu[vbas:vend]
    bus[:, MU_VMIN]  = zl[vbas:vend]
    branch[:, MU_SF] = ineqnonlin[:nl] / baseMVA
    branch[:, MU_ST] = ineqnonlin[nl:2 * nl] / baseMVA

    # extract lambdas from linear constraints
    lam = zg[neqnln + niqnln:]
#    nlt = len(ilt)
#    ngt = len(igt)
#    nbx = len(ibx)
#    lam = zeros(u.shape)
#    lam[ieq] = lmbda.eqlin
#    lam[ilt] = lmbda.ineqlin[:nlt]
#    lam[igt] = -lmbda.ineqlin[nlt + arange(ngt)]
#    lam[ibx] = lmbda.ineqlin[nlt + ngt + arange(nbx)] - lmbda.ineqlin[nlt + ngt + nbx + arange(nbx)]

    # stick in non-linear constraints too, so we can use the indexing variables
    # we've defined, and negate so it looks like the pimul from MINOS
    pimul = r_[
        -eqnonlin[:nb],
        -eqnonlin[nb:2 * nb],
        -ineqnonlin[:nl],
        -ineqnonlin[nl:2 * nl],
        -lam,
        -1,       ## dummy entry corresponding to linear cost row in A
        zl - zu
    ]
    #pimul = r_[-zg, -1, zl - zu]

    # If we succeeded and there were generators with general pq curve
    # characteristics, this is the time to re-compute the multipliers,
    # splitting any nonzero multiplier on one of the linear bounds among the
    # Pmax, Pmin, Qmax or Qmin limits, producing one multiplier for a P limit and
    # another for a Q limit. For upper Q limit, if we are neither at Pmin nor at
    # Pmax, the limit is taken as Pmin if the Qmax line's normal has a negative P
    # component, Pmax if it has a positive P component. Messy but there really
    # are many cases.  Remember multipliers in pimul() are negative.
    muPmax = gen[:, MU_PMAX]
    muPmin = gen[:, MU_PMIN]
    if success and (npqh > 0):
        k = 0
        for i in ipqh:
            if muPmax[i] > 0:
                gen[i, MU_PMAX] = gen[i, MU_PMAX] - pimul[pqhbas + k] * Apqhdata[k, 0] / baseMVA
            elif muPmin[i] > 0:
                gen[i, MU_PMIN] = gen[i, MU_PMIN] + pimul[pqhbas + k] * Apqhdata[k, 0] / baseMVA
            else:
                if Apqhdata[k, 0] >= 0:
                    gen[i, MU_PMAX] = gen[i, MU_PMAX] - pimul[pqhbas + k] * Apqhdata[k, 0] / baseMVA
                else:
                    gen[i, MU_PMIN] = gen[i, MU_PMIN] + pimul[pqhbas + k] * Apqhdata[k, 0] / baseMVA

            gen[i, MU_QMAX] = gen[i, MU_QMAX] - pimul[pqhbas + k] * Apqhdata[k, 1] / baseMVA
            k = k + 1

    if success and (npql > 0):
        k = 0
        for i in range(ipql):
            if muPmax[i] > 0:
                gen[i, MU_PMAX] = gen[i, MU_PMAX] - pimul[pqlbas + k] * Apqldata[k, 0] / baseMVA
            elif muPmin[i] > 0:
                gen[i, MU_PMIN] = gen[i, MU_PMIN] + pimul[pqlbas + k] * Apqldata[k, 0] / baseMVA
            else:
                if Apqldata[k, 0] >= 0:
                    gen[i, MU_PMAX] = gen[i, MU_PMAX] - pimul[pqlbas + k] * Apqldata[k, 0] / baseMVA
                else:
                    gen[i, MU_PMIN] = gen[i, MU_PMIN] + pimul[pqlbas + k] * Apqldata[k, 0] / baseMVA

            gen[i, MU_QMIN] = gen[i, MU_QMIN] + pimul[pqlbas + k -1 ] * Apqldata[k, 1] / baseMVA
            k = k + 1

    # angle limit constraints
    if success and (nang > 0):
        tmp = arange(angbas, angend)
        ii = find(pimul[tmp] > 0)
        branch[iang[ii], MU_ANGMIN] =  pimul[tmp[ii]] * pi / 180
        ii = find(pimul[tmp] < 0)
        branch[iang[ii], MU_ANGMAX] = -pimul[tmp[ii]] * pi / 180

    # With these modifications, printpf must then look for multipliers
    # if available in order to determine if a limit has been hit.

    # We are done with standard opf but we may need to provide the
    # constraints and their Jacobian also.
    g = eval_g(x, user_data)
    dg_row, dg_col = eval_jac_g(x, True, user_data)
    dg_data = eval_jac_g(x, False, user_data)
    jac = sparse((dg_data, (dg_row, dg_col)))

    # Go back to original data.
    # reorder generators
    gen = gen[inv_gen_ord, :]

    # convert to original external bus ordering
    bus, gen, branch, areas = int2ext(i2e, bus, gen, branch, areas)

    # Now create output matrices with all lines, all generators, committed and
    # non-committed
    busout = bus.copy()
    genout = genorg.copy()
    branchout = branchorg.copy()
    genout[comgen, :] = gen
    branchout[onbranch, :] = branch
    # And zero out appropriate fields of non-comitted generators and lines
    if len(offgen) > 0:
        tmp = zeros(len(offgen))
        genout[offgen, PG] = tmp
        genout[offgen, QG] = tmp
        genout[offgen, MU_PMAX] = tmp
        genout[offgen, MU_PMIN] = tmp

    if len(offbranch) > 0:
        tmp = zeros(len(offbranch))
        branchout[offbranch, PF] = tmp
        branchout[offbranch, QF] = tmp
        branchout[offbranch, PT] = tmp
        branchout[offbranch, QT] = tmp
        branchout[offbranch, MU_SF] = tmp
        branchout[offbranch, MU_ST] = tmp

    et = time() - t1

    return busout, genout, branchout, f, success, info, et, g, jac, x, pimul
