# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

"""Tests for constr-based optimal power flow.
"""

from os.path import dirname, join

from scipy.io import loadmat

from pypower.ppoption import ppoption
from pypower.runopf import runopf

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end


def t_opf_constr(quiet=False):
    """Tests for constr-based optimal power flow.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    num_tests = 10

    t_begin(num_tests, quiet)

    tdir = dirname(__file__)
    casefile = join(tdir, 't_case9_opf')

    verbose = 0#not quiet

    ppopt = ppoption(OUT_ALL=0, VERBOSE=verbose)

    ## get solved AC power flow case from MAT-file
    soln9_opf = loadmat(join(tdir, 'soln9_opf.mat'), struct_as_record=False)
    bus_soln = soln9_opf['bus_soln']
    gen_soln = soln9_opf['gen_soln']
    branch_soln = soln9_opf['branch_soln']
    f_soln = soln9_opf['f_soln']

    ## run constr OPF
    t = 'constr OPF : '
    ppopt = ppoption(ppopt, OPF_ALG=200)
    _, bus, gen, _, branch, f, success, _ = runopf(casefile, ppopt)
    t_ok(success, [t, 'success'])
    t_is(f, f_soln, 2, [t, 'f'])
    t_is(bus, bus_soln, 2, [t, 'bus'])
    t_is(gen, gen_soln, 2, [t, 'gen'])
    t_is(branch, branch_soln, 2, [t, 'branch'])

    ## get solved AC power flow case from MAT-file
    soln9_opf_Plim = loadmat(join(tdir, 'soln9_opf_Plim.mat'), struct_as_record=False)
    bus_soln = soln9_opf_Plim['bus_soln']
    gen_soln = soln9_opf_Plim['gen_soln']
    branch_soln = soln9_opf_Plim['branch_soln']
    f_soln = soln9_opf_Plim['f_soln']

    ## run constr OPF with active power line limits
    t = 'constr OPF (P line lim) : '
    ppopt = ppoption(ppopt, OPF_FLOW_LIM=1, OPF_ALG=200)
    _, bus, gen, _, branch, f, success, _ = runopf(casefile, ppopt)
    t_ok(success, [t, 'success'])
    t_is(f, f_soln, 2, [t, 'f'])
    t_is(bus, bus_soln, 2, [t, 'bus'])
    t_is(gen, gen_soln, 2, [t, 'gen'])
    t_is(branch, branch_soln, 2, [t, 'branch'])

    t_end()


if __name__ == '__main__':
    t_opf_constr(quiet=False)
