# Copyright 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from warnings import warn

from numpy import array, ones, zeros, Inf, r_, c_, concatenate, shape
from numpy import flatnonzero as find

from scipy.sparse import spdiags, hstack, vstack, csr_matrix as sparse
from scipy.sparse import eye as speye

from pypower import idx_dcline
from pypower.add_userfcn import add_userfcn
from pypower.remove_userfcn import remove_userfcn
from pypower.isload import isload

from pypower.idx_gen import MBASE, GEN_STATUS, PMIN, PMAX, GEN_BUS, PG, QG, \
    VG, QMIN, QMAX, MU_QMIN, MU_PMAX, MU_PMIN, MU_QMAX

from pypower.idx_bus import BUS_TYPE, REF, PV
from pypower.idx_cost import MODEL, POLYNOMIAL, NCOST


def toggle_dcline(ppc, on_off):
    """Enable or disable DC line modeling.

    Enables or disables a set of OPF userfcn callbacks to implement
    DC lines as a pair of linked generators. While it uses the OPF
    extension mechanism, this implementation works for simple power
    flow as well as OPF problems.

    These callbacks expect to find a 'dcline' field in the input MPC,
    where MPC.dcline is an ndc x 17 matrix with columns as defined
    in IDX_DCLINE, where ndc is the number of DC lines.

    The 'int2ext' callback also packages up flow results and stores them
    in appropriate columns of MPC.dcline.

    NOTE: Because of the way this extension modifies the number of
    rows in the gen and gencost matrices, caution must be taken
    when using it with other extensions that deal with generators.

    Examples:
        ppc = loadcase('t_case9_dcline')
        ppc = toggle_dcline(ppc, 'on')
        results1 = runpf(ppc)
        results2 = runopf(ppc)

    @see: L{idx_dcline}, L{add_userfcn}, L{remove_userfcn}, L{run_userfcn}.
    """
    if on_off == 'on':
        ## define named indices into data matrices
        c = idx_dcline.c

        ## check for proper input data

        if 'dcline' not in ppc or ppc['dcline'].shape[1] < c["LOSS1"] + 1:
            raise ValueError('toggle_dcline: case must contain a '
                    '\'dcline\' field, an ndc x %d matrix.', c["LOSS1"])

        if 'dclinecost' in ppc and ppc['dcline'].shape[0] != ppc['dclinecost'].shape[0]:
            raise ValueError('toggle_dcline: number of rows in \'dcline\''
                    ' field (%d) and \'dclinecost\' field (%d) do not match.' %
                (ppc['dcline'].shape[0], ppc['dclinecost'].shape[0]))

        k = find(ppc['dcline'][:, c["LOSS1"]] < 0)
        if len(k) > 0:
            warn('toggle_dcline: linear loss term is negative for DC line '
                   'from bus %d to %d\n' %
                  ppc['dcline'][k, c['F_BUS']:c['T_BUS'] + 1].T)

        ## add callback functions
        ## note: assumes all necessary data included in 1st arg (ppc, om, results)
        ##       so, no additional explicit args are needed
        ppc = add_userfcn(ppc, 'ext2int', userfcn_dcline_ext2int)
        ppc = add_userfcn(ppc, 'formulation', userfcn_dcline_formulation)
        ppc = add_userfcn(ppc, 'int2ext', userfcn_dcline_int2ext)
        ppc = add_userfcn(ppc, 'printpf', userfcn_dcline_printpf)
        ppc = add_userfcn(ppc, 'savecase', userfcn_dcline_savecase)
    elif on_off == 'off':
        ppc = remove_userfcn(ppc, 'savecase', userfcn_dcline_savecase)
        ppc = remove_userfcn(ppc, 'printpf', userfcn_dcline_printpf)
        ppc = remove_userfcn(ppc, 'int2ext', userfcn_dcline_int2ext)
        ppc = remove_userfcn(ppc, 'formulation', userfcn_dcline_formulation)
        ppc = remove_userfcn(ppc, 'ext2int', userfcn_dcline_ext2int)
    else:
        raise ValueError('toggle_dcline: 2nd argument must be either '
                '\'on\' or \'off\'')

    return ppc


