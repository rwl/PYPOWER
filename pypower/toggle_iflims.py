# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Enable or disable set of interface flow constraints.
"""

from sys import stderr

from pprint import pprint

from numpy import zeros, arange, unique, sign, delete, flatnonzero as find

from scipy.sparse import lil_matrix, csr_matrix as sparse

from pypower.add_userfcn import add_userfcn
from pypower.remove_userfcn import remove_userfcn
from pypower.makeBdc import makeBdc
from pypower.idx_brch import PF


def toggle_iflims(ppc, on_off):
    """Enable or disable set of interface flow constraints.

    Enables or disables a set of OPF userfcn callbacks to implement
    interface flow limits based on a DC flow model.

    These callbacks expect to find an 'if' field in the input C{ppc}, where
    C{ppc['if']} is a dict with the following fields:
        - C{map}     C{n x 2}, defines each interface in terms of a set of
        branch indices and directions. Interface I is defined
        by the set of rows whose 1st col is equal to I. The
        2nd column is a branch index multiplied by 1 or -1
        respectively for lines whose orientation is the same
        as or opposite to that of the interface.
        - C{lims}    C{nif x 3}, defines the DC model flow limits in MW
        for specified interfaces. The 2nd and 3rd columns specify
        the lower and upper limits on the (DC model) flow
        across the interface, respectively. Normally, the lower
        limit is negative, indicating a flow in the opposite
        direction.

    The 'int2ext' callback also packages up results and stores them in
    the following output fields of C{results['if']}:
        - C{P}       - C{nif x 1}, actual flow across each interface in MW
        - C{mu.l}    - C{nif x 1}, shadow price on lower flow limit, ($/MW)
        - C{mu.u}    - C{nif x 1}, shadow price on upper flow limit, ($/MW)

    @see: L{add_userfcn}, L{remove_userfcn}, L{run_userfcn},
        L{t.t_case30_userfcns}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    if on_off == 'on':
        ## check for proper reserve inputs
        if ('if' not in ppc) | (not isinstance(ppc['if'], dict)) | \
                ('map' not in ppc['if']) | \
                ('lims' not in ppc['if']):
            stderr.write('toggle_iflims: case must contain an \'if\' field, a struct defining \'map\' and \'lims\'')

        ## add callback functions
        ## note: assumes all necessary data included in 1st arg (ppc, om, results)
        ##       so, no additional explicit args are needed
        ppc = add_userfcn(ppc, 'ext2int', userfcn_iflims_ext2int)
        ppc = add_userfcn(ppc, 'formulation', userfcn_iflims_formulation)
        ppc = add_userfcn(ppc, 'int2ext', userfcn_iflims_int2ext)
        ppc = add_userfcn(ppc, 'printpf', userfcn_iflims_printpf)
        ppc = add_userfcn(ppc, 'savecase', userfcn_iflims_savecase)
    elif on_off == 'off':
        ppc = remove_userfcn(ppc, 'savecase', userfcn_iflims_savecase)
        ppc = remove_userfcn(ppc, 'printpf', userfcn_iflims_printpf)
        ppc = remove_userfcn(ppc, 'int2ext', userfcn_iflims_int2ext)
        ppc = remove_userfcn(ppc, 'formulation', userfcn_iflims_formulation)
        ppc = remove_userfcn(ppc, 'ext2int', userfcn_iflims_ext2int)
    else:
        stderr.write('toggle_iflims: 2nd argument must be either \'on\' or \'off\'')

    return ppc


def userfcn_iflims_ext2int(ppc, *args):
    """This is the 'ext2int' stage userfcn callback that prepares the input
    data for the formulation stage. It expects to find an 'if' field in
    ppc as described above. The optional args are not currently used.
    """
    ## initialize some things
    ifmap = ppc['if']['map']
    o = ppc['order']
    nl0 = o['ext']['branch'].shape[0]    ## original number of branches
    nl = ppc['branch'].shape[0]          ## number of on-line branches

    ## save if.map for external indexing
    ppc['order']['ext']['ifmap'] = ifmap

    ##-----  convert stuff to internal indexing  -----
    e2i = zeros(nl0)
    e2i[o['branch']['status']['on']] = arange(nl)  ## ext->int branch index mapping
    d = sign(ifmap[:, 1])
    br = abs(ifmap[:, 1]).astype(int)
    ifmap[:, 1] = d * e2i[br]

    ifmap = delete(ifmap, find(ifmap[:, 1] == 0), 0)  ## delete branches that are out

    ppc['if']['map'] = ifmap

    return ppc


def userfcn_iflims_formulation(om, *args):
    """This is the 'formulation' stage userfcn callback that defines the
    user costs and constraints for interface flow limits. It expects to
    find an 'if' field in the ppc stored in om, as described above. The
    optional args are not currently used.
    """
    ## initialize some things
    ppc = om.get_ppc()
    baseMVA, bus, branch = ppc['baseMVA'], ppc['bus'], ppc['branch']
    ifmap = ppc['if']['map']
    iflims = ppc['if']['lims']

    ## form B matrices for DC model
    _, Bf, _, Pfinj = makeBdc(baseMVA, bus, branch)
    n = Bf.shape[1]                    ## dim of theta

    ## form constraints
    ifidx = unique(iflims[:, 0])   ## interface number list
    nifs = len(ifidx)              ## number of interfaces
    Aif = lil_matrix((nifs, n))
    lif = zeros(nifs)
    uif = zeros(nifs)
    for k in range(nifs):
        ## extract branch indices
        br = ifmap[ifmap[:, 0] == ifidx[k], 1]
        if len(br) == 0:
            stderr.write('userfcn_iflims_formulation: interface %d has no in-service branches\n' % k)

        d = sign(br)
        br = abs(br)
        Ak = sparse((1, n))              ## Ak = sum( d(i) * Bf(i, :) )
        bk = 0                           ## bk = sum( d(i) * Pfinj(i) )
        for i in range(len(br)):
            Ak = Ak + d[i] * Bf[br[i], :]
            bk = bk + d[i] * Pfinj[br[i]]

        Aif[k, :] = Ak
        lif[k] = iflims[k, 1] / baseMVA - bk
        uif[k] = iflims[k, 2] / baseMVA - bk

    ## add interface constraint
    om.add_constraints('iflims',  Aif, lif, uif, ['Va'])      ## nifs

    return om


