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

from sys import stdout, stderr

from numpy import array, shape, any, delete, unique, arange, nonzero, pi, \
    r_, c_, ones, Inf
from numpy import flatnonzero as find

from scipy.sparse import csr_matrix as sparse

from pypower.pqcost import pqcost
from pypower.opf_args import opf_args
from pypower.makeBdc import makeBdc
from pypower.makeAvl import makeAvl
from pypower.makeApq import makeApq
from pypower.makeAang import makeAang
from pypower.makeAy import makeAy
from pypower.opf_model import opf_model
from pypower.run_userfcn import run_userfcn

from pypower.idx_cost import MODEL, NCOST, PW_LINEAR, COST, POLYNOMIAL
from pypower.idx_bus import BUS_TYPE, REF, VA, VM, PD, GS, VMAX, VMIN
from pypower.idx_gen import GEN_BUS, VG, PG, QG, PMAX, PMIN, QMAX, QMIN
from pypower.idx_brch import RATE_A


def opf_setup(ppc, ppopt):
    """Constructs an OPF model object from a PYPOWER case dict.

    Assumes that ppc is a MATPOWER case struct with internal indexing,
    all equipment in-service, etc.

    @see: C{opf}, C{ext2int}, C{opf_execute}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## options
    dc  = ppopt['PF_DC']        ## 1 = DC OPF, 0 = AC OPF
    alg = ppopt['OPF_ALG']
    verbose = ppopt['VERBOSE']

    ## data dimensions
    nb = shape(ppc['bus'])[0]    ## number of buses
    nl = shape(ppc['branch'])[0] ## number of branches
    ng = shape(ppc['gen'])[0]    ## number of dispatchable injections
    if 'A' in ppc:
        nusr = shape(ppc['A'])[0]    ## number of linear user constraints
    else:
        nusr = 0

    if 'N' in ppc:
        nw = shape(ppc['N'])[0]      ## number of general cost vars, w
    else:
        nw = 0

    if dc:
        ## ignore reactive costs for DC
        ppc['gencost'] = pqcost(ppc['gencost'], ng)

        ## reduce A and/or N from AC dimensions to DC dimensions, if needed
        if nusr | nw:
            acc = r_[nb + arange(nb), 2 * nb + ng + arange(ng)]   ## Vm and Qg columns
            if nusr and shape(ppc['A'])[1] >= 2*nb + 2*ng:
                ## make sure there aren't any constraints on Vm or Qg
                if any(any(ppc['A'][:, acc])):
                    stderr.write('opf_setup: attempting to solve DC OPF with user constraints on Vm or Qg\n')
                    ppc['A'] = delete(ppc['A'], acc, 1)           ## delete Vm and Qg columns

            if nw and shape(ppc['N'])[1] >= 2*nb + 2*ng:
                ## make sure there aren't any costs on Vm or Qg
                if any(any(ppc['N'][:, acc])):
                    ii, jj = nonzero(ppc['N'][:, acc])
                    _, ii = unique(ii, return_index=True)    ## indices of w with potential non-zero cost terms from Vm or Qg
                    if any(ppc['Cw'][ii]) | ('H' in ppc & len(ppc['H']) > 0 &
                    any(any(ppc['H'][:, ii]))):
                        stderr.write('opf_setup: attempting to solve DC OPF with user costs on Vm or Qg\n')

                ppc['N'] = delete(ppc['N'], acc, 1)               ## delete Vm and Qg columns

    ## convert single-block piecewise-linear costs into linear polynomial cost
    pwl1 = find(ppc['gencost'][:, MODEL] == PW_LINEAR & ppc['gencost'][:, NCOST] == 2)
    # p1 = array([])
    if len(pwl1) > 0:
        x0 = ppc['gencost'][pwl1, COST]
        y0 = ppc['gencost'][pwl1, COST + 1]
        x1 = ppc['gencost'][pwl1, COST + 2]
        y1 = ppc['gencost'][pwl1, COST + 3]
        m = (y1 - y0) / (x1 - x0)
        b = y0 - m * x0
        ppc['gencost'][pwl1, MODEL] = POLYNOMIAL
        ppc['gencost'][pwl1, NCOST] = 2
        ppc['gencost'][pwl1, COST:COST + 1] = r_[m, b]

    ## create (read-only) copies of individual fields for convenience
    baseMVA, bus, gen, branch, gencost, Au, lbu, ubu, ppopt, \
        N, fparm, H, Cw, z0, zl, zu, userfcn = opf_args(ppc, ppopt)

    ## warn if there is more than one reference bus
    refs = find(bus[:, BUS_TYPE] == REF)
    if len(refs) > 1 and verbose > 0:
        errstr = '\nopf_setup: Warning: Multiple reference buses.\n' + \
            '           For a system with islands, a reference bus in each island\n' + \
            '           may help convergence, but in a fully connected system such\n' + \
            '           a situation is probably not reasonable.\n\n'
        stdout.write(errstr)

    ## set up initial variables and bounds
    Va   = bus[:, VA] * (pi / 180.0)
    Vm   = bus[:, VM].copy()
    Vm[gen[:, GEN_BUS]] = gen[:, VG]   ## buses with gens, init Vm from gen data
    Pg   = gen[:, PG] / baseMVA
    Qg   = gen[:, QG] / baseMVA
    Pmin = gen[:, PMIN] / baseMVA
    Pmax = gen[:, PMAX] / baseMVA
    Qmin = gen[:, QMIN] / baseMVA
    Qmax = gen[:, QMAX] / baseMVA

    if dc:               ## DC model
        ## more problem dimensions
        nv    = 0            ## number of voltage magnitude vars
        nq    = 0            ## number of Qg vars
        q1    = array([])    ## index of 1st Qg column in Ay

        ## power mismatch constraints
        B, Bf, Pbusinj, Pfinj = makeBdc(baseMVA, bus, branch)
        neg_Cg = sparse((-1, (gen[:, GEN_BUS], arange(ng))), (nb, ng))   ## Pbus w.r.t. Pg
        Amis = c_[B, neg_Cg]
        bmis = -(bus[:, PD] + bus[:, GS]) / baseMVA - Pbusinj

        ## branch flow constraints
        il = find(branch[:, RATE_A] != 0 & branch[:, RATE_A] < 1e10)
        nl2 = len(il)         ## number of constrained lines
        lpf = -Inf * ones(nl2)
        upf = branch[il, RATE_A] / baseMVA - Pfinj[il]
        upt = branch[il, RATE_A] / baseMVA + Pfinj[il]

        user_vars = ['Va', 'Pg']
        ycon_vars = ['Pg', 'y']
    else:                ## AC model
        ## more problem dimensions
        nv    = nb           ## number of voltage magnitude vars
        nq    = ng           ## number of Qg vars
        q1    = 1 + ng       ## index of 1st Qg column in Ay

        ## dispatchable load, constant power factor constraints
        Avl, lvl, uvl  = makeAvl(baseMVA, gen)

        ## generator PQ capability curve constraints
        Apqh, ubpqh, Apql, ubpql, Apqdata = makeApq(baseMVA, gen)

        user_vars = ['Va', 'Vm', 'Pg', 'Qg']
        ycon_vars = ['Pg', 'Qg', 'y']

    ## voltage angle reference constraints
    Vau = Inf * ones(nb)
    Val = -Vau
    Vau[refs] = Va[refs]
    Val[refs] = Va[refs]

    ## branch voltage angle difference limits
    Aang, lang, uang, iang  = makeAang(baseMVA, branch, nb, ppopt)

    ## basin constraints for piece-wise linear gen cost variables
    if alg == 545 or alg == 550:     ## SC-PDIPM or TRALM, no CCV cost vars
        ny = 0
        Ay = None
        by = array([])
    else:
        ipwl = find(gencost[:, MODEL] == PW_LINEAR)  ## piece-wise linear costs
        ny = shape(ipwl)[0]   ## number of piece-wise linear cost vars
        Ay, by = makeAy(baseMVA, ng, gencost, 1, q1, 1+ng+nq)

    if any(gencost[:, MODEL] != POLYNOMIAL and gencost[:, MODEL] != PW_LINEAR):
        stderr.write('opf_setup: some generator cost rows have invalid MODEL value\n')

    ## more problem dimensions
    nx = nb+nv + ng+nq;  ## number of standard OPF control variables
    if nusr:
        nz = shape(ppc['A'])[1] - nx  ## number of user z variables
        if nz < 0:
            stderr.write('opf_setup: user supplied A matrix must have at least %d columns.\n' % nx)
    else:
        nz = 0               ## number of user z variables
        if nw:               ## still need to check number of columns of N
            if shape(ppc['N'])[1] != nx:
                stderr.write('opf_setup: user supplied N matrix must have %d columns.\n' % nx)

    ## construct OPF model object
    om = opf_model(ppc)
    if len(pwl1) > 0:
      om = om.userdata('pwl1', pwl1)

    if dc:
        om = om.userdata('Bf', Bf)
        om = om.userdata('Pfinj', Pfinj)
        om = om.userdata('iang', iang)
        om = om.add_vars('Va', nb, Va, Val, Vau)
        om = om.add_vars('Pg', ng, Pg, Pmin, Pmax)
        om = om.add_constraints('Pmis', Amis, bmis, bmis, ['Va', 'Pg']) ## nb
        om = om.add_constraints('Pf',  Bf[il, :], lpf, upf, ['Va'])     ## nl
        om = om.add_constraints('Pt', -Bf[il, :], lpf, upt, ['Va'])     ## nl
        om = om.add_constraints('ang', Aang, lang, uang, ['Va'])        ## nang
    else:
        om = om.userdata('Apqdata', Apqdata)
        om = om.userdata('iang', iang)
        om = om.add_vars('Va', nb, Va, Val, Vau)
        om = om.add_vars('Vm', nb, Vm, bus[:, VMIN], bus[:, VMAX])
        om = om.add_vars('Pg', ng, Pg, Pmin, Pmax)
        om = om.add_vars('Qg', ng, Qg, Qmin, Qmax)
        om = om.add_constraints('Pmis', nb, 'nonlinear')
        om = om.add_constraints('Qmis', nb, 'nonlinear')
        om = om.add_constraints('Sf', nl, 'nonlinear')
        om = om.add_constraints('St', nl, 'nonlinear')
        om = om.add_constraints('PQh', Apqh, array([]), ubpqh, ['Pg', 'Qg'])   ## npqh
        om = om.add_constraints('PQl', Apql, array([]), ubpql, ['Pg', 'Qg'])   ## npql
        om = om.add_constraints('vl',  Avl, lvl, uvl,   ['Pg', 'Qg'])   ## nvl
        om = om.add_constraints('ang', Aang, lang, uang, ['Va'])        ## nang

    ## y vars, constraints for piece-wise linear gen costs
    if ny > 0:
        om = om.add_vars('y', ny)
        om = om.add_constraints('ycon', Ay, array([]), by, ycon_vars)          ## ncony

    ## add user vars, constraints and costs (as specified via A, ..., N, ...)
    if nz > 0:
        om = om.add_vars('z', nz, z0, zl, zu)
        user_vars.append('z')

    if nusr:
        om = om.add_constraints('usr', ppc['A'], lbu, ubu, user_vars)      ## nusr

    if nw:
        user_cost = {}
        user_cost['N'] = ppc['N']
        user_cost['Cw'] = Cw
        if len(fparm) > 0:
            user_cost['dd'] = fparm[:, 0]
            user_cost['rh'] = fparm[:, 1]
            user_cost['kk'] = fparm[:, 2]
            user_cost['mm'] = fparm[:, 3]

        if len(H) > 0:
            user_cost['H'] = H

        om = om.add_costs('usr', user_cost, user_vars)

    ## execute userfcn callbacks for 'formulation' stage
    om = run_userfcn(userfcn, 'formulation', om)

    return om
