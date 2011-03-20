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

from numpy import \
    array, ones, zeros, nonzero, r_, sort, exp, pi, diff, real, imag

from scipy.sparse import csr_matrix

from idx_bus import *
from idx_gen import *
from idx_brch import *
from idx_cost import *

from isload import isload
from run_userfcn import run_userfcn
from ppoption import ppoption

def printpf(baseMVA, bus=None, gen=None, branch=None, f=None, success=None,
            et=None, fd=None, ppopt=None):
    """Prints power flow results.

    Prints power flow and optimal power flow results to FD (a file
    descriptor which defaults to STDOUT), with the details of what
    gets printed controlled by the optional ppopt argument, which is a
    PYPOWER options vector (see PPOPTION for details).

    The data can either be supplied in a single RESULTS struct, or
    in the individual arguments: BASEMVA, BUS, GEN, BRANCH, F, SUCCESS
    and ET, where F is the OPF objective function value, SUCCESS is
    true if the solution converged and false otherwise, and ET is the
    elapsed time for the computation in seconds. If F is given, it is
    assumed that the output is from an OPF run, otherwise it is assumed
    to be a simple power flow run.

    Examples:
        ppopt = ppoptions('OUT_GEN', 1, 'OUT_BUS', 0, 'OUT_BRANCH', 0)
        fd = open(fname, 'w+b')
        results = runopf(mpc)
        printpf(results)
        printpf(results, fd)
        printpf(results, fd, mpopt)
        printpf(baseMVA, bus, gen, branch, f, success, et)
        printpf(baseMVA, bus, gen, branch, f, success, et, fd)
        printpf(baseMVA, bus, gen, branch, f, success, et, fd, mpopt)
        fd.close()

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ##----- initialization -----
    ## default arguments
    if isinstance(baseMVA, dict):
        have_results_struct = 1
        results = baseMVA
        if gen is None:
            ppopt = ppoption   ## use default options
        else:
            ppopt = gen
        if ppopt['OUT_ALL'] == 0 and ppopt['OUT_RAW'] == 0:
            return     ## nothin' to see here, bail out now
        if bus is None:
            fd = 1         ## print to stdio by default
        else:
            fd = bus
        baseMVA, bus, gen, branch, success, et = \
            results["baseMVA"], results["bus"], results["gen"], \
            results["branch"], results["success"], results["et"]
        if results.has_key('f') and any(results["f"]):
            f = results["f"]
        else:
            f = array([])
    else:
        have_results_struct = 0
        if ppopt is None:
            ppopt = ppoption   ## use default options
            if fd is None:
                fd = 1         ## print to stdio by default
        if ppopt[32] == 0 & ppopt[43] == 0:     ## OUT_ALL or OUT_RAW
            return     ## nothin' to see here, bail out now

    isOPF = any(f)    ## FALSE -> only simple PF data, TRUE -> OPF data

    ## options
    isDC            = ppopt[10]        ## use DC formulation?
    OUT_ALL         = ppopt[32]
    OUT_ANY         = OUT_ALL == 1     ## set to true if any pretty output is to be generated
    OUT_SYS_SUM     = OUT_ALL == 1 | (OUT_ALL == -1 & ppopt[33])
    OUT_AREA_SUM    = OUT_ALL == 1 | (OUT_ALL == -1 & ppopt[34])
    OUT_BUS         = OUT_ALL == 1 | (OUT_ALL == -1 & ppopt[35])
    OUT_BRANCH      = OUT_ALL == 1 | (OUT_ALL == -1 & ppopt[36])
    OUT_GEN         = OUT_ALL == 1 | (OUT_ALL == -1 & ppopt[37])
    OUT_ANY         = OUT_ANY | (OUT_ALL == -1 &
                        (OUT_SYS_SUM | OUT_AREA_SUM | OUT_BUS |
                         OUT_BRANCH | OUT_GEN))
    if OUT_ALL == -1:
        OUT_ALL_LIM = ppopt[38]
    elif OUT_ALL == 1:
        OUT_ALL_LIM = 2
    else:
        OUT_ALL_LIM = 0

    OUT_ANY         = OUT_ANY | OUT_ALL_LIM >= 1
    if OUT_ALL_LIM == -1:
        OUT_V_LIM       = ppopt[39]
        OUT_LINE_LIM    = ppopt[40]
        OUT_PG_LIM      = ppopt[41]
        OUT_QG_LIM      = ppopt[42]
    else:
        OUT_V_LIM       = OUT_ALL_LIM
        OUT_LINE_LIM    = OUT_ALL_LIM
        OUT_PG_LIM      = OUT_ALL_LIM
        OUT_QG_LIM      = OUT_ALL_LIM

    OUT_ANY         = OUT_ANY | (OUT_ALL_LIM == -1 & (OUT_V_LIM | OUT_LINE_LIM | OUT_PG_LIM | OUT_QG_LIM))
    OUT_RAW         = ppopt[43]
    ptol = 1e-6        ## tolerance for displaying shadow prices

    ## create map of external bus numbers to bus indices
    i2e = bus[:, BUS_I]
    e2i = csr_matrix((max(i2e), 1))
    e2i[i2e] = range(bus.shape[0])

    ## sizes of things
    nb = bus.shape[0]      ## number of buses
    nl = branch.shape[0]   ## number of branches
    ng = gen.shape[0]      ## number of generators

    ## zero out some data to make printout consistent for DC case
    if isDC:
        bus[:, r_[QD, BS]]          = zeros((nb, 2))
        gen[:, r_[QG, QMAX, QMIN]]  = zeros((ng, 3))
        branch[:, r_[BR_R, BR_B]]   = zeros((nl, 2))

    ## parameters
    ties = nonzero(bus[e2i[branch[:, F_BUS]], BUS_AREA] !=
                   bus[e2i[branch[:, T_BUS]], BUS_AREA])
                            ## area inter-ties
    tap = ones(nl)                           ## default tap ratio = 1 for lines
    xfmr = nonzero(branch[:, TAP])           ## indices of transformers
    tap[xfmr] = branch[xfmr, TAP]            ## include transformer tap ratios
    tap = tap * exp(1j * pi / 180 * branch[:, SHIFT]) ## add phase shifters
    nzld = nonzero(bus[:, PD] | bus[:, QD])
    sorted_areas = sort(bus[:, BUS_AREA])
    ## area numbers
    s_areas = sorted_areas[r_[1, nonzero(diff(sorted_areas)) + 1]]
    nzsh = nonzero(bus[:, GS] | bus[:, BS])
    allg = nonzero( not isload(gen) )
    ong  = nonzero( gen[:, GEN_STATUS] > 0 and not isload(gen) )
    onld = nonzero( gen[:, GEN_STATUS] > 0 and     isload(gen) )
    V = bus[:, VM] * exp(-1j * pi / 180 * bus[:, VA])
    out = nonzero(branch[:, BR_STATUS] == 0)        ## out-of-service branches
    nout = len(out)
    if isDC:
        loss = zeros(nl)
    else:
        loss = baseMVA * abs(V[e2i[branch[:, F_BUS]]] / tap -
                             V[e2i[branch[:, T_BUS]]])**2 / \
                    (branch[:, BR_R] - 1j * branch[:, BR_X])

    fchg = abs(V[e2i[branch[:, F_BUS]]] / tap)**2 * branch[:, BR_B] * baseMVA / 2
    tchg = abs(V[e2i[branch[:, T_BUS]]]      )**2 * branch[:, BR_B] * baseMVA / 2
    loss[out] = zeros(nout)
    fchg[out] = zeros(nout)
    tchg[out] = zeros(nout)

    ##----- print the stuff -----
    if OUT_ANY:
        ## convergence & elapsed time
        if success:
            fd.write('\nConverged in %.2f seconds' % et)
        else:
            fd.write('\nDid not converge (%.2f seconds)\n' % et)

        ## objective function value
        if isOPF:
            fd.write('\nObjective Function Value = %.2f $/hr', f)

    if OUT_SYS_SUM:
        fd.write('\n================================================================================')
        fd.write('\n|     System Summary                                                           |')
        fd.write('\n================================================================================')
        fd.write('\n\nHow many?                How much?              P (MW)            Q (MVAr)')
        fd.write('\n---------------------    -------------------  -------------  -----------------')
        fd.write('\nBuses         %6d     Total Gen Capacity   %7.1f       %7.1f to %.1f' % (nb, sum(gen[allg, PMAX]), sum(gen[allg, QMIN]), sum(gen[allg, QMAX])))
        fd.write('\nGenerators     %5d     On-line Capacity     %7.1f       %7.1f to %.1f' % (len(allg), sum(gen[ong, PMAX]), sum(gen[ong, QMIN]), sum(gen[ong, QMAX])))
        fd.write('\nCommitted Gens %5d     Generation (actual)  %7.1f           %7.1f' % (len(ong), sum(gen[ong, PG]), sum(gen[ong, QG])))
        fd.write('\nLoads          %5d     Load                 %7.1f           %7.1f' % (len(nzld)+len(onld), sum(bus[nzld, PD])-sum(gen[onld, PG]), sum(bus[nzld, QD])-sum(gen[onld, QG])))
        fd.write('\n  Fixed        %5d       Fixed              %7.1f           %7.1f' % (len(nzld), sum(bus[nzld, PD]), sum(bus[nzld, QD])))
        fd.write('\n  Dispatchable %5d       Dispatchable       %7.1f of %-7.1f%7.1f' % (len(onld), -sum(gen[onld, PG]), -sum(gen[onld, PMIN]), -sum(gen[onld, QG])))
        fd.write('\nShunts         %5d     Shunt (inj)          %7.1f           %7.1f' % (len(nzsh),
            -sum(bus[nzsh, VM]**2 * bus[nzsh, GS]), sum(bus[nzsh, VM]**2 * bus[nzsh, BS]) ))
        fd.write('\nBranches       %5d     Losses (I^2 * Z)     %8.2f          %8.2f' % (nl, sum(loss.real), sum(loss.imag) ))
        fd.write('\nTransformers   %5d     Branch Charging (inj)     -            %7.1f' % (len(xfmr), sum(fchg) + sum(tchg) ))
        fd.write('\nInter-ties     %5d     Total Inter-tie Flow %7.1f           %7.1f' % (len(ties), sum(abs(branch[ties, PF]-branch[ties, PT])) / 2, sum(abs(branch[ties, QF]-branch[ties, QT])) / 2))
        fd.write('\nAreas          %5d' % len(s_areas))
        fd.write('\n')
        fd.write('\n                          Minimum                      Maximum')
        fd.write('\n                 -------------------------  --------------------------------')
        minv, mini = min(bus[:, VM])
        maxv, maxi = max(bus[:, VM])
        fd.write('\nVoltage Magnitude %7.3f p.u. @ bus %-4d     %7.3f p.u. @ bus %-4d' % (minv, bus[mini, BUS_I], maxv, bus[maxi, BUS_I]))
        minv, mini = min(bus[:, VA])
        maxv, maxi = max(bus[:, VA])
        fd.write('\nVoltage Angle   %8.2f deg   @ bus %-4d   %8.2f deg   @ bus %-4d' % (minv, bus[mini, BUS_I], maxv, bus[maxi, BUS_I]))
        if not isDC:
            maxv, maxi = max(loss.real)
            fd.write('\nP Losses (I^2*R)             -              %8.2f MW    @ line %d-%d', maxv, branch[maxi, F_BUS], branch[maxi, T_BUS])
            maxv, maxi = max(loss.imag)
            fd.write('\nQ Losses (I^2*X)             -              %8.2f MVAr  @ line %d-%d', maxv, branch[maxi, F_BUS], branch[maxi, T_BUS])
        if isOPF:
            minv, mini = min(bus[:, LAM_P])
            maxv, maxi = max(bus[:, LAM_P])
            fd.write('\nLambda P        %8.2f $/MWh @ bus %-4d   %8.2f $/MWh @ bus %-4d' % (minv, bus[mini, BUS_I], maxv, bus[maxi, BUS_I]))
            minv, mini = min(bus[:, LAM_Q])
            maxv, maxi = max(bus[:, LAM_Q])
            fd.write('\nLambda Q        %8.2f $/MWh @ bus %-4d   %8.2f $/MWh @ bus %-4d' % (minv, bus(mini, BUS_I), maxv, bus(maxi, BUS_I)))
        fd.write('\n')

    if OUT_AREA_SUM:
        fd.write('\n================================================================================')
        fd.write('\n|     Area Summary                                                             |')
        fd.write('\n================================================================================')
        fd.write('\nArea  # of      # of Gens        # of Loads         # of    # of   # of   # of')
        fd.write('\n Num  Buses   Total  Online   Total  Fixed  Disp    Shunt   Brchs  Xfmrs   Ties')
        fd.write('\n----  -----   -----  ------   -----  -----  -----   -----   -----  -----  -----')
        for i in range(len(s_areas)):
            a = s_areas[i]
            ib = nonzero(bus[:, BUS_AREA] == a)
            ig = nonzero(bus[e2i[gen[:, GEN_BUS]], BUS_AREA] == a & ~isload(gen))
            igon = nonzero(bus[e2i[gen[:, GEN_BUS]], BUS_AREA] == a & gen[:, GEN_STATUS] > 0 & ~isload(gen))
            ildon = nonzero(bus[e2i[gen[:, GEN_BUS]], BUS_AREA] == a & gen[:, GEN_STATUS] > 0 & isload(gen))
            inzld = nonzero(bus[:, BUS_AREA] == a & (bus[:, PD] | bus[:, QD]))
            inzsh = nonzero(bus[:, BUS_AREA] == a & (bus[:, GS] | bus[:, BS]))
            ibrch = nonzero(bus[e2i[branch[:, F_BUS]], BUS_AREA] == a & bus[e2i[branch[:, T_BUS]], BUS_AREA] == a)
            in_tie = nonzero(bus[e2i[branch[:, F_BUS]], BUS_AREA] == a & bus[e2i[branch[:, T_BUS]], BUS_AREA] != a)
            out_tie = nonzero(bus[e2i[branch[:, F_BUS]], BUS_AREA] != a & bus[e2i[branch[:, T_BUS]], BUS_AREA] == a)
            if not any(xfmr):
                nxfmr = 0
            else:
                nxfmr = len(nonzero(bus[e2i[branch[xfmr, F_BUS]], BUS_AREA] == a & bus[e2i[branch[xfmr, T_BUS]], BUS_AREA] == a))
            fd.write('\n%3d  %6d   %5d  %5d   %5d  %5d  %5d   %5d   %5d  %5d  %5d' %
                (a, len(ib), len(ig), len(igon), \
                len(inzld)+len(ildon), len(inzld), len(ildon), \
                len(inzsh), len(ibrch), nxfmr, len(in_tie)+len(out_tie)))

        fd.write('\n----  -----   -----  ------   -----  -----  -----   -----   -----  -----  -----')
        fd.write('\nTot: %6d   %5d  %5d   %5d  %5d  %5d   %5d   %5d  %5d  %5d' %
            (nb, len(allg), len(ong), len(nzld)+len(onld),
            len(nzld), len(onld), len(nzsh), nl, len(xfmr), len(ties)))
        fd.write('\n')
        fd.write('\nArea      Total Gen Capacity           On-line Gen Capacity         Generation')
        fd.write('\n Num     MW           MVAr            MW           MVAr             MW    MVAr')
        fd.write('\n----   ------  ------------------   ------  ------------------    ------  ------')
        for i in range(len(s_areas)):
            a = s_areas[i]
            ig = nonzero(bus[e2i[gen[:, GEN_BUS]], BUS_AREA] == a & ~isload(gen))
            igon = nonzero(bus[e2i[gen[:, GEN_BUS]], BUS_AREA] == a & gen[:, GEN_STATUS] > 0 & ~isload(gen))
            fd.write('\n%3d   %7.1f  %7.1f to %-7.1f  %7.1f  %7.1f to %-7.1f   %7.1f %7.1f' %
                (a, sum(gen[ig, PMAX]), sum(gen[ig, QMIN]), sum(gen[ig, QMAX]),
                sum(gen[igon, PMAX]), sum(gen[igon, QMIN]), sum(gen[igon, QMAX]),
                sum(gen[igon, PG]), sum(gen[igon, QG]) ))

        fd.write('\n----   ------  ------------------   ------  ------------------    ------  ------')
        fd.write('\nTot:  %7.1f  %7.1f to %-7.1f  %7.1f  %7.1f to %-7.1f   %7.1f %7.1f' %
                (sum(gen[allg, PMAX]), sum(gen[allg, QMIN]), sum(gen[allg, QMAX]),
                sum(gen[ong, PMAX]), sum(gen[ong, QMIN]), sum(gen[ong, QMAX]),
                sum(gen[ong, PG]), sum(gen[ong, QG]) ))
        fd.write('\n')
        fd.write('\nArea    Disp Load Cap       Disp Load         Fixed Load        Total Load')
        fd.write('\n Num      MW     MVAr       MW     MVAr       MW     MVAr       MW     MVAr')
        fd.write('\n----    ------  ------    ------  ------    ------  ------    ------  ------')
        Qlim = (gen[:, QMIN] == 0) * gen[:, QMAX] + (gen[:, QMAX] == 0) * gen[:, QMIN]
        for i in range(len(s_areas)):
            a = s_areas[i]
            ildon = nonzero(bus[e2i[gen[:, GEN_BUS]], BUS_AREA] == a & gen[:, GEN_STATUS] > 0 & isload(gen))
            inzld = nonzero(bus[:, BUS_AREA] == a & (bus[:, PD] | bus[:, QD]))
            fd.write('\n%3d    %7.1f %7.1f   %7.1f %7.1f   %7.1f %7.1f   %7.1f %7.1f' %
                (a, -sum(gen[ildon, PMIN]),
                -sum(Qlim[ildon]),
                -sum(gen[ildon, PG]), -sum(gen[ildon, QG]),
                sum(bus[inzld, PD]), sum(bus[inzld, QD]),
                -sum(gen[ildon, PG]) + sum(bus[inzld, PD]),
                -sum(gen[ildon, QG]) + sum(bus[inzld, QD]) ))

        fd.write('\n----    ------  ------    ------  ------    ------  ------    ------  ------')
        fd.write('\nTot:   %7.1f %7.1f   %7.1f %7.1f   %7.1f %7.1f   %7.1f %7.1f' %
                -sum(gen[onld, PMIN]),
                -sum(Qlim[onld]),
                -sum(gen[onld, PG]), -sum(gen[onld, QG]),
                sum(bus[nzld, PD]), sum(bus[nzld, QD]),
                -sum(gen[onld, PG]) + sum(bus[nzld, PD]),
                -sum(gen[onld, QG]) + sum(bus[nzld, QD]) )
        fd.write('\n')
        fd.write('\nArea      Shunt Inj        Branch      Series Losses      Net Export')
        fd.write('\n Num      MW     MVAr     Charging      MW     MVAr       MW     MVAr')
        fd.write('\n----    ------  ------    --------    ------  ------    ------  ------')
        for i in range(len(s_areas)):
            a = s_areas[i]
            inzsh = nonzero(bus[:, BUS_AREA] == a & (bus[:, GS] | bus[:, BS]))
            ibrch = nonzero(bus[e2i[branch[:, F_BUS]], BUS_AREA] == a & bus[e2i[branch[:, T_BUS]], BUS_AREA] == a & branch[:, BR_STATUS])
            in_tie = nonzero(bus[e2i[branch[:, F_BUS]], BUS_AREA] != a & bus[e2i[branch[:, T_BUS]], BUS_AREA] == a & branch[:, BR_STATUS])
            out_tie = nonzero(bus[e2i[branch[:, F_BUS]], BUS_AREA] == a & bus[e2i[branch[:, T_BUS]], BUS_AREA] != a & branch[:, BR_STATUS])
            fd.write('\n%3d    %7.1f %7.1f    %7.1f    %7.2f %7.2f   %7.1f %7.1f' %
                (a, -sum(bus[inzsh, VM]**2 * bus[inzsh, GS]),
                 sum(bus[inzsh, VM]**2 * bus[inzsh, BS]),
                 sum(fchg[ibrch]) + sum(tchg[ibrch]) + sum(fchg[out_tie]) + sum(tchg[in_tie]),
                 sum(real(loss[ibrch])) + sum(real(loss[r_[in_tie, out_tie]])) / 2,
                 sum(imag(loss[ibrch])) + sum(imag(loss[r_[in_tie, out_tie]])) / 2,
                 sum(branch[in_tie, PT])+sum(branch[out_tie, PF]) - sum(real(loss[r_[in_tie, out_tie]])) / 2,
                 sum(branch[in_tie, QT])+sum(branch[out_tie, QF]) - sum(imag(loss[r_[in_tie, out_tie]])) / 2  ))

        fd.write('\n----    ------  ------    --------    ------  ------    ------  ------')
        fd.write('\nTot:   %7.1f %7.1f    %7.1f    %7.2f %7.2f       -       -' %
            (-sum(bus[nzsh, VM]**2 * bus[nzsh, GS]),
             sum(bus[nzsh, VM]**2 * bus[nzsh, BS]),
             sum(fchg) + sum(tchg), sum(real(loss)), sum(imag(loss)) ))
        fd.write('\n')

    ## generator data
    if OUT_GEN:
        if isOPF:
            genlamP = bus[e2i[gen[:, GEN_BUS]], LAM_P]
            genlamQ = bus[e2i[gen[:, GEN_BUS]], LAM_Q]

        fd.write('\n================================================================================')
        fd.write('\n|     Generator Data                                                           |')
        fd.write('\n================================================================================')
        fd.write('\n Gen   Bus   Status     Pg        Qg   ')
        if isOPF: fd.write('   Lambda ($/MVA-hr)')
        fd.write('\n  #     #              (MW)     (MVAr) ')
        if isOPF: fd.write('     P         Q    ')
        fd.write('\n----  -----  ------  --------  --------')
        if isOPF: fd.write('  --------  --------')
        for k in range(len(ong)):
            i = ong[k]
            fd.write('\n%3d %6d     %2d ' % (i, gen(i, GEN_BUS), gen(i, GEN_STATUS)))
            if gen[i, GEN_STATUS] > 0 & (gen[i, PG] | gen[i, QG]):
                fd.write('%10.2f%10.2f' % (gen[i, PG], gen[i, QG]))
            else:
                fd.write('       -         -  ')
            if isOPF: fd.write('%10.2f%10.2f' % (genlamP[i], genlamQ[i]))

        fd.write('\n                     --------  --------')
        fd.write('\n            Total: %9.2f%10.2f', sum(gen[ong, PG]), sum(gen[ong, QG]))
        fd.write('\n')
        if any(onld):
            fd.write('\n================================================================================')
            fd.write('\n|     Dispatchable Load Data                                                   |')
            fd.write('\n================================================================================')
            fd.write('\n Gen   Bus   Status     Pd        Qd   ')
            if isOPF: fd.write('   Lambda ($/MVA-hr)')
            fd.write('\n  #     #              (MW)     (MVAr) ')
            if isOPF: fd.write('     P         Q    ')
            fd.write('\n----  -----  ------  --------  --------')
            if isOPF: fd.write('  --------  --------')
            for k in range(len(onld)):
                i = onld[k]
                fd.write('\n%3d %6d     %2d ' % (i, gen[i, GEN_BUS], gen[i, GEN_STATUS]))
                if gen[i, GEN_STATUS] > 0 & (gen[i, PG] | gen[i, QG]):
                    fd.write('%10.2f%10.2f' % (-gen(i, PG), -gen(i, QG)))
                else:
                    fd.write('       -         -  ')

                if isOPF: fd.write('%10.2f%10.2f' % (genlamP(i), genlamQ(i)))
            fd.write('\n                     --------  --------')
            fd.write('\n            Total: %9.2f%10.2f' % (-sum(gen(onld, PG)), -sum(gen(onld, QG))))
            fd.write('\n')

    ## bus data
    if OUT_BUS:
        fd.write('\n================================================================================')
        fd.write('\n|     Bus Data                                                                 |')
        fd.write('\n================================================================================')
        fd.write('\n Bus      Voltage          Generation             Load        ')
        if isOPF: fd.write('  Lambda($/MVA-hr)')
        fd.write('\n  #   Mag(pu) Ang(deg)   P (MW)   Q (MVAr)   P (MW)   Q (MVAr)')
        if isOPF: fd.write('     P        Q   ')
        fd.write('\n----- ------- --------  --------  --------  --------  --------')
        if isOPF: fd.write('  -------  -------')
        for i in range(nb):
            fd.write('\n%5d%7.3f%9.3f' % (bus(i, [BUS_I, VM, VA])))
            g  = nonzero(gen[:, GEN_STATUS] > 0 & gen[:, GEN_BUS] == bus[i, BUS_I] &
                        ~isload(gen))
            ld = nonzero(gen[:, GEN_STATUS] > 0 & gen[:, GEN_BUS] == bus[i, BUS_I] &
                        isload(gen))
            if any(g):
                fd.write('%10.2f%10.2f', sum(gen[g, PG]), sum(gen[g, QG]))
            else:
                fd.write('       -         -  ')

            if bus[i, PD] | bus[i, QD] | any(ld):
                if any(ld):
                    fd.write('%10.2f*%9.2f*' % (bus[i, PD] - sum(gen[ld, PG]),
                                                 bus[i, QD] - sum(gen[ld, QG])))
                else:
                    fd.write('%10.2f%10.2f ' % bus[i, [PD, QD]])
            else:
                fd.write('       -         -   ')
            if isOPF:
                fd.write('%9.3f' % bus[i, LAM_P])
                if abs(bus[i, LAM_Q]) > ptol:
                    fd.write('%8.3f' % bus[i, LAM_Q])
                else:
                    fd.write('     -')
        fd.write('\n                        --------  --------  --------  --------')
        fd.write('\n               Total: %9.2f %9.2f %9.2f %9.2f' %
            (sum(gen(ong, PG)), sum(gen(ong, QG)),
             sum(bus(nzld, PD)) - sum(gen(onld, PG)),
             sum(bus(nzld, QD)) - sum(gen(onld, QG))))
        fd.write('\n')

    ## branch data
    if OUT_BRANCH:
        fd.write('\n================================================================================')
        fd.write('\n|     Branch Data                                                              |')
        fd.write('\n================================================================================')
        fd.write('\nBrnch   From   To    From Bus Injection   To Bus Injection     Loss (I^2 * Z)  ')
        fd.write('\n  #     Bus    Bus    P (MW)   Q (MVAr)   P (MW)   Q (MVAr)   P (MW)   Q (MVAr)')
        fd.write('\n-----  -----  -----  --------  --------  --------  --------  --------  --------')
        fd.write('\n%4d%7d%7d%10.2f%10.2f%10.2f%10.2f%10.3f%10.2f' %
                r_[  range(nl), branch[:, [F_BUS, T_BUS]],
                     branch[:, [PF, QF]], branch[:, [PT, QT]],
                    real(loss), imag(loss)
                ].T)
        fd.write('\n                                                             --------  --------')
        fd.write('\n                                                    Total:%10.3f%10.2f' %
                (sum(real(loss)), sum(imag(loss))))
        fd.write('\n')

    ##-----  constraint data  -----
    if isOPF:
        ctol = ppopt[16]   ## constraint violation tolerance
        ## voltage constraints
        if not isDC & (OUT_V_LIM == 2 | (OUT_V_LIM == 1 &
                             (any(bus[:, VM] < bus[:, VMIN] + ctol) |
                              any(bus[:, VM] > bus[:, VMAX] - ctol) |
                              any(bus[:, MU_VMIN] > ptol) |
                              any(bus[:, MU_VMAX] > ptol)))):
            fd.write('\n================================================================================')
            fd.write('\n|     Voltage Constraints                                                      |')
            fd.write('\n================================================================================')
            fd.write('\nBus #  Vmin mu    Vmin    |V|   Vmax    Vmax mu')
            fd.write('\n-----  --------   -----  -----  -----   --------')
            for i in range(nb):
                if OUT_V_LIM == 2 | (OUT_V_LIM == 1 &
                             (bus[i, VM] < bus[i, VMIN] + ctol |
                              bus[i, VM] > bus[i, VMAX] - ctol |
                              bus[i, MU_VMIN] > ptol | bus[i, MU_VMAX] > ptol)):
                    fd.write('\n%5d', bus[i, BUS_I])
                    if bus[i, VM] < bus[i, VMIN] + ctol | bus[i, MU_VMIN] > ptol:
                        fd.write('%10.3f' % bus[i, MU_VMIN])
                    else:
                        fd.write('      -   ')

                    fd.write('%8.3f%7.3f%7.3f' % bus[i, [VMIN, VM, VMAX]])
                    if bus[i, VM] > bus[i, VMAX] - ctol | bus[i, MU_VMAX] > ptol:
                        fd.write('%10.3f', bus[i, MU_VMAX])
                    else:
                        fd.write('      -    ')
            fd.write('\n')

        ## generator P constraints
        if OUT_PG_LIM == 2 | \
                (OUT_PG_LIM == 1 & (any(gen[ong, PG] < gen[ong, PMIN] + ctol) |
                                    any(gen[ong, PG] > gen[ong, PMAX] - ctol) |
                                    any(gen[ong, MU_PMIN] > ptol) |
                                    any(gen[ong, MU_PMAX] > ptol))) | \
                (not isDC & (OUT_QG_LIM == 2 |
                (OUT_QG_LIM == 1 & (any(gen[ong, QG] < gen[ong, QMIN] + ctol) |
                                    any(gen[ong, QG] > gen[ong, QMAX] - ctol) |
                                    any(gen[ong, MU_QMIN] > ptol) |
                                    any(gen[ong, MU_QMAX] > ptol))))):
            fd.write('\n================================================================================')
            fd.write('\n|     Generation Constraints                                                   |')
            fd.write('\n================================================================================')

        if OUT_PG_LIM == 2 | (OUT_PG_LIM == 1 &
                                 (any(gen[ong, PG] < gen[ong, PMIN] + ctol) |
                                  any(gen[ong, PG] > gen[ong, PMAX] - ctol) |
                                  any(gen[ong, MU_PMIN] > ptol) |
                                  any(gen[ong, MU_PMAX] > ptol))):
            fd.write('\n Gen   Bus                Active Power Limits')
            fd.write('\n  #     #    Pmin mu    Pmin       Pg       Pmax    Pmax mu')
            fd.write('\n----  -----  -------  --------  --------  --------  -------')
            for k in range(len(ong)):
                i = ong[k]
                if OUT_PG_LIM == 2 | (OUT_PG_LIM == 1 &
                            (gen[i, PG] < gen[i, PMIN] + ctol |
                             gen[i, PG] > gen[i, PMAX] - ctol |
                             gen[i, MU_PMIN] > ptol | gen[i, MU_PMAX] > ptol)):
                    fd.write('\n%4d%6d ' % (i, gen[i, GEN_BUS]))
                    if gen[i, PG] < gen[i, PMIN] + ctol | gen[i, MU_PMIN] > ptol:
                        fd.write('%8.3f' % gen(i, MU_PMIN))
                    else:
                        fd.write('     -  ')
                    if gen[i, PG]:
                        fd.write('%10.2f%10.2f%10.2f' % (gen[i, [PMIN, PG, PMAX]]))
                    else:
                        fd.write('%10.2f       -  %10.2f' % (gen[i, [PMIN, PMAX]]))
                    if gen[i, PG] > gen[i, PMAX] - ctol | gen[i, MU_PMAX] > ptol:
                        fd.write('%9.3f' % gen[i, MU_PMAX])
                    else:
                        fd.write('      -  ')
            fd.write('\n')

        ## generator Q constraints
        if not isDC & (OUT_QG_LIM == 2 | (OUT_QG_LIM == 1 &
                                 (any(gen[ong, QG] < gen[ong, QMIN] + ctol) |
                                  any(gen[ong, QG] > gen[ong, QMAX] - ctol) |
                                  any(gen[ong, MU_QMIN] > ptol) |
                                  any(gen[ong, MU_QMAX] > ptol)))):
            fd.write('\nGen  Bus              Reactive Power Limits')
            fd.write('\n #    #   Qmin mu    Qmin       Qg       Qmax    Qmax mu')
            fd.write('\n---  ---  -------  --------  --------  --------  -------')
            for k in range(len(ong)):
                i = ong[k]
                if OUT_QG_LIM == 2 | (OUT_QG_LIM == 1 &
                            (gen[i, QG] < gen[i, QMIN] + ctol |
                             gen[i, QG] > gen[i, QMAX] - ctol |
                             gen[i, MU_QMIN] > ptol | gen[i, MU_QMAX] > ptol)):
                    fd.write('\n%3d%5d' % (i, gen(i, GEN_BUS)))
                    if gen[i, QG] < gen[i, QMIN] + ctol | gen[i, MU_QMIN] > ptol:
                        fd.write('%8.3f' % gen[i, MU_QMIN])
                    else:
                        fd.write('     -  ')
                    if gen[i, QG]:
                        fd.write('%10.2f%10.2f%10.2f' % gen[i, [QMIN, QG, QMAX]])
                    else:
                        fd.write('%10.2f       -  %10.2f' % gen[i, [QMIN, QMAX]])

                    if gen[i, QG] > gen[i, QMAX] - ctol | gen[i, MU_QMAX] > ptol:
                        fd.write('%9.3f' % gen(i, MU_QMAX))
                    else:
                        fd.write('      -  ')
            fd.write('\n')

        ## dispatchable load P constraints
        if OUT_PG_LIM == 2 | OUT_QG_LIM == 2 | \
                (OUT_PG_LIM == 1 & (any(gen[onld, PG] < gen[onld, PMIN] + ctol) |
                                    any(gen[onld, PG] > gen[onld, PMAX] - ctol) |
                                    any(gen[onld, MU_PMIN] > ptol) |
                                    any(gen[onld, MU_PMAX] > ptol))) | \
                (OUT_QG_LIM == 1 & (any(gen[onld, QG] < gen[onld, QMIN] + ctol) |
                                    any(gen[onld, QG] > gen[onld, QMAX] - ctol) |
                                    any(gen[onld, MU_QMIN] > ptol) |
                                    any(gen[onld, MU_QMAX] > ptol))):
            fd.write('\n================================================================================')
            fd.write('\n|     Dispatchable Load Constraints                                            |')
            fd.write('\n================================================================================')
        if OUT_PG_LIM == 2 | (OUT_PG_LIM == 1 &
                                 (any(gen[onld, PG] < gen[onld, PMIN] + ctol) |
                                  any(gen[onld, PG] > gen[onld, PMAX] - ctol) |
                                  any(gen[onld, MU_PMIN] > ptol) |
                                  any(gen[onld, MU_PMAX] > ptol))):
            fd.write('\nGen  Bus               Active Power Limits')
            fd.write('\n #    #   Pmin mu    Pmin       Pg       Pmax    Pmax mu')
            fd.write('\n---  ---  -------  --------  --------  --------  -------')
            for k in range(len(onld)):
                i = onld[k]
                if OUT_PG_LIM == 2 | (OUT_PG_LIM == 1 &
                            (gen[i, PG] < gen[i, PMIN] + ctol |
                             gen[i, PG] > gen[i, PMAX] - ctol |
                             gen[i, MU_PMIN] > ptol | gen[i, MU_PMAX] > ptol)):
                    fd.write('\n%3d%5d' % (i, gen(i, GEN_BUS)))
                    if gen[i, PG] < gen[i, PMIN] + ctol | gen[i, MU_PMIN] > ptol:
                        fd.write('%8.3f' % gen[i, MU_PMIN])
                    else:
                        fd.write('     -  ')
                    if gen[i, PG]:
                        fd.write('%10.2f%10.2f%10.2f' % gen[i, [PMIN, PG, PMAX]])
                    else:
                        fd.write('%10.2f       -  %10.2f' % gen[i, [PMIN, PMAX]])

                    if gen[i, PG] > gen[i, PMAX] - ctol | gen[i, MU_PMAX] > ptol:
                        fd.write('%9.3f' % gen[i, MU_PMAX])
                    else:
                        fd.write('      -  ')
            fd.write('\n')

        ## dispatchable load Q constraints
        if not isDC & (OUT_QG_LIM == 2 | (OUT_QG_LIM == 1 &
                                 (any(gen[onld, QG] < gen[onld, QMIN] + ctol) |
                                  any(gen[onld, QG] > gen[onld, QMAX] - ctol) |
                                  any(gen[onld, MU_QMIN] > ptol) |
                                  any(gen[onld, MU_QMAX] > ptol)))):
            fd.write('\nGen  Bus              Reactive Power Limits')
            fd.write('\n #    #   Qmin mu    Qmin       Qg       Qmax    Qmax mu')
            fd.write('\n---  ---  -------  --------  --------  --------  -------')
            for k in range(len(onld)):
                i = onld[k]
                if OUT_QG_LIM == 2 | (OUT_QG_LIM == 1 &
                            (gen[i, QG] < gen[i, QMIN] + ctol |
                             gen[i, QG] > gen[i, QMAX] - ctol |
                             gen[i, MU_QMIN] > ptol | gen[i, MU_QMAX] > ptol)):
                    fd.write('\n%3d%5d' % (i, gen(i, GEN_BUS)))
                    if gen[i, QG] < gen[i, QMIN] + ctol | gen[i, MU_QMIN] > ptol:
                        fd.write('%8.3f' % gen[i, MU_QMIN])
                    else:
                        fd.write('     -  ')

                    if gen[i, QG]:
                        fd.write('%10.2f%10.2f%10.2f' % gen[i, [QMIN, QG, QMAX]])
                    else:
                        fd.write('%10.2f       -  %10.2f' % gen[i, [QMIN, QMAX]])

                    if gen[i, QG] > gen[i, QMAX] - ctol | gen[i, MU_QMAX] > ptol:
                        fd.write('%9.3f' % gen[i, MU_QMAX])
                    else:
                        fd.write('      -  ')
            fd.write('\n')

        ## line flow constraints
        if ppopt[24] == 1 | isDC:  ## P limit
            Ff = branch[:, PF]
            Ft = branch[:, PT]
            str = '\n  #     Bus    Pf  mu     Pf      |Pmax|      Pt      Pt  mu   Bus'
        elif ppopt[24] == 2:   ## |I| limit
            Ff = abs( (branch[:, PF] + 1j * branch[:, QF]) / V[e2i[branch[:, F_BUS]]] )
            Ft = abs( (branch[:, PT] + 1j * branch[:, QT]) / V[e2i[branch[:, T_BUS]]] )
            str = '\n  #     Bus   |If| mu    |If|     |Imax|     |It|    |It| mu   Bus'
        else:                ## |S| limit
            Ff = abs(branch[:, PF] + 1j * branch[:, QF])
            Ft = abs(branch[:, PT] + 1j * branch[:, QT])
            str = '\n  #     Bus   |Sf| mu    |Sf|     |Smax|     |St|    |St| mu   Bus'

        if OUT_LINE_LIM == 2 | (OUT_LINE_LIM == 1 &
                            (any(branch[:, RATE_A] != 0 & abs(Ff) > branch[:, RATE_A] - ctol) |
                             any(branch[:, RATE_A] != 0 & abs(Ft) > branch[:, RATE_A] - ctol) |
                             any(branch[:, MU_SF] > ptol) |
                             any(branch[:, MU_ST] > ptol))):
            fd.write('\n================================================================================')
            fd.write('\n|     Branch Flow Constraints                                                  |')
            fd.write('\n================================================================================')
            fd.write('\nBrnch   From     "From" End        Limit       "To" End        To')
            fd.write(str)
            fd.write('\n-----  -----  -------  --------  --------  --------  -------  -----')
            for i in range(nl):
                if OUT_LINE_LIM == 2 | (OUT_LINE_LIM == 1 &
                       ((branch[i, RATE_A] != 0 & abs(Ff[i]) > branch[i, RATE_A] - ctol) |
                        (branch[i, RATE_A] != 0 & abs(Ft[i]) > branch[i, RATE_A] - ctol) |
                        branch[i, MU_SF] > ptol | branch[i, MU_ST] > ptol)):
                    fd.write('\n%4d%7d' % (i, branch(i, F_BUS)))
                    if Ff[i] > branch[i, RATE_A] - ctol | branch[i, MU_SF] > ptol:
                        fd.write('%10.3f' % branch(i, MU_SF))
                    else:
                        fd.write('      -   ')

                    fd.write('%9.2f%10.2f%10.2f' %
                        [Ff[i], branch[i, RATE_A], Ft[i]])
                    if Ft[i] > branch[i, RATE_A] - ctol | branch[i, MU_ST] > ptol:
                        fd.write('%10.3f' % branch[i, MU_ST])
                    else:
                        fd.write('      -   ')
                    fd.write('%6d' % branch[i, T_BUS])
            fd.write('\n')

    ## execute userfcn callbacks for 'printpf' stage
    if have_results_struct & results.has_key('userfcn'):
        run_userfcn(results["userfcn"], 'printpf', results, fd, ppopt)

    ## print raw data for Perl database interface
    if OUT_RAW:
        fd.write('----------  raw PB::Soln data below  ----------\n')
        fd.write('bus\n')
        if isOPF:
            fd.write('%d\t%d\t%g\t%g\t%g\t%g\t%g\t%g\n' %
                        bus[:, [BUS_I, BUS_TYPE, VM, VA, LAM_P, LAM_Q, MU_VMAX, MU_VMIN]].T)

            fd.write('branch\n')
            fd.write('%d\t%g\t%g\t%g\t%g\t%g\t%g\n' %
                        r_[range(nl), branch[:, [PF, QF, PT, QT, MU_SF, MU_ST]]].T)

            fd.write('gen\n')
            fd.write('%d\t%g\t%g\t%g\t%d\t%g\t%g\t%g\t%g\n' %
                        r_[range(ng), gen[:, [PG, QG, VG, GEN_STATUS, MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN]]])
        else:
            fd.write('%d\t%d\t%f\t%f\t%d\t%d\t%d\t%d\n' %
                        r_[bus[:, [BUS_I, BUS_TYPE, VM, VA]], zeros((nb, 4))])

            fd.write('branch\n')
            fd.write('%d\t%f\t%f\t%f\t%f\t%d\t%d\n' %
                        r_[range(nl), branch[:, [PF, QF, PT, QT]], zeros((nl, 2))])

            fd.write('gen\n')
            fd.write('%d\t%f\t%f\t%f\t%d\t%d\t%d\t%d\t%d\n' %
                        r_[range(ng), gen[:, [PG, QG, VG, GEN_STATUS]], zeros((ng, 4))])
        fd.write('end\n')
        fd.write('----------  raw PB::Soln data above  ----------\n')