##-----  ext2int  ------------------------------------------------------
def userfcn_dcline_ext2int(ppc, args):
    """This is the 'ext2int' stage userfcn callback that prepares the input
    data for the formulation stage. It expects to find a 'dcline' field
    in ppc as described above. The optional args are not currently used.
    It adds two dummy generators for each in-service DC line, with the
    appropriate upper and lower generation bounds and corresponding
    zero-cost entries in gencost.
    """
    c = idx_dcline.c

    ## initialize some things
    if 'dclinecost' in ppc:
        havecost = True
    else:
        havecost = False

    ## save version with external indexing
    ppc['order']['ext']['dcline'] = ppc['dcline']              ## external indexing
    if havecost:
        ppc['order']['ext']['dclinecost'] = ppc['dclinecost']  ## external indexing

    ppc['order']['ext']['status']  = {}
    ## work with only in-service DC lines
    ppc['order']['ext']['status']['on']  = find(ppc['dcline'][:, c['BR_STATUS']] >  0)
    ppc['order']['ext']['status']['off'] = find(ppc['dcline'][:, c['BR_STATUS']] <= 0)

    ## remove out-of-service DC lines
    dc = ppc['dcline'][ppc['order']['ext']['status']['on'], :] ## only in-service DC lines
    if havecost:
        dcc = ppc['dclinecost'][ppc['order']['ext']['status']['on'], :]    ## only in-service DC lines
        ppc['dclinecost'] = dcc

    ndc = dc.shape[0]          ## number of in-service DC lines
    o = ppc['order']

    ##-----  convert stuff to internal indexing  -----
    dc[:, c['F_BUS']] = o['bus']['e2i'][dc[:, c['F_BUS']]]
    dc[:, c['T_BUS']] = o['bus']['e2i'][dc[:, c['T_BUS']]]
    ppc['dcline'] = dc

    ##-----  create gens to represent DC line terminals  -----
    ## ensure consistency of initial values of PF, PT and losses
    ## (for simple power flow cases)
    dc[:, c['PT']] = dc[:, c['PF']] - (dc[:, c['LOSS0']] + dc[:, c['LOSS1']] * dc[:, c['PF']])

    ## create gens
    fg = zeros((ndc, ppc['gen'].shape[1]))
    fg[:, MBASE]        = 100
    fg[:, GEN_STATUS]   =  dc[:, c['BR_STATUS']]   ## status (should be all 1's)
    fg[:, PMIN]         = -Inf
    fg[:, PMAX]         =  Inf
    tg = fg.copy()
    fg[:, GEN_BUS]      =  dc[:, c['F_BUS']]       ## from bus
    tg[:, GEN_BUS]      =  dc[:, c['T_BUS']]       ## to bus
    fg[:, PG]           = -dc[:, c['PF']]          ## flow (extracted at "from")
    tg[:, PG]           =  dc[:, c['PT']]          ## flow (injected at "to")
    fg[:, QG]           =  dc[:, c['QF']]          ## VAr injection at "from"
    tg[:, QG]           =  dc[:, c['QT']]          ## VAr injection at "to"
    fg[:, VG]           =  dc[:, c['VF']]          ## voltage set-point at "from"
    tg[:, VG]           =  dc[:, c['VT']]          ## voltage set-point at "to"
    k = find(dc[:, c['PMIN']] >= 0)           ## min positive direction flow
    if len(k) > 0:                             ## contrain at "from" end
        fg[k, PMAX]     = -dc[k, c['PMIN']]       ## "from" extraction lower lim

    k = find(dc[:, c['PMAX']] >= 0)           ## max positive direction flow
    if len(k) > 0:                             ## contrain at "from" end
        fg[k, PMIN]     = -dc[k, c['PMAX']]       ## "from" extraction upper lim

    k = find(dc[:, c['PMIN']] < 0)            ## max negative direction flow
    if len(k) > 0:                             ## contrain at "to" end
        tg[k, PMIN]     =  dc[k, c['PMIN']]       ## "to" injection lower lim

    k = find(dc[:, c['PMAX']] < 0)            ## min negative direction flow
    if len(k) > 0:                             ## contrain at "to" end
        tg[k, PMAX]     =  dc[k, c['PMAX']]       ## "to" injection upper lim

    fg[:, QMIN]         =  dc[:, c['QMINF']]      ## "from" VAr injection lower lim
    fg[:, QMAX]         =  dc[:, c['QMAXF']]      ## "from" VAr injection upper lim
    tg[:, QMIN]         =  dc[:, c['QMINT']]      ##  "to"  VAr injection lower lim
    tg[:, QMAX]         =  dc[:, c['QMAXT']]      ##  "to"  VAr injection upper lim

    ## fudge PMAX a bit if necessary to avoid triggering
    ## dispatchable load constant power factor constraints
    fg[isload(fg), PMAX] = -1e-6
    tg[isload(tg), PMAX] = -1e-6

    ## set all terminal buses to PV (except ref bus)
    refbus = find(ppc['bus'][:, BUS_TYPE] == REF)
    ppc['bus'][dc[:, c['F_BUS']], BUS_TYPE] = PV
    ppc['bus'][dc[:, c['T_BUS']], BUS_TYPE] = PV
    ppc['bus'][refbus, BUS_TYPE] = REF

    ## append dummy gens
    ppc['gen'] = r_[ppc['gen'], fg, tg]

    ## gencost
    if 'gencost' in ppc and len(ppc['gencost']) > 0:
        ngcr, ngcc = ppc['gencost'].shape   ## dimensions of gencost
        if havecost:         ## user has provided costs
            ndccc = dcc.shape[1]           ## number of dclinecost columns
            ccc = max(r_[ngcc, ndccc])     ## number of columns in new gencost
            if ccc > ngcc:                 ## right zero-pad gencost
                ppc.gencost = c_[ppc['gencost'], zeros(ngcr, ccc-ngcc)]

            ## flip function across vertical axis and append to gencost
            ## (PF for DC line = -PG for dummy gen at "from" bus)
            for k in range(ndc):
                if dcc[k, MODEL] == POLYNOMIAL:
                    nc = dcc[k, NCOST]
                    temp = dcc[k, NCOST + range(nc + 1)]
                    ## flip sign on coefficients of odd terms
                    ## (every other starting with linear term,
                    ##  that is, the next to last one)
