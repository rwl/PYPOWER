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

"""Tests for C{loadcase}
"""

import os

from os.path import dirname, join

from scipy.io import savemat

from pypower.loadcase import loadcase
from pypower.ppoption import ppoption
from pypower.runpf import runpf

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
    @author: Richard Lincoln
    """
    t_begin(227, quiet)

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
    baseMVA, bus, gen, branch, areas, gencost = ppc['baseMVA'], ppc['bus'], \
        ppc['gen'], ppc['branch'], ppc['areas'], ppc['gencost']
    ## save as .mat file
    savemat(matfilev2 + '.mat', {'ppc': ppc}, oned_as='column')

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

    t = 'loadcase(opf_struct_v2): '
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

    ##-----  load OPF data into dict  -----

    t = 'ppc = loadcase(opf_PY_file_v1) without .py extension : '
    ppc1 = loadcase(casefile, return_as_dict=True)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_PY_file_v1) with .py extension : '
    ppc1 = loadcase(casefile + '.py', return_as_dict=True)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_MAT_file_v1) without .mat extension : '
    ppc1 = loadcase(matfile, return_as_dict=True)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_MAT_file_v1) with .mat extension : '
    ppc1 = loadcase(matfile + '.mat', return_as_dict=True)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_PY_file_v2) without .m extension : '
    ppc1 = loadcase(casefilev2, return_as_dict=True)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_PY_file_v2) with .py extension : '
    ppc1 = loadcase(casefilev2 + '.py', return_as_dict=True)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_MAT_file_v2) without .mat extension : '
    ppc1 = loadcase(matfilev2, return_as_dict=True)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_MAT_file_v2) with .mat extension : '
    ppc1 = loadcase(matfilev2 + '.mat', return_as_dict=True)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc1['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc1['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_struct_v1) (no version): '
    baseMVA1, bus1, gen1, branch1, areas1, gencost1 = t_case9_opf()
    c = {}
    c['baseMVA']   = baseMVA1
    c['bus']       = bus1.copy()
    c['gen']       = gen1.copy()
    c['branch']    = branch1.copy()
    c['areas']     = areas1.copy()
    c['gencost']   = gencost1.copy()
    ppc2 = loadcase(c, return_as_dict=True)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc2['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc2['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_struct_v1) (version=\'1\'): '
    c['version']   = '1'
    ppc2 = loadcase(c, return_as_dict=True)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])
    t_is(ppc2['areas'],    areas,      12, [t, 'areas'])
    t_is(ppc2['gencost'],  gencost,    12, [t, 'gencost'])

    t = 'ppc = loadcase(opf_struct_v2) (no version): '
    c = {}
    c['baseMVA']   = baseMVA
    c['bus']       = bus.copy()
    c['gen']       = gen.copy()
    c['branch']    = branch.copy()
    c['areas']     = areas.copy()
    c['gencost']   = gencost.copy()
    ppc2 = loadcase(c, return_as_dict=True)
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
            loadcase(pfcasefile, expect_opf_data=False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_PY_file_v1) with .py extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfcasefile + '.py', expect_opf_data=False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_MAT_file_v1) without .mat extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfmatfile, expect_opf_data=False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_MAT_file_v1) with .mat extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfmatfile + '.mat', expect_opf_data=False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_PY_file_v2) without .py extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfcasefilev2, expect_opf_data=False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_PY_file_v2) with .py extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfcasefilev2 + '.py', expect_opf_data=False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_MAT_file_v2) without .mat extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfmatfilev2, expect_opf_data=False)
    t_is(baseMVA1,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus1,      bus,        12, [t, 'bus'])
    t_is(gen1,      gen,        12, [t, 'gen'])
    t_is(branch1,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_MAT_file_v2) with .mat extension : '
    baseMVA1, bus1, gen1, branch1 = \
            loadcase(pfmatfilev2 + '.mat', expect_opf_data=False)
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
    baseMVA2, bus2, gen2, branch2 = loadcase(c, expect_opf_data=False)
    t_is(baseMVA2,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus2,      bus,        12, [t, 'bus'])
    t_is(gen2,      gen,        12, [t, 'gen'])
    t_is(branch2,   branch,     12, [t, 'branch'])

    t = 'loadcase(pf_struct_v1) (version=''1''): '
    c['version']   = '1'
    baseMVA2, bus2, gen2, branch2 = loadcase(c, expect_opf_data=False)
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
    baseMVA2, bus2, gen2, branch2 = loadcase(c, expect_opf_data=False)
    t_is(baseMVA2,  baseMVA,    12, [t, 'baseMVA'])
    t_is(bus2,      bus,        12, [t, 'bus'])
    t_is(gen2,      gen,        12, [t, 'gen'])
    t_is(branch2,   branch,     12, [t, 'branch'])






    ##-----  load PF data into struct  -----
    t = 'ppc = loadcase(pf_PY_file_v1) without .py extension : '
    ppc1 = loadcase(pfcasefile, return_as_dict=True, expect_opf_data=False)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_PY_file_v1) with .py extension : '
    ppc1 = loadcase(pfcasefile + '.py', return_as_dict=True, expect_opf_data=False)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_MAT_file_v1) without .mat extension : '
    ppc1 = loadcase(pfmatfile, return_as_dict=True, expect_opf_data=False)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_MAT_file_v1) with .mat extension : '
    ppc1 = loadcase(pfmatfile + '.mat', return_as_dict=True, expect_opf_data=False)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_PY_file_v2) without .py extension : '
    ppc1 = loadcase(pfcasefilev2, return_as_dict=True, expect_opf_data=False)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_PY_file_v2) with .py extension : '
    ppc1 = loadcase(pfcasefilev2 + '.py', return_as_dict=True, expect_opf_data=False)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_MAT_file_v2) without .mat extension : '
    ppc1 = loadcase(pfmatfilev2, return_as_dict=True, expect_opf_data=False)
    t_is(ppc1['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc1['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc1['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc1['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_MAT_file_v2) with .mat extension : '
    ppc1 = loadcase(pfmatfilev2 + '.mat', return_as_dict=True, expect_opf_data=False)
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
    ppc2 = loadcase(c, return_as_dict=True, expect_opf_data=False)
    t_is(ppc2['baseMVA'],  baseMVA,    12, [t, 'baseMVA'])
    t_is(ppc2['bus'],      bus,        12, [t, 'bus'])
    t_is(ppc2['gen'],      gen,        12, [t, 'gen'])
    t_is(ppc2['branch'],   branch,     12, [t, 'branch'])

    t = 'ppc = loadcase(pf_struct_v1) (version=''1''): '
    c['version']   = '1'
    ppc2 = loadcase(c, return_as_dict=True, expect_opf_data=False)
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
    ppc2 = loadcase(c, return_as_dict=True, expect_opf_data=False)
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
    baseMVA3, bus3, gen3, branch3, success, _ = runpf(pfcasefile, ppopt,
                                                      expect_opf_data=False)
    t_ok( success, t )

    t = 'runpf(my_object)'
    baseMVA4, bus4, gen4, branch4, success, _ = runpf(c, ppopt,
                                                      expect_opf_data=False)
    t_ok( success, t )

    t = 'runpf result comparison : '
    t_is(baseMVA3,  baseMVA4,   12, [t, 'baseMVA'])
    t_is(bus3,      bus4,       12, [t, 'bus'])
    t_is(gen3,      gen4,       12, [t, 'gen'])
    t_is(branch3,   branch4,    12, [t, 'branch'])

    t = 'runpf(modified_dict)'
    c['gen'][2, 1] = c['gen'][2, 1] + 1            ## increase gen 3 output by 1
    _, _, gen5, _, success, _ = runpf(c, ppopt, expect_opf_data=False)
    t_is(gen5[0, 1], gen4[0, 1] - 1, 1, t)   ## slack bus output should decrease by 1

    t_end()


if __name__ == '__main__':
    t_loadcase(False)
