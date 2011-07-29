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

"""Tests for DC optimal power flow.
"""

from os.path import dirname, join

from scipy.io import loadmat

from pypower.ppoption import ppoption
from pypower.rundcopf import rundcopf

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_ok import t_ok
from pypower.t.t_end import t_end


def t_opf_dc(quiet=False):
    """Tests for DC optimal power flow.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    num_tests = 5

    t_begin(num_tests, quiet)

    tdir = dirname(__file__)
    casefile = join(tdir, 't_case9_opf')
    verbose = 0#not quiet

    ppopt = ppoption(OUT_ALL=0, VERBOSE=verbose)

    ## get solved DC power flow case from MAT-file
    soln9_dcopf = loadmat(join(tdir, 'soln9_dcopf.mat'), struct_as_record=False)
    bus_soln = soln9_dcopf['bus_soln']
    gen_soln = soln9_dcopf['gen_soln']
    branch_soln = soln9_dcopf['branch_soln']
    f_soln = soln9_dcopf['f_soln']

    ## run DC OPF
    t = 'DC OPF : '
    ppopt = ppoption(ppopt, OUT_ALL=0, VERBOSE=verbose)
    _, bus, gen, _, branch, f, success, _ = rundcopf(casefile, ppopt)
    t_ok(success, [t, 'success'])
    t_is(f, f_soln, 3, [t, 'f'])
    t_is(bus, bus_soln, 3, [t, 'bus'])
    t_is(gen, gen_soln, 3, [t, 'gen'])
    t_is(branch, branch_soln, 3, [t, 'branch'])

    t_end()


if __name__ == '__main__':
    t_opf_dc(False)