#                    temp((nc-1):-2:1) = -temp((nc-1):-2:1)
                    temp[range(nc, 0, -2)] = -temp[range(nc, 0, -2)]
                else:  ## dcc(k, MODEL) == PW_LINEAR
                    nc = dcc[k, NCOST]
                    temp = dcc[k, NCOST + range(2*nc + 1)]
                    ## switch sign on horizontal coordinate
                    xx = -temp[range(0, 2 * nc + 1, 2)]
                    yy =  temp[range(1, 2 * nc + 1, 2)]
                    temp[range(0, 2*nc + 1, 2)] = xx[-1::-1]
                    temp[range(1, 2*nc + 1, 2)] = yy[-1::-1]

                padding = zeros(ccc - NCOST - len(temp))
                gck = c_[dcc[k, :NCOST + 1], temp, padding]

                ## append to gencost
                ppc['gencost'] = r_[ppc['gencost'], gck]

            ## use zero cost on "to" end gen
            tgc = ones((ndc, 1)) * [2, 0, 0, 2, zeros(ccc-4)]
            ppc['gencost'] = c_[ppc['gencost'], tgc]
        else:
            ## use zero cost as default
            dcgc = ones((2 * ndc, 1)) * concatenate([array([2, 0, 0, 2]), zeros(ngcc-4)])
            ppc['gencost'] = r_[ppc['gencost'], dcgc]

    return ppc


