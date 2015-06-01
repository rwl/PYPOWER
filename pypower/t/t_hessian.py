# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Numerical tests of 2nd derivative code.
"""

from numpy import pi, random, ones, zeros, exp
from scipy.sparse import csr_matrix as sparse

from pypower.case30 import case30
from pypower.ppoption import ppoption
from pypower.runpf import runpf
from pypower.ext2int import ext2int1
from pypower.makeYbus import makeYbus
from pypower.dSbus_dV import dSbus_dV
from pypower.d2Sbus_dV2 import d2Sbus_dV2
from pypower.dSbr_dV import dSbr_dV
from pypower.d2Sbr_dV2 import d2Sbr_dV2
from pypower.dIbr_dV import dIbr_dV
from pypower.d2Ibr_dV2 import d2Ibr_dV2
from pypower.dAbr_dV import dAbr_dV
from pypower.d2ASbr_dV2 import d2ASbr_dV2
from pypower.d2AIbr_dV2 import d2AIbr_dV2

from pypower.idx_bus import VM, VA
from pypower.idx_brch import T_BUS, F_BUS

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end


def t_hessian(quiet=False):
    """Numerical tests of 2nd derivative code.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    t_begin(44, quiet)

    ## run powerflow to get solved case
    ppopt = ppoption(VERBOSE=0, OUT_ALL=0)
    results, _ = runpf(case30(), ppopt)
    baseMVA, bus, gen, branch = \
        results['baseMVA'], results['bus'], results['gen'], results['branch']

    ## switch to internal bus numbering and build admittance matrices
    _, bus, gen, branch = ext2int1(bus, gen, branch)
    Ybus, Yf, Yt = makeYbus(baseMVA, bus, branch)
    Vm = bus[:, VM]
    Va = bus[:, VA] * (pi / 180)
    V = Vm * exp(1j * Va)
    f = branch[:, F_BUS]       ## list of "from" buses
    t = branch[:, T_BUS]       ## list of "to" buses
    nl = len(f)
    nb = len(V)
    Cf = sparse((ones(nl), (range(nl), f)), (nl, nb))  ## connection matrix for line & from buses
    Ct = sparse((ones(nl), (range(nl), t)), (nl, nb))  ## connection matrix for line & to buses
    pert = 1e-8

    ##-----  check d2Sbus_dV2 code  -----
    t = ' - d2Sbus_dV2 (complex power injections)'
    lam = 10 * random.rand(nb)
    num_Haa = zeros((nb, nb), complex)
    num_Hav = zeros((nb, nb), complex)
    num_Hva = zeros((nb, nb), complex)
    num_Hvv = zeros((nb, nb), complex)
    dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)
    Haa, Hav, Hva, Hvv = d2Sbus_dV2(Ybus, V, lam)
    for i in range(nb):
        Vap = V.copy()
        Vap[i] = Vm[i] * exp(1j * (Va[i] + pert))
        dSbus_dVm_ap, dSbus_dVa_ap = dSbus_dV(Ybus, Vap)
        num_Haa[:, i] = (dSbus_dVa_ap - dSbus_dVa).T * lam / pert
        num_Hva[:, i] = (dSbus_dVm_ap - dSbus_dVm).T * lam / pert

        Vmp = V.copy()
        Vmp[i] = (Vm[i] + pert) * exp(1j * Va[i])
        dSbus_dVm_mp, dSbus_dVa_mp = dSbus_dV(Ybus, Vmp)
        num_Hav[:, i] = (dSbus_dVa_mp - dSbus_dVa).T * lam / pert
        num_Hvv[:, i] = (dSbus_dVm_mp - dSbus_dVm).T * lam / pert

    t_is(Haa.todense(), num_Haa, 4, ['Haa', t])
    t_is(Hav.todense(), num_Hav, 4, ['Hav', t])
    t_is(Hva.todense(), num_Hva, 4, ['Hva', t])
    t_is(Hvv.todense(), num_Hvv, 4, ['Hvv', t])

    ##-----  check d2Sbr_dV2 code  -----
    t = ' - d2Sbr_dV2 (complex power flows)'
    lam = 10 * random.rand(nl)
    # lam = [1 zeros(nl-1, 1)]
    num_Gfaa = zeros((nb, nb), complex)
    num_Gfav = zeros((nb, nb), complex)
    num_Gfva = zeros((nb, nb), complex)
    num_Gfvv = zeros((nb, nb), complex)
    num_Gtaa = zeros((nb, nb), complex)
    num_Gtav = zeros((nb, nb), complex)
    num_Gtva = zeros((nb, nb), complex)
    num_Gtvv = zeros((nb, nb), complex)
    dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, _, _ = dSbr_dV(branch, Yf, Yt, V)
    Gfaa, Gfav, Gfva, Gfvv = d2Sbr_dV2(Cf, Yf, V, lam)
    Gtaa, Gtav, Gtva, Gtvv = d2Sbr_dV2(Ct, Yt, V, lam)
    for i in range(nb):
        Vap = V.copy()
        Vap[i] = Vm[i] * exp(1j * (Va[i] + pert))
        dSf_dVa_ap, dSf_dVm_ap, dSt_dVa_ap, dSt_dVm_ap, Sf_ap, St_ap = \
            dSbr_dV(branch, Yf, Yt, Vap)
        num_Gfaa[:, i] = (dSf_dVa_ap - dSf_dVa).T * lam / pert
        num_Gfva[:, i] = (dSf_dVm_ap - dSf_dVm).T * lam / pert
        num_Gtaa[:, i] = (dSt_dVa_ap - dSt_dVa).T * lam / pert
        num_Gtva[:, i] = (dSt_dVm_ap - dSt_dVm).T * lam / pert

        Vmp = V.copy()
        Vmp[i] = (Vm[i] + pert) * exp(1j * Va[i])
        dSf_dVa_mp, dSf_dVm_mp, dSt_dVa_mp, dSt_dVm_mp, Sf_mp, St_mp = \
            dSbr_dV(branch, Yf, Yt, Vmp)
        num_Gfav[:, i] = (dSf_dVa_mp - dSf_dVa).T * lam / pert
        num_Gfvv[:, i] = (dSf_dVm_mp - dSf_dVm).T * lam / pert
        num_Gtav[:, i] = (dSt_dVa_mp - dSt_dVa).T * lam / pert
        num_Gtvv[:, i] = (dSt_dVm_mp - dSt_dVm).T * lam / pert

    t_is(Gfaa.todense(), num_Gfaa, 4, ['Gfaa', t])
    t_is(Gfav.todense(), num_Gfav, 4, ['Gfav', t])
    t_is(Gfva.todense(), num_Gfva, 4, ['Gfva', t])
    t_is(Gfvv.todense(), num_Gfvv, 4, ['Gfvv', t])

    t_is(Gtaa.todense(), num_Gtaa, 4, ['Gtaa', t])
    t_is(Gtav.todense(), num_Gtav, 4, ['Gtav', t])
    t_is(Gtva.todense(), num_Gtva, 4, ['Gtva', t])
    t_is(Gtvv.todense(), num_Gtvv, 4, ['Gtvv', t])

    ##-----  check d2Ibr_dV2 code  -----
    t = ' - d2Ibr_dV2 (complex currents)'
    lam = 10 * random.rand(nl)
    # lam = [1, zeros(nl-1)]
    num_Gfaa = zeros((nb, nb), complex)
    num_Gfav = zeros((nb, nb), complex)
    num_Gfva = zeros((nb, nb), complex)
    num_Gfvv = zeros((nb, nb), complex)
    num_Gtaa = zeros((nb, nb), complex)
    num_Gtav = zeros((nb, nb), complex)
    num_Gtva = zeros((nb, nb), complex)
    num_Gtvv = zeros((nb, nb), complex)
    dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, _, _ = dIbr_dV(branch, Yf, Yt, V)
    Gfaa, Gfav, Gfva, Gfvv = d2Ibr_dV2(Yf, V, lam)

    Gtaa, Gtav, Gtva, Gtvv = d2Ibr_dV2(Yt, V, lam)
    for i in range(nb):
        Vap = V.copy()
        Vap[i] = Vm[i] * exp(1j * (Va[i] + pert))
        dIf_dVa_ap, dIf_dVm_ap, dIt_dVa_ap, dIt_dVm_ap, If_ap, It_ap = \
            dIbr_dV(branch, Yf, Yt, Vap)
        num_Gfaa[:, i] = (dIf_dVa_ap - dIf_dVa).T * lam / pert
        num_Gfva[:, i] = (dIf_dVm_ap - dIf_dVm).T * lam / pert
        num_Gtaa[:, i] = (dIt_dVa_ap - dIt_dVa).T * lam / pert
        num_Gtva[:, i] = (dIt_dVm_ap - dIt_dVm).T * lam / pert

        Vmp = V.copy()
        Vmp[i] = (Vm[i] + pert) * exp(1j * Va[i])
        dIf_dVa_mp, dIf_dVm_mp, dIt_dVa_mp, dIt_dVm_mp, If_mp, It_mp = \
            dIbr_dV(branch, Yf, Yt, Vmp)
        num_Gfav[:, i] = (dIf_dVa_mp - dIf_dVa).T * lam / pert
        num_Gfvv[:, i] = (dIf_dVm_mp - dIf_dVm).T * lam / pert
        num_Gtav[:, i] = (dIt_dVa_mp - dIt_dVa).T * lam / pert
        num_Gtvv[:, i] = (dIt_dVm_mp - dIt_dVm).T * lam / pert

    t_is(Gfaa.todense(), num_Gfaa, 4, ['Gfaa', t])
    t_is(Gfav.todense(), num_Gfav, 4, ['Gfav', t])
    t_is(Gfva.todense(), num_Gfva, 4, ['Gfva', t])
    t_is(Gfvv.todense(), num_Gfvv, 4, ['Gfvv', t])

    t_is(Gtaa.todense(), num_Gtaa, 4, ['Gtaa', t])
    t_is(Gtav.todense(), num_Gtav, 4, ['Gtav', t])
    t_is(Gtva.todense(), num_Gtva, 4, ['Gtva', t])
    t_is(Gtvv.todense(), num_Gtvv, 4, ['Gtvv', t])

    ##-----  check d2ASbr_dV2 code  -----
    t = ' - d2ASbr_dV2 (squared apparent power flows)'
    lam = 10 * random.rand(nl)
    # lam = [1 zeros(nl-1, 1)]
    num_Gfaa = zeros((nb, nb), complex)
    num_Gfav = zeros((nb, nb), complex)
    num_Gfva = zeros((nb, nb), complex)
    num_Gfvv = zeros((nb, nb), complex)
    num_Gtaa = zeros((nb, nb), complex)
    num_Gtav = zeros((nb, nb), complex)
    num_Gtva = zeros((nb, nb), complex)
    num_Gtvv = zeros((nb, nb), complex)
    dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St = dSbr_dV(branch, Yf, Yt, V)
    dAf_dVa, dAf_dVm, dAt_dVa, dAt_dVm = \
                            dAbr_dV(dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St)
    Gfaa, Gfav, Gfva, Gfvv = d2ASbr_dV2(dSf_dVa, dSf_dVm, Sf, Cf, Yf, V, lam)
    Gtaa, Gtav, Gtva, Gtvv = d2ASbr_dV2(dSt_dVa, dSt_dVm, St, Ct, Yt, V, lam)
    for i in range(nb):
        Vap = V.copy()
        Vap[i] = Vm[i] * exp(1j * (Va[i] + pert))
        dSf_dVa_ap, dSf_dVm_ap, dSt_dVa_ap, dSt_dVm_ap, Sf_ap, St_ap = \
            dSbr_dV(branch, Yf, Yt, Vap)
        dAf_dVa_ap, dAf_dVm_ap, dAt_dVa_ap, dAt_dVm_ap = \
            dAbr_dV(dSf_dVa_ap, dSf_dVm_ap, dSt_dVa_ap, dSt_dVm_ap, Sf_ap, St_ap)
        num_Gfaa[:, i] = (dAf_dVa_ap - dAf_dVa).T * lam / pert
        num_Gfva[:, i] = (dAf_dVm_ap - dAf_dVm).T * lam / pert
        num_Gtaa[:, i] = (dAt_dVa_ap - dAt_dVa).T * lam / pert
        num_Gtva[:, i] = (dAt_dVm_ap - dAt_dVm).T * lam / pert

        Vmp = V.copy()
        Vmp[i] = (Vm[i] + pert) * exp(1j * Va[i])
        dSf_dVa_mp, dSf_dVm_mp, dSt_dVa_mp, dSt_dVm_mp, Sf_mp, St_mp = \
            dSbr_dV(branch, Yf, Yt, Vmp)
        dAf_dVa_mp, dAf_dVm_mp, dAt_dVa_mp, dAt_dVm_mp = \
            dAbr_dV(dSf_dVa_mp, dSf_dVm_mp, dSt_dVa_mp, dSt_dVm_mp, Sf_mp, St_mp)
        num_Gfav[:, i] = (dAf_dVa_mp - dAf_dVa).T * lam / pert
        num_Gfvv[:, i] = (dAf_dVm_mp - dAf_dVm).T * lam / pert
        num_Gtav[:, i] = (dAt_dVa_mp - dAt_dVa).T * lam / pert
        num_Gtvv[:, i] = (dAt_dVm_mp - dAt_dVm).T * lam / pert

    t_is(Gfaa.todense(), num_Gfaa, 2, ['Gfaa', t])
    t_is(Gfav.todense(), num_Gfav, 2, ['Gfav', t])
    t_is(Gfva.todense(), num_Gfva, 2, ['Gfva', t])
    t_is(Gfvv.todense(), num_Gfvv, 2, ['Gfvv', t])

    t_is(Gtaa.todense(), num_Gtaa, 2, ['Gtaa', t])
    t_is(Gtav.todense(), num_Gtav, 2, ['Gtav', t])
    t_is(Gtva.todense(), num_Gtva, 2, ['Gtva', t])
    t_is(Gtvv.todense(), num_Gtvv, 2, ['Gtvv', t])

    ##-----  check d2ASbr_dV2 code  -----
    t = ' - d2ASbr_dV2 (squared real power flows)'
    lam = 10 * random.rand(nl)
    # lam = [1 zeros(nl-1, 1)]
    num_Gfaa = zeros((nb, nb), complex)
    num_Gfav = zeros((nb, nb), complex)
    num_Gfva = zeros((nb, nb), complex)
    num_Gfvv = zeros((nb, nb), complex)
    num_Gtaa = zeros((nb, nb), complex)
    num_Gtav = zeros((nb, nb), complex)
    num_Gtva = zeros((nb, nb), complex)
    num_Gtvv = zeros((nb, nb), complex)
    dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St = dSbr_dV(branch, Yf, Yt, V)
    dAf_dVa, dAf_dVm, dAt_dVa, dAt_dVm = \
           dAbr_dV(dSf_dVa.real, dSf_dVm.real, dSt_dVa.real, dSt_dVm.real, Sf.real, St.real)
    Gfaa, Gfav, Gfva, Gfvv = d2ASbr_dV2(dSf_dVa.real, dSf_dVm.real, Sf.real, Cf, Yf, V, lam)
    Gtaa, Gtav, Gtva, Gtvv = d2ASbr_dV2(dSt_dVa.real, dSt_dVm.real, St.real, Ct, Yt, V, lam)
    for i in range(nb):
        Vap = V.copy()
        Vap[i] = Vm[i] * exp(1j * (Va[i] + pert))
        dSf_dVa_ap, dSf_dVm_ap, dSt_dVa_ap, dSt_dVm_ap, Sf_ap, St_ap = \
            dSbr_dV(branch, Yf, Yt, Vap)
        dAf_dVa_ap, dAf_dVm_ap, dAt_dVa_ap, dAt_dVm_ap = \
            dAbr_dV(dSf_dVa_ap.real, dSf_dVm_ap.real, dSt_dVa_ap.real, dSt_dVm_ap.real, Sf_ap.real, St_ap.real)
        num_Gfaa[:, i] = (dAf_dVa_ap - dAf_dVa).T * lam / pert
        num_Gfva[:, i] = (dAf_dVm_ap - dAf_dVm).T * lam / pert
        num_Gtaa[:, i] = (dAt_dVa_ap - dAt_dVa).T * lam / pert
        num_Gtva[:, i] = (dAt_dVm_ap - dAt_dVm).T * lam / pert

        Vmp = V.copy()
        Vmp[i] = (Vm[i] + pert) * exp(1j * Va[i])
        dSf_dVa_mp, dSf_dVm_mp, dSt_dVa_mp, dSt_dVm_mp, Sf_mp, St_mp = \
            dSbr_dV(branch, Yf, Yt, Vmp)
        dAf_dVa_mp, dAf_dVm_mp, dAt_dVa_mp, dAt_dVm_mp = \
            dAbr_dV(dSf_dVa_mp.real, dSf_dVm_mp.real, dSt_dVa_mp.real, dSt_dVm_mp.real, Sf_mp.real, St_mp.real)
        num_Gfav[:, i] = (dAf_dVa_mp - dAf_dVa).T * lam / pert
        num_Gfvv[:, i] = (dAf_dVm_mp - dAf_dVm).T * lam / pert
        num_Gtav[:, i] = (dAt_dVa_mp - dAt_dVa).T * lam / pert
        num_Gtvv[:, i] = (dAt_dVm_mp - dAt_dVm).T * lam / pert

    t_is(Gfaa.todense(), num_Gfaa, 2, ['Gfaa', t])
    t_is(Gfav.todense(), num_Gfav, 2, ['Gfav', t])
    t_is(Gfva.todense(), num_Gfva, 2, ['Gfva', t])
    t_is(Gfvv.todense(), num_Gfvv, 2, ['Gfvv', t])

    t_is(Gtaa.todense(), num_Gtaa, 2, ['Gtaa', t])
    t_is(Gtav.todense(), num_Gtav, 2, ['Gtav', t])
    t_is(Gtva.todense(), num_Gtva, 2, ['Gtva', t])
    t_is(Gtvv.todense(), num_Gtvv, 2, ['Gtvv', t])

    ##-----  check d2AIbr_dV2 code  -----
    t = ' - d2AIbr_dV2 (squared current magnitudes)'
    lam = 10 * random.rand(nl)
    # lam = [1 zeros(nl-1, 1)]
    num_Gfaa = zeros((nb, nb), complex)
    num_Gfav = zeros((nb, nb), complex)
    num_Gfva = zeros((nb, nb), complex)
    num_Gfvv = zeros((nb, nb), complex)
    num_Gtaa = zeros((nb, nb), complex)
    num_Gtav = zeros((nb, nb), complex)
    num_Gtva = zeros((nb, nb), complex)
    num_Gtvv = zeros((nb, nb), complex)
    dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It = dIbr_dV(branch, Yf, Yt, V)
    dAf_dVa, dAf_dVm, dAt_dVa, dAt_dVm = \
                            dAbr_dV(dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It)
    Gfaa, Gfav, Gfva, Gfvv = d2AIbr_dV2(dIf_dVa, dIf_dVm, If, Yf, V, lam)
    Gtaa, Gtav, Gtva, Gtvv = d2AIbr_dV2(dIt_dVa, dIt_dVm, It, Yt, V, lam)
    for i in range(nb):
        Vap = V.copy()
        Vap[i] = Vm[i] * exp(1j * (Va[i] + pert))
        dIf_dVa_ap, dIf_dVm_ap, dIt_dVa_ap, dIt_dVm_ap, If_ap, It_ap = \
            dIbr_dV(branch, Yf, Yt, Vap)
        dAf_dVa_ap, dAf_dVm_ap, dAt_dVa_ap, dAt_dVm_ap = \
            dAbr_dV(dIf_dVa_ap, dIf_dVm_ap, dIt_dVa_ap, dIt_dVm_ap, If_ap, It_ap)
        num_Gfaa[:, i] = (dAf_dVa_ap - dAf_dVa).T * lam / pert
        num_Gfva[:, i] = (dAf_dVm_ap - dAf_dVm).T * lam / pert
        num_Gtaa[:, i] = (dAt_dVa_ap - dAt_dVa).T * lam / pert
        num_Gtva[:, i] = (dAt_dVm_ap - dAt_dVm).T * lam / pert

        Vmp = V.copy()
        Vmp[i] = (Vm[i] + pert) * exp(1j * Va[i])
        dIf_dVa_mp, dIf_dVm_mp, dIt_dVa_mp, dIt_dVm_mp, If_mp, It_mp = \
            dIbr_dV(branch, Yf, Yt, Vmp)
        dAf_dVa_mp, dAf_dVm_mp, dAt_dVa_mp, dAt_dVm_mp = \
            dAbr_dV(dIf_dVa_mp, dIf_dVm_mp, dIt_dVa_mp, dIt_dVm_mp, If_mp, It_mp)
        num_Gfav[:, i] = (dAf_dVa_mp - dAf_dVa).T * lam / pert
        num_Gfvv[:, i] = (dAf_dVm_mp - dAf_dVm).T * lam / pert
        num_Gtav[:, i] = (dAt_dVa_mp - dAt_dVa).T * lam / pert
        num_Gtvv[:, i] = (dAt_dVm_mp - dAt_dVm).T * lam / pert

    t_is(Gfaa.todense(), num_Gfaa, 3, ['Gfaa', t])
    t_is(Gfav.todense(), num_Gfav, 3, ['Gfav', t])
    t_is(Gfva.todense(), num_Gfva, 3, ['Gfva', t])
    t_is(Gfvv.todense(), num_Gfvv, 2, ['Gfvv', t])

    t_is(Gtaa.todense(), num_Gtaa, 3, ['Gtaa', t])
    t_is(Gtav.todense(), num_Gtav, 3, ['Gtav', t])
    t_is(Gtva.todense(), num_Gtva, 3, ['Gtva', t])
    t_is(Gtvv.todense(), num_Gtvv, 2, ['Gtvv', t])

    t_end()


if __name__ == '__main__':
    t_hessian(quiet=False)
