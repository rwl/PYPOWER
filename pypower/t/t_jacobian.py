# Copyright (C) 2004-2011 Power System Engineering Research Center
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

"""Numerical tests of partial derivative code.
"""

from os.path import dirname, join

from numpy import ones, conj, eye, exp, pi, array

from pypower.ppoption import ppoption
from pypower.loadcase import loadcase
from pypower.ext2int import ext2int
from pypower.runpf import runpf
from pypower.makeYbus import makeYbus
from pypower.dSbus_dV import dSbus_dV
from pypower.dSbr_dV import dSbr_dV

from pypower.idx_bus import VM, VA
from pypower.idx_brch import F_BUS, T_BUS

from pypower.t.t_begin import t_begin
from pypower.t.t_end import t_end
from pypower.t.t_is import t_is

import pypower.api


def t_jacobian(quiet=False):
    """Numerical tests of partial derivative code.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    t_begin(12, quiet)

    ppdir = dirname(pypower.api.__file__)
    casefile = join(ppdir, 'case30')

    ## run powerflow to get solved case
    ppopt = ppoption(VERBOSE=0, OUT_ALL=0)
    ppc = loadcase(casefile, return_as_dict=True)

    baseMVA, bus, gen, branch, _, _ = runpf(ppc, ppopt)

    ## switch to internal bus numbering and build admittance matrices
    _, bus, gen, branch = ext2int(bus, gen, branch)
    Ybus, Yf, Yt = makeYbus(baseMVA, bus, branch)
    Ybus_full = Ybus.todense()
    Yf_full   = Yf.todense()
    Yt_full   = Yt.todense()
    Vm = bus[:, VM]
    Va = bus[:, VA] * (pi / 180)
    V = Vm * exp(1j * Va)
    f = branch[:, F_BUS].astype(int)       ## list of "from" buses
    t = branch[:, T_BUS].astype(int)       ## list of "to" buses
    #nl = len(f)
    nb = len(V)
    pert = 1e-8

    Vm = array([Vm]).T  # column array
    Va = array([Va]).T  # column array
    Vc = array([V]).T   # column array

    ##-----  check dSbus_dV code  -----
    ## full matrices
    dSbus_dVm_full, dSbus_dVa_full = dSbus_dV(Ybus_full, V)

    ## sparse matrices
    dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)
    dSbus_dVm_sp = dSbus_dVm.todense()
    dSbus_dVa_sp = dSbus_dVa.todense()

    ## compute numerically to compare
    Vmp = (Vm * ones((1, nb)) + pert*eye(nb)) * (exp(1j * Va) * ones((1, nb)))
    Vap = (Vm * ones((1, nb))) * (exp(1j * (Va*ones((1, nb)) + pert*eye(nb))))
    num_dSbus_dVm = (Vmp * conj(Ybus * Vmp) - Vc * ones((1, nb)) * conj(Ybus * Vc * ones((1, nb)))) / pert
    num_dSbus_dVa = (Vap * conj(Ybus * Vap) - Vc * ones((1, nb)) * conj(Ybus * Vc * ones((1, nb)))) / pert

    t_is(dSbus_dVm_sp, num_dSbus_dVm, 5, 'dSbus_dVm (sparse)')
    t_is(dSbus_dVa_sp, num_dSbus_dVa, 5, 'dSbus_dVa (sparse)')
    t_is(dSbus_dVm_full, num_dSbus_dVm, 5, 'dSbus_dVm (full)')
    t_is(dSbus_dVa_full, num_dSbus_dVa, 5, 'dSbus_dVa (full)')

    ##-----  check dSbr_dV code  -----
    ## full matrices
    dSf_dVa_full, dSf_dVm_full, dSt_dVa_full, dSt_dVm_full, _, _ = \
            dSbr_dV(branch, Yf_full, Yt_full, V)

    ## sparse matrices
    dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, _, _ = dSbr_dV(branch, Yf, Yt, V)
    dSf_dVa_sp = dSf_dVa.todense()
    dSf_dVm_sp = dSf_dVm.todense()
    dSt_dVa_sp = dSt_dVa.todense()
    dSt_dVm_sp = dSt_dVm.todense()

    ## compute numerically to compare
    Vmpf = Vmp[f, :]
    Vapf = Vap[f, :]
    Vmpt = Vmp[t, :]
    Vapt = Vap[t, :]
    Sf2 = (Vc[f] * ones((1, nb))) * conj(Yf * Vc * ones((1, nb)))
    St2 = (Vc[t] * ones((1, nb))) * conj(Yt * Vc * ones((1, nb)))
    Smpf = Vmpf * conj(Yf * Vmp)
    Sapf = Vapf * conj(Yf * Vap)
    Smpt = Vmpt * conj(Yt * Vmp)
    Sapt = Vapt * conj(Yt * Vap)

    num_dSf_dVm = (Smpf - Sf2) / pert
    num_dSf_dVa = (Sapf - Sf2) / pert
    num_dSt_dVm = (Smpt - St2) / pert
    num_dSt_dVa = (Sapt - St2) / pert

    t_is(dSf_dVm_sp, num_dSf_dVm, 5, 'dSf_dVm (sparse)')
    t_is(dSf_dVa_sp, num_dSf_dVa, 5, 'dSf_dVa (sparse)')
    t_is(dSt_dVm_sp, num_dSt_dVm, 5, 'dSt_dVm (sparse)')
    t_is(dSt_dVa_sp, num_dSt_dVa, 5, 'dSt_dVa (sparse)')
    t_is(dSf_dVm_full, num_dSf_dVm, 5, 'dSf_dVm (full)')
    t_is(dSf_dVa_full, num_dSf_dVa, 5, 'dSf_dVa (full)')
    t_is(dSt_dVm_full, num_dSt_dVm, 5, 'dSt_dVm (full)')
    t_is(dSt_dVa_full, num_dSt_dVa, 5, 'dSt_dVa (full)')

    t_end()


if __name__ == "__main__":
    t_jacobian(quiet=False)
