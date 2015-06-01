# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
from pypower.e2i_field import e2i_field
from pypower.i2e_field import i2e_field
from pypower.i2e_data import i2e_data

"""Enable or disable fixed reserve requirements.
"""

from sys import stderr

from pprint import pprint

from numpy import zeros, ones, arange, Inf, any, flatnonzero as find

from scipy.sparse import eye as speye
from scipy.sparse import csr_matrix as sparse
from scipy.sparse import hstack

from pypower.add_userfcn import add_userfcn
from pypower.remove_userfcn import remove_userfcn
from pypower.ext2int import ext2int
from pypower.int2ext import int2ext
from pypower.idx_gen import RAMP_10, PMAX, GEN_STATUS, GEN_BUS


def toggle_reserves(ppc, on_off):
    """Enable or disable fixed reserve requirements.

    Enables or disables a set of OPF userfcn callbacks to implement
    co-optimization of reserves with fixed zonal reserve requirements.

    These callbacks expect to find a 'reserves' field in the input C{ppc},
    where C{ppc['reserves']} is a dict with the following fields:
        - C{zones}   C{nrz x ng}, C{zone(i, j) = 1}, if gen C{j} belongs
        to zone C{i} 0, otherwise
        - C{req}     C{nrz x 1}, zonal reserve requirement in MW
        - C{cost}    (C{ng} or C{ngr}) C{x 1}, cost of reserves in $/MW
        - C{qty}     (C{ng} or C{ngr}) C{x 1}, max quantity of reserves
        in MW (optional)
    where C{nrz} is the number of reserve zones and C{ngr} is the number of
    generators belonging to at least one reserve zone and C{ng} is the total
    number of generators.

    The 'int2ext' callback also packages up results and stores them in
    the following output fields of C{results['reserves']}:
        - C{R}       - C{ng x 1}, reserves provided by each gen in MW
        - C{Rmin}    - C{ng x 1}, lower limit on reserves provided by
        each gen, (MW)
        - C{Rmax}    - C{ng x 1}, upper limit on reserves provided by
        each gen, (MW)
        - C{mu.l}    - C{ng x 1}, shadow price on reserve lower limit, ($/MW)
        - C{mu.u}    - C{ng x 1}, shadow price on reserve upper limit, ($/MW)
        - C{mu.Pmax} - C{ng x 1}, shadow price on C{Pg + R <= Pmax}
        constraint, ($/MW)
        - C{prc}     - C{ng x 1}, reserve price for each gen equal to
        maximum of the shadow prices on the zonal requirement constraint
        for each zone the generator belongs to

    @see: L{runopf_w_res}, L{add_userfcn}, L{remove_userfcn}, L{run_userfcn},
        L{t.t_case30_userfcns}

    @author: Ray Zimmerman (PSERC Cornell)
    """
    if on_off == 'on':
        ## check for proper reserve inputs
        if ('reserves' not in ppc) | (not isinstance(ppc['reserves'], dict)) | \
                ('zones' not in ppc['reserves']) | \
                ('req' not in ppc['reserves']) | \
                ('cost' not in ppc['reserves']):
            stderr.write('toggle_reserves: case must contain a \'reserves\' field, a struct defining \'zones\', \'req\' and \'cost\'\n')

        ## add callback functions
        ## note: assumes all necessary data included in 1st arg (ppc, om, results)
        ##       so, no additional explicit args are needed
        ppc = add_userfcn(ppc, 'ext2int', userfcn_reserves_ext2int)
        ppc = add_userfcn(ppc, 'formulation', userfcn_reserves_formulation)
        ppc = add_userfcn(ppc, 'int2ext', userfcn_reserves_int2ext)
        ppc = add_userfcn(ppc, 'printpf', userfcn_reserves_printpf)
        ppc = add_userfcn(ppc, 'savecase', userfcn_reserves_savecase)
    elif on_off == 'off':
        ppc = remove_userfcn(ppc, 'savecase', userfcn_reserves_savecase)
        ppc = remove_userfcn(ppc, 'printpf', userfcn_reserves_printpf)
        ppc = remove_userfcn(ppc, 'int2ext', userfcn_reserves_int2ext)
        ppc = remove_userfcn(ppc, 'formulation', userfcn_reserves_formulation)
        ppc = remove_userfcn(ppc, 'ext2int', userfcn_reserves_ext2int)
    else:
        stderr.write('toggle_reserves: 2nd argument must be either ''on'' or ''off''')

    return ppc


