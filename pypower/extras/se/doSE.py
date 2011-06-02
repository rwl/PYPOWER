# Copyright (C) 2009-2011 Rui Bo <eeborui@hotmail.com>
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

from numpy import array, angle, abs, ones, exp, linalg, conj, Inf, power

from scipy.sparse import \
    csr_matrix, vstack, hstack

from scipy.sparse.linalg import spsolve

from dSbus_dV import dSbus_dV
from dSbr_dV import dSbr_dV

from idx_bus import *
from idx_brch import *
from idx_gen import *


def doSE(baseMVA, bus, gen, branch, Ybus, Yf, Yt, V0, ref, pv, pq, measure, idx, sigma):
    """ Do state estimation.

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """

    ## options
    tol     = 1e-5  # ppopt(2)
    max_it  = 100   # ppopt(3)
    verbose = False # ppopt(31)

    ## initialize
    j = 1j
    converged = False
    i = 0
    V = V0
    Va = angle(V)
    Vm = abs(V)

    nb = Ybus.shape[0]
    f = branch[:, F_BUS]       ## list of "from" buses
    t = branch[:, T_BUS]       ## list of "to" buses

    ## get non reference buses
    nonref = pv + pq

    ## form measurement vector 'z'. NOTE: all are p.u. values
    z = array([
        measure["PF"],
        measure["PT"],
        measure["PG"],
        measure["Va"],
        measure["QF"],
        measure["QT"],
        measure["QG"],
        measure["Vm"]
    ])

    ## form measurement index vectors
    idx_zPF = idx["idx_zPF"]
    idx_zPT = idx["idx_zPT"]
    idx_zPG = idx["idx_zPG"]
    idx_zVa = idx["idx_zVa"]
    idx_zQF = idx["idx_zQF"]
    idx_zQT = idx["idx_zQT"]
    idx_zQG = idx["idx_zQG"]
    idx_zVm = idx["idx_zVm"]

    ## get R inverse matrix
    sigma_vector = [
        sigma["sigma_PF"] * ones(idx_zPF.shape[0]),
        sigma["sigma_PT"] * ones(idx_zPT.shape[0]),
        sigma["sigma_PG"] * ones(idx_zPG.shape[0]),
        sigma["sigma_Va"] * ones(idx_zVa.shape[0]),
        sigma["sigma_QF"] * ones(idx_zQF.shape[0]),
        sigma["sigma_QT"] * ones(idx_zQT.shape[0]),
        sigma["sigma_QG"] * ones(idx_zQG.shape[0]),
        sigma["sigma_Vm"] * ones(idx_zVm.shape[0])
    ] # NOTE: zero-valued elements of simga are skipped
    sigma_square = power(sigma_vector, 2)

    rsig = range(len(sigma_square))
    Rinv = csr_matrix((1.0 / sigma_square, (rsig, rsig)))

    ## do Newton iterations
    while (not converged and i < max_it):
        ## update iteration counter
        i += 1

        ## --- compute estimated measurement ---
        Sfe = V[f] * conj(Yf * V)
        Ste = V[t] * conj(Yt * V)
        ## compute net injection at generator buses
        gbus = gen[:, GEN_BUS]
        Sgbus = V[gbus] * conj(Ybus[gbus, :] * V)
        Sgen = Sgbus * baseMVA + (bus[gbus, PD] + j*bus[gbus, QD])   ## inj S + local Sd
        Sgen = Sgen / baseMVA
        z_est = array([       # NOTE: all are p.u. values
            Sfe[idx_zPF].real,
            Ste[idx_zPT].real,
            Sgen[idx_zPG].real,
            angle(V[idx_zVa]),
            Sfe[idx_zQF].imag,
            Ste[idx_zQT].imag,
            Sgen[idx_zQG].imag,
            abs(V[idx_zVm])
        ])

        ## --- get H matrix ---
        dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)
        dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, _, _ = dSbr_dV(branch, Yf, Yt, V)
    #     genbus_row = findBusRowByIdx(bus, gbus)
        genbus_row = gbus  ## rdz, this should be fine if using internal bus numbering

        ## get sub-matrix of H relating to line flow
        dPF_dVa = dSf_dVa.real # from end
        dQF_dVa = dSf_dVa.imag
        dPF_dVm = dSf_dVm.real
        dQF_dVm = dSf_dVm.imag
        dPT_dVa = dSt_dVa.real # to end
        dQT_dVa = dSt_dVa.imag
        dPT_dVm = dSt_dVm.real
        dQT_dVm = dSt_dVm.imag
        ## get sub-matrix of H relating to generator output
        dPG_dVa = dSbus_dVa[genbus_row, :].real
        dQG_dVa = dSbus_dVa[genbus_row, :].imag
        dPG_dVm = dSbus_dVm[genbus_row, :].real
        dQG_dVm = dSbus_dVm[genbus_row, :].imag
        ## get sub-matrix of H relating to voltage angle
        dVa_dVa = csr_matrix((ones(nb), (range(nb), range(nb))))
        dVa_dVm = csr_matrix((nb, nb))
        ## get sub-matrix of H relating to voltage magnitude
        dVm_dVa = csr_matrix((nb, nb))
        dVm_dVm = csr_matrix((ones(nb), (range(nb), range(nb))))

        h = [(col(idx_zPF), dPF_dVa, dPF_dVm),
             (col(idx_zPT), dPT_dVa, dPT_dVm),
             (col(idx_zPG), dPG_dVa, dPG_dVm),
             (col(idx_zVa), dVa_dVa, dVa_dVm),
             (col(idx_zQF), dQF_dVa, dQF_dVm),
             (col(idx_zQT), dQT_dVa, dQT_dVm),
             (col(idx_zQG), dQG_dVa, dQG_dVm),
             (col(idx_zVm), dVm_dVa, dVm_dVm)]

        H = vstack([hstack([dVa[idx, nonref], dVm[idx, nonref]])
                    for idx, dVa, dVm in h if len(idx) > 0 ])

        ## compute update step
        J = H.T * Rinv * H
        F = H.T * Rinv * (z - z_est) # evalute F(x)
        dx = spsolve(J, F)

        ## check for convergence
        normF = linalg.norm(F, Inf)
        if verbose > 1:
            print '\niteration [#3d]\t\tnorm of mismatch: #10.3e' % (i, normF)

        if normF < tol:
            converged = True

        ## update voltage
        Va[nonref] = Va[nonref] + dx[:nonref.shape[0]]
        Vm[nonref] = Vm[nonref] + dx[nonref.shape[0]:2 * nonref.shape[0]]
        V = Vm * exp(j * Va)   # NOTE: angle is in radians in pf solver, but in degree in case data
        Vm = abs(V)            ## update Vm and Va again in case
        Va = angle(V)          ## we wrapped around with a negative Vm

    iterNum = i

    ## get weighted sum squares of error
    error_sqrsum = sum((z - z_est)**2 / sigma_square)

    return V, converged, iterNum, z, z_est, error_sqrsum


def col(seq):
    return [[k] for k in seq]