##-----  formulation  --------------------------------------------------
def userfcn_dcline_formulation(om, args):
    """This is the 'formulation' stage userfcn callback that defines the
    user constraints for the dummy generators representing DC lines.
    It expects to find a 'dcline' field in the ppc stored in om, as
    described above. By the time it is passed to this callback,
    MPC.dcline should contain only in-service lines and the from and
    two bus columns should be converted to internal indexing. The
    optional args are not currently used.

    If Pf, Pt and Ploss are the flow at the "from" end, flow at the
    "to" end and loss respectively, and L0 and L1 are the linear loss
    coefficients, the the relationships between them is given by:
        Pf - Ploss = Pt
        Ploss = L0 + L1 * Pf
    If Pgf and Pgt represent the injections of the dummy generators
    representing the DC line injections into the network, then
    Pgf = -Pf and Pgt = Pt, and we can combine all of the above to
    get the following constraint on Pgf ang Pgt:
        -Pgf - (L0 - L1 * Pgf) = Pgt
    which can be written:
        -L0 <= (1 - L1) * Pgf + Pgt <= -L0
    """
    ## define named indices into data matrices
    c = idx_dcline.c

    ## initialize some things
    ppc = om.get_ppc()
    dc = ppc['dcline']
    ndc = dc.shape[0]              ## number of in-service DC lines
    ng  = ppc['gen'].shape[0] - 2 * ndc  ## number of original gens/disp loads

    ## constraints
    nL0 = -dc[:, c['LOSS0']] / ppc['baseMVA']
    L1  =  dc[:, c['LOSS1']]
    Adc = hstack([sparse((ndc, ng)), spdiags(1-L1, 0, ndc, ndc), speye(ndc, ndc)], format="csr")

    ## add them to the model
    om = om.add_constraints('dcline', Adc, nL0, nL0, ['Pg'])

    return om


##-----  int2ext  ------------------------------------------------------
def userfcn_dcline_int2ext(results, args):
    """This is the 'int2ext' stage userfcn callback that converts everything
    back to external indexing and packages up the results. It expects to
    find a 'dcline' field in the results struct as described for ppc
    above. It also expects that the last 2*ndc entries in the gen and
    gencost matrices correspond to the in-service DC lines (where ndc is
    the number of rows in MPC.dcline. These extra rows are removed from
    gen and gencost and the flow is taken from the PG of these gens and
    placed in the flow column of the appropiate dcline row. The
    optional args are not currently used.
    """
    c = idx_dcline.c

    ## initialize some things
    o = results['order']
    k = find(o['ext']['dcline'][:, c['BR_STATUS']])
    ndc = len(k)                    ## number of in-service DC lines
    ng  = results['gen'].shape[0] - 2*ndc; ## number of original gens/disp loads

    ## extract dummy gens
    fg = results['gen'][ng:ng + ndc, :]
    tg = results['gen'][ng + ndc:ng + 2 * ndc, :]

    ## remove dummy gens
    #results['gen']     = results['gen'][:ng + 1, :]
    #results['gencost'] = results['gencost'][:ng + 1, :]
    results['gen']     = results['gen'][:ng, :]
    results['gencost'] = results['gencost'][:ng, :]

    ## get the solved flows
    results['dcline'][:, c['PF']] = -fg[:, PG]
    results['dcline'][:, c['PT']] =  tg[:, PG]
    results['dcline'][:, c['QF']] =  fg[:, QG]
    results['dcline'][:, c['QT']] =  tg[:, QG]
    results['dcline'][:, c['VF']] =  fg[:, VG]
    results['dcline'][:, c['VT']] =  tg[:, VG]
    if fg.shape[1] >= MU_QMIN:
        results['dcline'] = c_[results['dcline'], zeros((ndc, 6))]
        results['dcline'][:, c['MU_PMIN'] ] = fg[:, MU_PMAX] + tg[:, MU_PMIN]
        results['dcline'][:, c['MU_PMAX'] ] = fg[:, MU_PMIN] + tg[:, MU_PMAX]
        results['dcline'][:, c['MU_QMINF']] = fg[:, MU_QMIN]
        results['dcline'][:, c['MU_QMAXF']] = fg[:, MU_QMAX]
        results['dcline'][:, c['MU_QMINT']] = tg[:, MU_QMIN]
        results['dcline'][:, c['MU_QMAXT']] = tg[:, MU_QMAX]

    results['order']['int'] = {}
    ##-----  convert stuff back to external indexing  -----
    results['order']['int']['dcline'] = results['dcline']  ## save internal version
    ## copy results to external version
    o['ext']['dcline'][k, c['PF']:c['VT'] + 1] = results['dcline'][:, c['PF']:c['VT'] + 1]
    if results['dcline'].shape[1] == c['MU_QMAXT'] + 1:
        o['ext']['dcline'] = c_[o['ext']['dcline'], zeros((ndc, 6))]
        o['ext']['dcline'][k, c['MU_PMIN']:c['MU_QMAXT'] + 1] = \
                results['dcline'][:, c['MU_PMIN']:c['MU_QMAXT'] + 1]

    results['dcline'] = o['ext']['dcline']            ## use external version

    return results