def userfcn_reserves_ext2int(ppc, *args):
    """This is the 'ext2int' stage userfcn callback that prepares the input
    data for the formulation stage. It expects to find a 'reserves' field
    in ppc as described above. The optional args are not currently used.
    """
    ## initialize some things
    r = ppc['reserves']
    o = ppc['order']
    ng0 = o['ext']['gen'].shape[0]  ## number of original gens (+ disp loads)
    nrz = r['req'].shape[0]         ## number of reserve zones
    if nrz > 1:
        ppc['reserves']['rgens'] = any(r['zones'], 0)  ## mask of gens available to provide reserves
    else:
        ppc['reserves']['rgens'] = r['zones']

    igr = find(ppc['reserves']['rgens']) ## indices of gens available to provide reserves
    ngr = len(igr)              ## number of gens available to provide reserves

    ## check data for consistent dimensions
    if r['zones'].shape[0] != nrz:
        stderr.write('userfcn_reserves_ext2int: the number of rows in ppc[\'reserves\'][\'req\'] (%d) and ppc[\'reserves\'][\'zones\'] (%d) must match\n' % (nrz, r['zones'].shape[0]))

    if (r['cost'].shape[0] != ng0) & (r['cost'].shape[0] != ngr):
        stderr.write('userfcn_reserves_ext2int: the number of rows in ppc[\'reserves\'][\'cost\'] (%d) must equal the total number of generators (%d) or the number of generators able to provide reserves (%d)\n' % (r['cost'].shape[0], ng0, ngr))

    if 'qty' in r:
        if r['qty'].shape[0] != r['cost'].shape[0]:
            stderr.write('userfcn_reserves_ext2int: ppc[\'reserves\'][\'cost\'] (%d x 1) and ppc[\'reserves\'][\'qty\'] (%d x 1) must be the same dimension\n' % (r['cost'].shape[0], r['qty'].shape[0]))


    ## convert both cost and qty from ngr x 1 to full ng x 1 vectors if necessary
    if r['cost'].shape[0] < ng0:
        if 'original' not in ppc['reserves']:
            ppc['reserves']['original'] = {}
        ppc['reserves']['original']['cost'] = r['cost'].copy()    ## save original
        cost = zeros(ng0)
        cost[igr] = r['cost']
        ppc['reserves']['cost'] = cost
        if 'qty' in r:
            ppc['reserves']['original']['qty'] = r['qty'].copy()  ## save original
            qty = zeros(ng0)
            qty[igr] = r['qty']
            ppc['reserves']['qty'] = qty

    ##-----  convert stuff to internal indexing  -----
    ## convert all reserve parameters (zones, costs, qty, rgens)
    if 'qty' in r:
        ppc = e2i_field(ppc, ['reserves', 'qty'], 'gen')

    ppc = e2i_field(ppc, ['reserves', 'cost'], 'gen')
    ppc = e2i_field(ppc, ['reserves', 'zones'], 'gen', 1)
    ppc = e2i_field(ppc, ['reserves', 'rgens'], 'gen', 1)

    ## save indices of gens available to provide reserves
    ppc['order']['ext']['reserves']['igr'] = igr               ## external indexing
    ppc['reserves']['igr'] = find(ppc['reserves']['rgens'])    ## internal indexing

    return ppc


