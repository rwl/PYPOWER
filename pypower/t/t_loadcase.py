# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for C{loadcase}
"""

import os

from os.path import dirname, join

from numpy import zeros

from scipy.io import savemat

from pypower.loadcase import loadcase
from pypower.ppoption import ppoption
from pypower.runpf import runpf

from pypower.idx_gen import PC1, PC2, QC1MIN, QC1MAX, QC2MIN, QC2MAX
from pypower.idx_brch import ANGMAX, ANGMIN

from pypower.t.t_case9_pf import t_case9_pf
from pypower.t.t_case9_pfv2 import t_case9_pfv2
from pypower.t.t_case9_opf import t_case9_opf
from pypower.t.t_case9_opfv2 import t_case9_opfv2

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end


def t_loadcase(quiet=False):
    """Test that C{loadcase} works with an object as well as case file.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    t_begin(240, quiet)

    ## compare result of loading from M-file file to result of using data matrices
    tdir = dirname(__file__)
    casefile = join(tdir, 't_case9_opf')
    matfile  = join(tdir, 't_mat9_opf')
    pfcasefile = join(tdir, 't_case9_pf')
    pfmatfile  = join(tdir, 't_mat9_pf')
    casefilev2 = join(tdir, 't_case9_opfv2')
    matfilev2  = join(tdir, 't_mat9_opfv2')
    pfcasefilev2 = join(tdir, 't_case9_pfv2')
    pfmatfilev2  = join(tdir, 't_mat9_pfv2')

    ## read version 1 OPF data matrices
    baseMVA, bus, gen, branch, areas, gencost = t_case9_opf()
    ## save as .mat file
    savemat(matfile + '.mat', {'baseMVA': baseMVA, 'bus': bus, 'gen': gen,
            'branch': branch, 'areas': areas, 'gencost': gencost}, oned_as='row')

    ## read version 2 OPF data matrices
    ppc = t_case9_opfv2()
    ## save as .mat file
    savemat(matfilev2 + '.mat', {'ppc': ppc}, oned_as='column')

    ## prepare expected matrices for v1 load
    ## (missing gen cap curve & branch ang diff lims)
    tmp1 = (ppc['baseMVA'], ppc['bus'].copy(), ppc['gen'].copy(), ppc['branch'].copy(),
        ppc['areas'].copy(), ppc['gencost'].copy())
    tmp2 = (ppc['baseMVA'], ppc['bus'].copy(), ppc['gen'].copy(), ppc['branch'].copy(),
        ppc['areas'].copy(), ppc['gencost'].copy())
    ## remove capability curves, angle difference limits
    tmp1[2][1:3, [PC1, PC2, QC1MIN, QC1MAX, QC2MIN, QC2MAX]] = zeros((2,6))
    tmp1[3][0, ANGMAX] = 360
    tmp1[3][8, ANGMIN] = -360

    baseMVA, bus, gen, branch, areas, gencost = tmp1

    ##-----  load OPF data into individual matrices  -----
    t = 'loadcase(opf_PY_file_v1) without .py extension : '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = \
            loadcase(casefile, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])
    t_is(areas1,    areas,      12, [t, 'areas'])
    t_is(gencost1,  gencost,    12, [t, 'gencost'])

    t = 'loadcase(opf_PY_file_v1) with .py extension : '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = \
            loadcase(casefile + '.py', False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])
    t_is(areas1,    areas,      12, [t, 'areas'])
    t_is(gencost1,  gencost,    12, [t, 'gencost'])

    t = 'loadcase(opf_MAT_file_v1) without .mat extension : '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = \
            loadcase(matfile, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])
    t_is(areas1,    areas,      12, [t, 'areas'])
    t_is(gencost1,  gencost,    12, [t, 'gencost'])

    t = 'loadcase(opf_MAT_file_v1) with .mat extension : '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = \
            loadcase(matfile + '.mat', False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])
    t_is(areas1,    areas,      12, [t, 'areas'])
    t_is(gencost1,  gencost,    12, [t, 'gencost'])

    ## prepare expected matrices for v2 load
    baseMVA, bus, gen, branch, areas, gencost = tmp2

    t = 'loadcase(opf_PY_file_v2) without .py extension : '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = \
            loadcase(casefilev2, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])
    t_is(areas1,    areas,      12, [t, 'areas'])
    t_is(gencost1,  gencost,    12, [t, 'gencost'])

    t = 'loadcase(opf_PY_file_v2) with .py extension : '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = \
            loadcase(casefilev2 + '.py', False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])
    t_is(areas1,    areas,      12, [t, 'areas'])
    t_is(gencost1,  gencost,    12, [t, 'gencost'])

    t = 'loadcase(opf_MAT_file_v2) without .mat extension : '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = \
            loadcase(matfilev2, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])
    t_is(areas1,    areas,      12, [t, 'areas'])
    t_is(gencost1,  gencost,    12, [t, 'gencost'])

    t = 'loadcase(opf_MAT_file_v2) with .mat extension : '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = \
            loadcase(matfilev2 + '.mat', False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])
    t_is(areas1,    areas,      12, [t, 'areas'])
    t_is(gencost1,  gencost,    12, [t, 'gencost'])

    ## prepare expected matrices for v1 load
    baseMVA, bus, gen, branch, areas, gencost = tmp1

    t = 'loadcase(opf_struct_v1) (no version): '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = t_case9_opf()
    c = {}
    c['baseMVA']   = baseMVA1
    c['bus']       = bus1.copy()
    c['gen']       = gen1.copy()
    c['branch']    = branch1.copy()
    c['areas']     = areas1.copy()
    c['gencost']   = gencost1.copy()
    baseMVA2, bus2, gen2, branch2, areas2, gencost2 = loadcase(c, False)
    t_is(baseMVA2,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus2,      bus,        12, [t, 'bus'])
    t_is(gen2,      gen,        12, [t, 'gen'])
    t_is(branch2,   branch,     12, [t, 'branch'])
    t_is(areas2,    areas,      12, [t, 'areas'])
    t_is(gencost2,  gencost,    12, [t, 'gencost'])

    t = 'loadcase(opf_struct_v1) (version=\'1\'): '
    c['version']   = '1'
    baseMVA2, bus2, gen2, branch2, areas2, gencost2 = loadcase(c, False)
    t_is(baseMVA2,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus2,      bus,        12, [t, 'bus'])
    t_is(gen2,      gen,        12, [t, 'gen'])
    t_is(branch2,   branch,     12, [t, 'branch'])
    t_is(areas2,    areas,      12, [t, 'areas'])
    t_is(gencost2,  gencost,    12, [t, 'gencost'])

    ## prepare expected matrices for v2 load
    baseMVA, bus, gen, branch, areas, gencost = tmp2

    t = 'loadcase(opf_struct_v2) (no version): '
    c = {}
    c['baseMVA']   = baseMVA
    c['bus']       = bus.copy()
    c['gen']       = gen.copy()
    c['branch']    = branch.copy()
    c['areas']     = areas.copy()
    c['gencost']   = gencost.copy()
    baseMVA2, bus2, gen2, branch2, areas2, gencost2 = loadcase(c, False)
    t_is(baseMVA2,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus2,      bus,        12, [t, 'bus'])
    t_is(gen2,      gen,        12, [t, 'gen'])
    t_is(branch2,   branch,     12, [t, 'branch'])
    t_is(areas2,    areas,      12, [t, 'areas'])
    t_is(gencost2,  gencost,    12, [t, 'gencost'])

    t = 'loadcase(opf_struct_v2) (version=''2''): '
    c = {}
    c['baseMVA']   = baseMVA
    c['bus']       = bus.copy()
    c['gen']       = gen.copy()
    c['branch']    = branch.copy()
    c['areas']     = areas.copy()
    c['gencost']   = gencost.copy()
    c['version']   = '2'
    baseMVA2, bus2, gen2, branch2, areas2, gencost2 = loadcase(c, False)
    t_is(baseMVA2,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus2,      bus,        12, [t, 'bus'])
    t_is(gen2,      gen,        12, [t, 'gen'])
    t_is(branch2,   branch,     12, [t, 'branch'])
    t_is(areas2,    areas,      12, [t, 'areas'])
    t_is(gencost2,  gencost,    12, [t, 'gencost'])

    ##-----  load OPF data into struct  -----
    ## prepare expected matrices for v1 load
    baseMVA, bus, gen, branch, areas, gencost = tmp1

    t = 'ppc = loadcase(opf_PY_file_v1) without .py extension : '
    ppc1 = loadcase(casefile)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_PY_file_v1) with .py extension : '
    ppc1 = loadcase(casefile + '.py')
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_MAT_file_v1) without .mat extension : '
    ppc1 = loadcase(matfile)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_MAT_file_v1) with .mat extension : '
    ppc1 = loadcase(matfile + '.mat')
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    ## prepare expected matrices for v2 load
    baseMVA, bus, gen, branch, areas, gencost = tmp2

    t = 'ppc = loadcase(opf_PY_file_v2) without .m extension : '
    ppc1 = loadcase(casefilev2)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_PY_file_v2) with .py extension : '
    ppc1 = loadcase(casefilev2 + '.py')
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_MAT_file_v2) without .mat extension : '
    ppc1 = loadcase(matfilev2)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_MAT_file_v2) with .mat extension : '
    ppc1 = loadcase(matfilev2 + '.mat')
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    ## prepare expected matrices for v1 load
    baseMVA, bus, gen, branch, areas, gencost = tmp1

    t = 'ppc = loadcase(opf_struct_v1) (no version): '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = t_case9_opf()
    c = {}
    c['baseMVA']   = baseMVA1
    c['bus']       = bus1.copy()
    c['gen']       = gen1.copy()
    c['branch']    = branch1.copy()
    c['areas']     = areas1.copy()
    c['gencost']   = gencost1.copy()
    ppc2 = loadcase(c)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc2['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc2['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_struct_v1) (version=''1''): '
    c['version']   = '1'
    ppc2 = loadcase(c)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc2['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc2['gencost'],  gencost,    12, [t, 'gencost'])

    ## prepare expected matrices for v2 load
    baseMVA, bus, gen, branch, areas, gencost = tmp2

    t = 'ppc = loadcase(opf_struct_v2) (no version): '
    c = {}
    c['baseMVA']   = baseMVA
    c['bus']       = bus.copy()
    c['gen']       = gen.copy()
    c['branch']    = branch.copy()
    c['areas']     = areas.copy()
    c['gencost']   = gencost.copy()
    ppc2 = loadcase(c)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc2['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc2['gencost'],  gencost,    12, [t, 'gencost'])
    t_ok(ppc2['version'] == '2', [t, 'version'])

    t = 'ppc = loadcase(opf_struct_v2) (version=''2''): '
    c = {}
    c['baseMVA']   = baseMVA
    c['bus']       = bus.copy()
    c['gen']       = gen.copy()
    c['branch']    = branch.copy()
    c['areas']     = areas.copy()
    c['gencost']   = gencost.copy()
    c['version']   = '2'
    ppc2 = loadcase(c)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc2['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc2['gencost'],  gencost,    12, [t, 'gencost'])


    ## read version 1 PF data matrices
    baseMVA, bus, gen, branch = t_case9_pf()
    savemat(pfmatfile + '.mat',
        {'baseMVA': baseMVA, 'bus': bus, 'gen': gen, 'branch': branch},
        oned_as='column')

    ## read version 2 PF data matrices
    ppc = t_case9_pfv2()
    tmp = (ppc['baseMVA'], ppc['bus'].copy(),
           ppc['gen'].copy(), ppc['branch'].copy())
    baseMVA, bus, gen, branch = tmp
    ## save as .mat file
    savemat(pfmatfilev2 + '.mat', {'ppc': ppc}, oned_as='column')

    ##-----  load PF data into individual matrices  -----
    t = 'loadcase(pf_PY_file_v1) without .py extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfcasefile, False, False, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_PY_file_v1) with .py extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfcasefile + '.py', False, False, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_MAT_file_v1) without .mat extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfmatfile, False, False, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_MAT_file_v1) with .mat extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfmatfile + '.mat', False, False, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_PY_file_v2) without .py extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfcasefilev2, False, False, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_PY_file_v2) with .py extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfcasefilev2 + '.py', False, False, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_MAT_file_v2) without .mat extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfmatfilev2, False, False, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_MAT_file_v2) with .mat extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfmatfilev2 + '.mat', False, False, False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_struct_v1) (no version): '
    baseMVA1, bus1, gen1, branch1 = t_case9_pf()
    c = {}
    c['baseMVA']   = baseMVA1
    c['bus']       = bus1.copy()
    c['gen']       = gen1.copy()
    c['branch']    = branch1.copy()
    baseMVA2, bus2, gen2, branch2 = loadcase(c, False, False, False)
    t_is(baseMVA2,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus2,      bus,        12, [t, 'bus'])
    t_is(gen2,      gen,        12, [t, 'gen'])
    t_is(branch2,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_struct_v1) (version=''1''): '
    c['version']   = '1'
    baseMVA2, bus2, gen2, branch2 = loadcase(c, False, False, False)
    t_is(baseMVA2,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus2,      bus,        12, [t, 'bus'])
    t_is(gen2,      gen,        12, [t, 'gen'])
    t_is(branch2,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_struct_v2) : '
    c = {}
    c['baseMVA']   = baseMVA
    c['bus']       = bus.copy()
    c['gen']       = gen.copy()
    c['branch']    = branch.copy()
    c['version']   = '2'
    baseMVA2, bus2, gen2, branch2 = loadcase(c, False, False, False)
    t_is(baseMVA2,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus2,      bus,        12, [t, 'bus'])
    t_is(gen2,      gen,        12, [t, 'gen'])
    t_is(branch2,   branch,     12, [t, 'branch'])






    ##-----  load PF data into struct  -----
    t = 'ppc = loadcase(pf_PY_file_v1) without .py extension : '
    ppc1 = loadcase(pfcasefile)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_PY_file_v1) with .py extension : '
    ppc1 = loadcase(pfcasefile + '.py')
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_MAT_file_v1) without .mat extension : '
    ppc1 = loadcase(pfmatfile)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_MAT_file_v1) with .mat extension : '
    ppc1 = loadcase(pfmatfile + '.mat')
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_PY_file_v2) without .py extension : '
    ppc1 = loadcase(pfcasefilev2)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_PY_file_v2) with .py extension : '
    ppc1 = loadcase(pfcasefilev2 + '.py')
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_MAT_file_v2) without .mat extension : '
    ppc1 = loadcase(pfmatfilev2)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_MAT_file_v2) with .mat extension : '
    ppc1 = loadcase(pfmatfilev2 + '.mat')
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_struct_v1) (no version): '
    baseMVA1, bus1, gen1, branch1 = t_case9_pf()
    c = {}
    c['baseMVA']   = baseMVA1
    c['bus']       = bus1.copy()
    c['gen']       = gen1.copy()
    c['branch']    = branch1.copy()
    ppc2 = loadcase(c)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_struct_v1) (version=''1''): '
    c['version']   = '1'
    ppc2 = loadcase(c)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_struct_v2) : '
    c = {}
    c['baseMVA']   = baseMVA
    c['bus']       = bus.copy()
    c['gen']       = gen.copy()
    c['branch']    = branch.copy()
    c['version']   = '2'
    ppc2 = loadcase(c)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])

    ## cleanup
    os.remove(matfile + '.mat')
    os.remove(pfmatfile + '.mat')
    os.remove(matfilev2 + '.mat')
    os.remove(pfmatfilev2 + '.mat')

    t = 'runpf(my_PY_file)'
    ppopt = ppoption(VERBOSE=0, OUT_ALL=0)
    results3, success = runpf(pfcasefile, ppopt)
    baseMVA3, bus3, gen3, branch3 = results3['baseMVA'], results3['bus'], \
            results3['gen'], results3['branch']
    t_ok( success, t )

    t = 'runpf(my_object)'
    results4, success = runpf(c, ppopt)
    baseMVA4, bus4, gen4, branch4 = results4['baseMVA'], results4['bus'], \
            results4['gen'], results4['branch']
    t_ok( success, t )

    t = 'runpf result comparison : '
    t_is(baseMVA3,  baseMVA4,   12, [t, 'baseMVA'])
    t_is(bus3,      bus4,       12, [t, 'bus'])
    t_is(gen3,      gen4,       12, [t, 'gen'])
    t_is(branch3,   branch4,    12, [t, 'branch'])

    t = 'runpf(modified_struct)'
    c['gen'][2, 1] = c['gen'][2, 1] + 1            ## increase gen 3 output by 1
    results5, success = runpf(c, ppopt)
    gen5 = results5['gen']
    t_is(gen5[0, 1], gen4[0, 1] - 1, 1, t)   ## slack bus output should decrease by 1

    t_end()


if __name__ == '__main__':
    t_loadcase(False)