##-----  printpf  ------------------------------------------------------
def userfcn_dcline_printpf(results, fd, ppopt, args):
    """This is the 'printpf' stage userfcn callback that pretty-prints the
    results. It expects a results struct, a file descriptor and a MATPOWER
    options vector. The optional args are not currently used.
    """
    ## define named indices into data matrices
    c = idx_dcline.c

    ## options
    OUT_ALL = ppopt['OUT_ALL']
    OUT_BRANCH      = OUT_ALL == 1 or (OUT_ALL == -1 and ppopt['OUT_BRANCH'])
    if OUT_ALL == -1:
        OUT_ALL_LIM = ppopt['OUT_ALL_LIM']
    elif OUT_ALL == 1:
        OUT_ALL_LIM = 2
    else:
        OUT_ALL_LIM = 0

    if OUT_ALL_LIM == -1:
        OUT_LINE_LIM    = ppopt['OUT_LINE_LIM']
    else:
        OUT_LINE_LIM    = OUT_ALL_LIM

    ctol = ppopt['OPF_VIOLATION']   ## constraint violation tolerance
    ptol = 1e-4        ## tolerance for displaying shadow prices

    ##-----  print results  -----
    dc = results['dcline']
    ndc = dc.shape[0]
    kk = find(dc[:, c['BR_STATUS']] != 0)
    if OUT_BRANCH:
        fd.write('\n================================================================================')
        fd.write('\n|     DC Line Data                                                             |')
        fd.write('\n================================================================================')
        fd.write('\n Line    From     To        Power Flow           Loss     Reactive Inj (MVAr)')
        fd.write('\n   #      Bus     Bus   From (MW)   To (MW)      (MW)       From        To   ')
        fd.write('\n------  ------  ------  ---------  ---------  ---------  ---------  ---------')
        loss = 0
        for k in range(ndc):
            if dc[k, c['BR_STATUS']]:   ## status on
                fd.write('\n{0:5.0f}{1:8.0f}{2:8.0f}{3:11.2f}{4:11.2f}{5:11.2f}{6:11.2f}{7:11.2f}'.format(*r_[k, dc[k, c['F_BUS']:c['T_BUS'] + 1], dc[k, c['PF']:c['PT'] + 1],dc[k, c['PF']] - dc[k, c['PT']], dc[k, c['QF']:c['QT'] + 1]]))

                loss = loss + dc[k, c['PF']] - dc[k, c['PT']]
            else:
                fd.write('\n%5d%8d%8d%11s%11s%11s%11s%11s' %
                            (k, dc[k, c['F_BUS']:c['T_BUS'] + 1], '-  ', '-  ', '-  ', '-  ', '-  '))

        fd.write('\n                                              ---------')
        fd.write('\n                                     Total:{0:11.2f}\n'.format(loss))

    if OUT_LINE_LIM == 2 or (OUT_LINE_LIM == 1 and
            (any(dc[kk, c['PF']] > dc[kk, c['PMAX']] - ctol) or
             any(dc[kk, c['MU_PMIN']] > ptol) or
             any(dc[kk, c['MU_PMAX']] > ptol))):
        fd.write('\n================================================================================')
        fd.write('\n|     DC Line Constraints                                                      |')
        fd.write('\n================================================================================')
        fd.write('\n Line    From     To          Minimum        Actual Flow       Maximum')
        fd.write('\n   #      Bus     Bus    Pmin mu     Pmin       (MW)       Pmax      Pmax mu ')
        fd.write('\n------  ------  ------  ---------  ---------  ---------  ---------  ---------')
        for k in range(ndc):
            if OUT_LINE_LIM == 2 or (OUT_LINE_LIM == 1 and
                    (dc[k, c['PF']] > dc[k, c['PMAX']] - ctol or
                     dc[k, c['MU_PMIN']] > ptol or
                     dc[k, c['MU_PMAX']] > ptol)):
                if dc[k, c['BR_STATUS']]:   ## status on
                    fd.write('\n{0:5.0f}{1:8.0f}{2:8.0f}'.format(*r_[k, dc[k, c['F_BUS']:c['T_BUS'] + 1]]))
                    #fd.write('\n%5d%8d%8d' % (k + 1, dc[k, c['F_BUS']:c['T_BUS'] + 1] ))
                    if dc[k, c['MU_PMIN']] > ptol:
                        fd.write('{0:11.3f}'.format(dc[k, c['MU_PMIN']]) )
                    else:
                        fd.write('%11s' % ('-  '))

                    fd.write('{0:11.2f}{1:11.2f}{2:11.2f}' \
                                .format(*r_[dc[k, c['PMIN']], dc[k, c['PF']], dc[k, c['PMAX']]]))
                    if dc[k, c['MU_PMAX']] > ptol:
                        fd.write('{0:11.3f}'.format(dc[k, c['MU_PMAX']]))
                    else:
                        fd.write('%11s' % ('-  '))

                else:
                    fd.write('\n%5d%8d%8d%11s%11s%11s%11s%11s' %
                                (k, dc[k, c['F_BUS']:c['T_BUS'] + 1], '-  ', '-  ', '-  ', '-  ', '-  '))

        fd.write('\n')

    return results