def userfcn_reserves_formulation(om, *args):
    """This is the 'formulation' stage userfcn callback that defines the
    user costs and constraints for fixed reserves. It expects to find
    a 'reserves' field in the ppc stored in om, as described above.
    By the time it is passed to this callback, ppc['reserves'] should
    have two additional fields:
        - C{igr}     C{1 x ngr}, indices of generators available for reserves
        - C{rgens}   C{1 x ng}, 1 if gen avaiable for reserves, 0 otherwise
    It is also assumed that if cost or qty were C{ngr x 1}, they have been
    expanded to C{ng x 1} and that everything has been converted to
    internal indexing, i.e. all gens are on-line (by the 'ext2int'
    callback). The optional args are not currently used.
    """
    ## initialize some things
    ppc = om.get_ppc()
    r = ppc['reserves']
    igr = r['igr']                ## indices of gens available to provide reserves
    ngr = len(igr)                ## number of gens available to provide reserves
    ng  = ppc['gen'].shape[0]     ## number of on-line gens (+ disp loads)

    ## variable bounds
    Rmin = zeros(ngr)               ## bound below by 0
    Rmax = Inf * ones(ngr)          ## bound above by ...
    k = find(ppc['gen'][igr, RAMP_10])
    Rmax[k] = ppc['gen'][igr[k], RAMP_10] ## ... ramp rate and ...
    if 'qty' in r:
        k = find(r['qty'][igr] < Rmax)
        Rmax[k] = r['qty'][igr[k]]        ## ... stated max reserve qty
    Rmax = Rmax / ppc['baseMVA']

    ## constraints
    I = speye(ngr, ngr, format='csr')                     ## identity matrix
    Ar = hstack([sparse((ones(ngr), (arange(ngr), igr)), (ngr, ng)), I], 'csr')
    ur = ppc['gen'][igr, PMAX] / ppc['baseMVA']
    lreq = r['req'] / ppc['baseMVA']

    ## cost
    Cw = r['cost'][igr] * ppc['baseMVA']     ## per unit cost coefficients

    ## add them to the model
    om.add_vars('R', ngr, [], Rmin, Rmax)
    om.add_constraints('Pg_plus_R', Ar, [], ur, ['Pg', 'R'])
    om.add_constraints('Rreq', sparse( r['zones'][:, igr] ), lreq, [], ['R'])
    om.add_costs('Rcost', {'N': I, 'Cw': Cw}, ['R'])

    return om


def userfcn_reserves_int2ext(results, *args):
    """This is the 'int2ext' stage userfcn callback that converts everything
    back to external indexing and packages up the results. It expects to
    find a 'reserves' field in the results struct as described for ppc
    above, including the two additional fields 'igr' and 'rgens'. It also
    expects the results to contain a variable 'R' and linear constraints
    'Pg_plus_R' and 'Rreq' which are used to populate output fields in
    results.reserves. The optional args are not currently used.
    """
    ## initialize some things
    r = results['reserves']

    ## grab some info in internal indexing order
    igr = r['igr']                ## indices of gens available to provide reserves
    ng  = results['gen'].shape[0] ## number of on-line gens (+ disp loads)

    ##-----  convert stuff back to external indexing  -----
    ## convert all reserve parameters (zones, costs, qty, rgens)
    if 'qty' in r:
        results = i2e_field(results, ['reserves', 'qty'], ordering='gen')

    results = i2e_field(results, ['reserves', 'cost'], ordering='gen')
    results = i2e_field(results, ['reserves', 'zones'], ordering='gen', dim=1)
    results = i2e_field(results, ['reserves', 'rgens'], ordering='gen', dim=1)
    results['order']['int']['reserves']['igr'] = results['reserves']['igr']  ## save internal version
    results['reserves']['igr'] = results['order']['ext']['reserves']['igr']  ## use external version
    r = results['reserves']       ## update
    o = results['order']          ## update

    ## grab same info in external indexing order
    igr0 = r['igr']               ## indices of gens available to provide reserves
    ng0  = o['ext']['gen'].shape[0]  ## number of gens (+ disp loads)

    ##-----  results post-processing  -----
    ## get the results (per gen reserves, multipliers) with internal gen indexing
    ## and convert from p.u. to per MW units
    _, Rl, Ru = results['om'].getv('R')
    R       = zeros(ng)
    Rmin    = zeros(ng)
    Rmax    = zeros(ng)
    mu_l    = zeros(ng)
    mu_u    = zeros(ng)
    mu_Pmax = zeros(ng)
    R[igr]       = results['var']['val']['R'] * results['baseMVA']
    Rmin[igr]    = Rl * results['baseMVA']
    Rmax[igr]    = Ru * results['baseMVA']
    mu_l[igr]    = results['var']['mu']['l']['R'] / results['baseMVA']
    mu_u[igr]    = results['var']['mu']['u']['R'] / results['baseMVA']
    mu_Pmax[igr] = results['lin']['mu']['u']['Pg_plus_R'] / results['baseMVA']

    ## store in results in results struct
    z = zeros(ng0)
    results['reserves']['R']       = i2e_data(results, R, z, 'gen')
    results['reserves']['Rmin']    = i2e_data(results, Rmin, z, 'gen')
    results['reserves']['Rmax']    = i2e_data(results, Rmax, z, 'gen')
    if 'mu' not in results['reserves']:
        results['reserves']['mu'] = {}
    results['reserves']['mu']['l']    = i2e_data(results, mu_l, z, 'gen')
    results['reserves']['mu']['u']    = i2e_data(results, mu_u, z, 'gen')
    results['reserves']['mu']['Pmax'] = i2e_data(results, mu_Pmax, z, 'gen')
    results['reserves']['prc']        = z
    for k in igr0:
        iz = find(r['zones'][:, k])
        results['reserves']['prc'][k] = sum(results['lin']['mu']['l']['Rreq'][iz]) / results['baseMVA']

    results['reserves']['totalcost'] = results['cost']['Rcost']

    ## replace ng x 1 cost, qty with ngr x 1 originals
    if 'original' in r:
        if 'qty' in r:
            results['reserves']['qty'] = r['original']['qty']
        results['reserves']['cost'] = r['original']['cost']
        del results['reserves']['original']

    return results


