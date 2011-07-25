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

"""Evaluates objective function, gradient and Hessian for OPF.
"""

from sys import stdout

from numpy import arange, polyval, polyder, ones, zeros, r_, flatnonzero as find

from scipy.sparse import spdiags, eye, csc_matrix as sparse

from pypower.idx_gen import PG, QG
from pypower.totcost import totcost
from pypower.pqcost import pqcost
from pypower.idx_cost import MODEL, POLYNOMIAL, PW_LINEAR, COST, NCOST


def costfmin(x, baseMVA, bus, gen, gencost, branch, areas,
             Ybus, Yf, Yt, mpopt, parms, ccost, N, fparm, H, Cw):
    """Evaluates objective function, gradient and Hessian for OPF.
    """
    ## unpack needed parameters
    # nb = parms[0]
    ng = parms[1]
    # nl = parms[2]
    ny = parms[3]
    # nx = parms[4]
    # nvl = parms[5]
    nz = parms[6]
    # nxyz = parms[7]
    # thbas = parms[8]
    # thend = parms[9]
    # vbas = parms[10]
    vend = parms[11]
    pgbas = parms[12]
    pgend = parms[13]
    qgbas = parms[14]
    qgend = parms[15]
    # ybas = parms[16]
    # yend = parms[17]
    # zbas = parms[18]
    # zend = parms[19]
    # pmsmbas = parms[20]
    # pmsmend = parms[21]
    # qmsmbas = parms[22]
    # qmsmend = parms[23]
    # sfbas = parms[24]
    # sfend = parms[25]
    # stbas = parms[26]
    # stend = parms[27]

    ## grab Pg & Qg
    Pg = x[pgbas:pgend]            ## active generation in p.u.
    Qg = x[qgbas:qgend]            ## reactive generation in p.u.

    ## put Pg & Qg back in gen
    gen[:, PG] = Pg * baseMVA      ## active generation in MW
    gen[:, QG] = Qg * baseMVA      ## reactive generation in MVAr

    ##----- evaluate objective function -----
    ## polynomial cost of P and Q
    # use totcost only on polynomial cost; in the minimization problem
    # formulation, pwl cost is the sum of the y variables.
    ipol = find(gencost[:, MODEL] == POLYNOMIAL)   ## poly MW and MVAr costs
    ipwl = find(gencost[:, MODEL] == PW_LINEAR)    ## pw_lin MW and MVAr costs
    xx = r_[ gen[:, PG], gen[:, QG] ]
    if len(ipol) > 0:
        f = sum( totcost(gencost[ipol, :], xx[ipol]) )  ## cost of poly P or Q
    else:
        f = 0

    ## piecewise linear cost of P and Q
    if ny > 0:
        f = f + ccost * x

    ## generalized cost term
    if len(N) > 0:
        nw = N.shape[0]
        r = N * x - fparm[:, 1]            ## Nx - rhat
        h = fparm[:, 2]
        iLT = find(r < -h)                 ## below dead zone
        iEQ = find((r == 0) & (h == 0))    ## dead zone doesn't exist
        iGT = find(r > h)                  ## above dead zone
        iND = r_[iLT, iEQ, iGT]            ## rows that are Not in the Dead region
        D = sparse(iND, iND, 1, nw, nw)
        M = spdiags(fparm[:, 3], 0, nw, nw)
        hh = sparse((r_[ ones(len(iLT)),
                         zeros(len(iEQ))
                        -ones(len(iGT)) ], (iND, iND)), (nw, nw)) * h
        rr = r + hh

        ## create diagonal matrix w/ rr on diagonal for quadratic rows (those that
        ## need to be squared), 1 for linear rows
        iL = find(fparm[:, 0] == 1)    ## rows using linear function
        iQ = find(fparm[:, 0] == 2)    ## rows using quadratic function
        iLQ = r_[iL, iQ]               ## linear rows first, then quadratic
        SQR = sparse((r_[ones(len(iL)), rr(iQ)], (iLQ, iLQ)), (nw, nw))

        w = M * D * SQR * rr
        f = f + (w.T * H * w) / 2 + Cw.T * w

    ##----- evaluate cost gradient -----
    if nargout > 1:
        ## polynomial cost of P and Q
        df_dPgQg = zeros(2*ng, 1)
        for i in ipol:
            ## w.r.t p.u. Pg
            df_dPgQg[i] = baseMVA * \
                    polyval(polyder(gencost[i, COST:(COST + gencost[i, NCOST] - 1)]), xx[i])

        df = r_[  zeros(vend),          ## partial w.r.t. Va & Vm
                  df_dPgQg,             ## partial w.r.t. polynomial cost Pg and Qg
                  zeros(ny + nz)  ]

        ## piecewise linear cost of P and Q
        df = df + ccost.T  # As in MINOS, the linear cost row is additive wrt any nonlinear cost.

        ## generalized cost term
        if len(N) > 0:
            SQR2 = (eye(nw) + sparse(iQ, iQ, 1, nw, nw)) * SQR
            df = df + ((H * w + Cw).T * (M * D * SQR2 * N)).T

            ## numerical check
            if 0:    ## 1 to check, 0 to skip check
                ddff = zeros(df.shape)
                step = 1e-7
                tol  = 1e-3
                for k in range(len(x)):
                    xx = x.copy()
                    xx[k] = xx[k] + step
                    ddff[k] = (costfmin(xx, baseMVA, bus, gen, gencost, branch, areas,
                          Ybus, Yf, Yt, mpopt, parms, ccost, N, fparm, H, Cw) - f) / step

                if max(abs(ddff - df)) > tol:
                    idx = find(abs(ddff - df) == max(abs(ddff - df)))
                    stdout.write('\nMismatch in gradient\n')
                    stdout.write('idx             df(num)         df              diff\n')
                    stdout.write('%4d%16g%16g%16g\n' % (arange(len(df)), ddff, df, abs(ddff - df)))
                    stdout.write('MAX\n')
                    stdout.write('%4d%16g%16g%16g\n' % (idx, ddff(idx), df[idx], abs(ddff[idx] - df[idx])))
                    stdout.write('\n')

    return f, df

    # Currently PyIPOPT can't use the Hessian. When it does
    # the following must be fixed for mixed poly/pwl costs.

    ## ---- evaluate cost Hessian -----
    if nargout > 2:
        pcost, qcost = pqcost(gencost, gen.shape[0])

        d2f_dPg2 = zeros(ng)
        d2f_dQg2 = zeros(ng)
        for i in range(ng):
            d2f_dPg2[i] = polyval(polyder(polyder(pcost[i,COST:(COST + pcost[i, NCOST] - 1)])),
                                  Pg[i] * baseMVA) * baseMVA**2     ## w.r.t p.u. Pg

        if len(qcost) > 0:          ## Qg is not free
            for i in range(ng):
                d2f_dQg2[i] = polyval(polyder(polyder(qcost[i,COST:(COST + qcost[i, NCOST] - 1)])),
                                      Qg[i] * baseMVA) * baseMVA**2     ## w.r.t p.u. Qg

        i = arange(pgbas, qgend)
        d2f = sparse((r_[d2f_dPg2, d2f_dQg2], (i, i)))

    return f, df, d2f