##-----  savecase  -----------------------------------------------------
def userfcn_dcline_savecase(ppc, fd, prefix, args):
    """This is the 'savecase' stage userfcn callback that prints the Py-file
    code to save the 'dcline' field in the case file. It expects a
    PYPOWER case dict (ppc), a file descriptor and variable prefix
    (usually 'ppc.'). The optional args are not currently used.
    """
    ## define named indices into data matrices
    c = idx_dcline.c

    ## save it
    ncols = ppc['dcline'].shape[1]
    fd.write('\n####-----  DC Line Data  -----####\n')
    if ncols < c['MU_QMAXT']:
        fd.write('##\tfbus\ttbus\tstatus\tPf\tPt\tQf\tQt\tVf\tVt\tPmin\tPmax\tQminF\tQmaxF\tQminT\tQmaxT\tloss0\tloss1\n')
    else:
        fd.write('##\tfbus\ttbus\tstatus\tPf\tPt\tQf\tQt\tVf\tVt\tPmin\tPmax\tQminF\tQmaxF\tQminT\tQmaxT\tloss0\tloss1\tmuPmin\tmuPmax\tmuQminF\tmuQmaxF\tmuQminT\tmuQmaxT\n')

    template = '\t%d\t%d\t%d\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g\t%.9g'
    if ncols == c['MU_QMAXT'] + 1:
        template = [template, '\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f']

    template = template + ';\n'
    fd.write('%sdcline = [\n' % prefix)
    fd.write(template, ppc['dcline'].T)
    fd.write('];\n')

    return ppc