def userfcn_reserves_printpf(results, fd, ppopt, *args):
    """This is the 'printpf' stage userfcn callback that pretty-prints the
    results. It expects a C{results} dict, a file descriptor and a PYPOWER
    options vector. The optional args are not currently used.
    """
    ##-----  print results  -----
    r = results['reserves']
    nrz = r['req'].shape[0]
    OUT_ALL = ppopt['OUT_ALL']
    if OUT_ALL != 0:
        fd.write('\n================================================================================')
        fd.write('\n|     Reserves                                                                 |')
        fd.write('\n================================================================================')
        fd.write('\n Gen   Bus   Status  Reserves   Price')
        fd.write('\n  #     #              (MW)     ($/MW)     Included in Zones ...')
        fd.write('\n----  -----  ------  --------  --------   ------------------------')
        for k in r['igr']:
            iz = find(r['zones'][:, k])
            fd.write('\n%3d %6d     %2d ' % (k, results['gen'][k, GEN_BUS], results['gen'][k, GEN_STATUS]))
            if (results['gen'][k, GEN_STATUS] > 0) & (abs(results['reserves']['R'][k]) > 1e-6):
                fd.write('%10.2f' % results['reserves']['R'][k])
            else:
                fd.write('       -  ')

            fd.write('%10.2f     ' % results['reserves']['prc'][k])
            for i in range(len(iz)):
                if i != 0:
                    fd.write(', ')
                fd.write('%d' % iz[i])

        fd.write('\n                     --------')
        fd.write('\n            Total:%10.2f              Total Cost: $%.2f' %
            (sum(results['reserves']['R'][r['igr']]), results['reserves']['totalcost']))
        fd.write('\n')

        fd.write('\nZone  Reserves   Price  ')
        fd.write('\n  #     (MW)     ($/MW) ')
        fd.write('\n----  --------  --------')
        for k in range(nrz):
            iz = find(r['zones'][k, :])     ## gens in zone k
            fd.write('\n%3d%10.2f%10.2f' % (k, sum(results['reserves']['R'][iz]),
                    results['lin']['mu']['l']['Rreq'][k] / results['baseMVA']))
        fd.write('\n')

        fd.write('\n================================================================================')
        fd.write('\n|     Reserve Limits                                                           |')
        fd.write('\n================================================================================')
        fd.write('\n Gen   Bus   Status  Rmin mu     Rmin    Reserves    Rmax    Rmax mu   Pmax mu ')
        fd.write('\n  #     #             ($/MW)     (MW)      (MW)      (MW)     ($/MW)    ($/MW) ')
        fd.write('\n----  -----  ------  --------  --------  --------  --------  --------  --------')
        for k in r['igr']:
            fd.write('\n%3d %6d     %2d ' % (k, results['gen'][k, GEN_BUS], results['gen'][k, GEN_STATUS]))
            if (results['gen'][k, GEN_STATUS] > 0) & (results['reserves']['mu']['l'][k] > 1e-6):
                fd.write('%10.2f' % results['reserves']['mu']['l'][k])
            else:
                fd.write('       -  ')

            fd.write('%10.2f' % results['reserves']['Rmin'][k])
            if (results['gen'][k, GEN_STATUS] > 0) & (abs(results['reserves']['R'][k]) > 1e-6):
                fd.write('%10.2f' % results['reserves']['R'][k])
            else:
                fd.write('       -  ')

            fd.write('%10.2f' % results['reserves']['Rmax'][k])
            if (results['gen'][k, GEN_STATUS] > 0) & (results['reserves']['mu']['u'][k] > 1e-6):
                fd.write('%10.2f' % results['reserves']['mu']['u'][k])
            else:
                fd.write('       -  ')

            if (results['gen'][k, GEN_STATUS] > 0) & (results['reserves']['mu']['Pmax'][k] > 1e-6):
                fd.write('%10.2f' % results['reserves']['mu']['Pmax'][k])
            else:
                fd.write('       -  ')

        fd.write('\n                                         --------')
        fd.write('\n                                Total:%10.2f' % sum(results['reserves']['R'][r['igr']]))
        fd.write('\n')

    return results