def userfcn_iflims_int2ext(results, *args):
    """This is the 'int2ext' stage userfcn callback that converts everything
    back to external indexing and packages up the results. It expects to
    find an 'if' field in the C{results} dict as described for ppc above.
    It also expects the results to contain solved branch flows and linear
    constraints named 'iflims' which are used to populate output fields
    in C{results['if']}. The optional args are not currently used.
    """
    ## get internal ifmap
    ifmap = results['if']['map']
    iflims = results['if']['lims']

    ##-----  convert stuff back to external indexing  -----
    results['if']['map'] = results['order']['ext']['ifmap']

    ##-----  results post-processing  -----
    ifidx = unique(iflims[:, 0])   ## interface number list
    nifs = len(ifidx)           ## number of interfaces
    results['if']['P'] = zeros(nifs)
    for k in range(nifs):
        ## extract branch indices
        br = ifmap[ifmap[:, 0] == ifidx[k], 1]
        d = sign(br)
        br = abs(br)
        results['if']['P'][k] = sum( d * results['branch'][br, PF] )

    if 'mu' not in results['if']:
        results['if']['mu'] = {}
    results['if']['mu']['l'] = results['lin']['mu']['l']['iflims']
    results['if']['mu']['u'] = results['lin']['mu']['u']['iflims']

    return results


def userfcn_iflims_printpf(results, fd, ppopt, *args):
    """This is the 'printpf' stage userfcn callback that pretty-prints the
    results. It expects a C{results} dict, a file descriptor and a PYPOWER
    options vector. The optional args are not currently used.
    """
    ##-----  print results  -----
    OUT_ALL = ppopt['OUT_ALL']
    # ctol = ppopt['OPF_VIOLATION']   ## constraint violation tolerance
    ptol = 1e-6        ## tolerance for displaying shadow prices

    if OUT_ALL != 0:
        iflims = results['if']['lims']
        fd.write('\n================================================================================')
        fd.write('\n|     Interface Flow Limits                                                    |')
        fd.write('\n================================================================================')
        fd.write('\n Interface  Shadow Prc  Lower Lim      Flow      Upper Lim   Shadow Prc')
        fd.write('\n     #        ($/MW)       (MW)        (MW)        (MW)       ($/MW)   ')
        fd.write('\n----------  ----------  ----------  ----------  ----------  -----------')
        ifidx = unique(iflims[:, 0])   ## interface number list
        nifs = len(ifidx)           ## number of interfaces
        for k in range(nifs):
            fd.write('\n%6d ', iflims(k, 1))
            if results['if']['mu']['l'][k] > ptol:
                fd.write('%14.3f' % results['if']['mu']['l'][k])
            else:
                fd.write('          -   ')

            fd.write('%12.2f%12.2f%12.2f' % (iflims[k, 1], results['if']['P'][k], iflims[k, 2]))
            if results['if']['mu']['u'][k] > ptol:
                fd.write('%13.3f' % results['if']['mu']['u'][k])
            else:
                fd.write('         -     ')

        fd.write('\n')

    return results


def userfcn_iflims_savecase(ppc, fd, prefix, *args):
    """This is the 'savecase' stage userfcn callback that prints the Python
    file code to save the 'if' field in the case file. It expects a
    PYPOWER case dict (ppc), a file descriptor and variable prefix
    (usually 'ppc'). The optional args are not currently used.
    """
    ifmap = ppc['if']['map']
    iflims = ppc['if']['lims']

    fd.write('\n####-----  Interface Flow Limit Data  -----####\n')
    fd.write('#### interface<->branch map data\n')
    fd.write('##\tifnum\tbranchidx (negative defines opposite direction)\n')
    fd.write('%sif.map = [\n' % prefix)
    fd.write('\t%d\t%d;\n' % ifmap.T)
    fd.write('];\n')

    fd.write('\n#### interface flow limit data (based on DC model)\n')
    fd.write('#### (lower limit should be negative for opposite direction)\n')
    fd.write('##\tifnum\tlower\tupper\n')
    fd.write('%sif.lims = [\n' % prefix)
    fd.write('\t%d\t%g\t%g;\n' % iflims.T)
    fd.write('];\n')

    ## save output fields for solved case
    if ('P' in ppc['if']):
        fd.write('\n#### solved values\n')
        fd.write('%sif.P = %s\n' % (prefix, pprint(ppc['if']['P'])))
        fd.write('%sif.mu.l = %s\n' % (prefix, pprint(ppc['if']['mu']['l'])))
        fd.write('%sif.mu.u = %s\n' % (prefix, pprint(ppc['if']['mu']['u'])))

    return ppc