def userfcn_reserves_savecase(ppc, fd, prefix, *args):
    """This is the 'savecase' stage userfcn callback that prints the Python
    file code to save the 'reserves' field in the case file. It expects a
    PYPOWER case dict (ppc), a file descriptor and variable prefix
    (usually 'ppc'). The optional args are not currently used.
    """
    r = ppc['reserves']

    fd.write('\n####-----  Reserve Data  -----####\n')
    fd.write('#### reserve zones, element i, j is 1 if gen j is in zone i, 0 otherwise\n')
    fd.write('%sreserves.zones = [\n' % prefix)
    template = ''
    for _ in range(r['zones'].shape[1]):
        template = template + '\t%d'
    template = template + ';\n'
    fd.write(template, r.zones.T)
    fd.write('];\n')

    fd.write('\n#### reserve requirements for each zone in MW\n')
    fd.write('%sreserves.req = [\t%g' % (prefix, r['req'][0]))
    if len(r['req']) > 1:
        fd.write(';\t%g' % r['req'][1:])
    fd.write('\t];\n')

    fd.write('\n#### reserve costs in $/MW for each gen that belongs to at least 1 zone\n')
    fd.write('#### (same order as gens, but skipping any gen that does not belong to any zone)\n')
    fd.write('%sreserves.cost = [\t%g' % (prefix, r['cost'][0]))
    if len(r['cost']) > 1:
        fd.write(';\t%g' % r['cost'][1:])
    fd.write('\t];\n')

    if 'qty' in r:
        fd.write('\n#### OPTIONAL max reserve quantities for each gen that belongs to at least 1 zone\n')
        fd.write('#### (same order as gens, but skipping any gen that does not belong to any zone)\n')
        fd.write('%sreserves.qty = [\t%g' % (prefix, r['qty'][0]))
        if len(r['qty']) > 1:
            fd.write(';\t%g' % r['qty'][1:])
        fd.write('\t];\n')

    ## save output fields for solved case
    if 'R' in r:
        fd.write('\n#### solved values\n')
        fd.write('%sreserves.R = %s\n' % (prefix, pprint(r['R'])))
        fd.write('%sreserves.Rmin = %s\n' % (prefix, pprint(r['Rmin'])))
        fd.write('%sreserves.Rmax = %s\n' % (prefix, pprint(r['Rmax'])))
        fd.write('%sreserves.mu.l = %s\n' % (prefix, pprint(r['mu']['l'])))
        fd.write('%sreserves.mu.u = %s\n' % (prefix, pprint(r['mu']['u'])))
        fd.write('%sreserves.prc = %s\n' % (prefix, pprint(r['prc'])))
        fd.write('%sreserves.totalcost = %s\n' % (prefix, pprint(r['totalcost'])))

    return ppc
