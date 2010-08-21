# Copyright (C) 2000-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

from numpy import array, ones, nonzero
from scipy.sparse import csr_matrix

from idx_bus import *
from idx_gen import *
from idx_brch import *
from idx_cost import *

def dcopf_solver(om, mpopt, out_opt=None):
    """Solves a DC optimal power flow.

    Inputs are an OPF model object, a MATPOWER options vector and
    a struct containing fields (can be empty) for each of the desired
    optional output fields.

    Outputs are a RESULTS struct, SUCCESS flag and RAW output struct.

    RESULTS is a MATPOWER case struct (mpc) with the usual baseMVA, bus
    branch, gen, gencost fields, along with the following additional
    fields:
        .order      see 'help ext2int' for details of this field
        .x          final value of optimization variables (internal order)
        .f          final objective function value
        .mu         shadow prices on ...
            .var
                .l  lower bounds on variables
                .u  upper bounds on variables
            .lin
                .l  lower bounds on linear constraints
                .u  upper bounds on linear constraints
        .g          (optional) constraint values
        .dg         (optional) constraint 1st derivatives
        .df         (optional) obj fun 1st derivatives (not yet implemented)
        .d2f        (optional) obj fun 2nd derivatives (not yet implemented)

    SUCCESS     1 if solver converged successfully, 0 otherwise

    RAW         raw output in form returned by MINOS
        .xr     final value of optimization variables
        .pimul  constraint multipliers
        .info   solver specific termination code
        .output solver specific output information

    @see: L{opf}, L{qps_pypower}
    """
    if out_opt is None:
        out_opt = {}

    ## options
    verbose = mpopt[31]    ## VERBOSE
    alg     = mpopt[26]    ## OPF_ALG_DC

    if alg == 0:
        alg = 200

    ## unpack data
    mpc = om.get_mpc()
    baseMVA, bus, gen, branch, gencost = \
        mpc["baseMVA"], mpc["bus"], mpc["gen"], mpc["branch"], mpc["gencost"]
    cp = om.get_cost_params()
    N, H, Cw = cp["N"], cp["H"], cp["Cw"]
    fparm = array([cp["dd"], cp["rh"], cp["kk"], cp["mm"]])
    Bf = om.userdata('Bf')
    Pfinj = om.userdata('Pfinj')
    vv, ll = om.get_idx()

    ## problem dimensions
    ipol = nonzero(gencost[:, MODEL] == POLYNOMIAL) ## polynomial costs
    ipwl = nonzero(gencost[:, MODEL] == PW_LINEAR)  ## piece-wise linear costs
    nb = bus.shape[0]              ## number of buses
    nl = branch.shape[0]           ## number of branches
    nw = N.shape[0]                ## number of general cost vars, w
    ny = om.getN('var', 'y')      ## number of piece-wise linear costs
    nxyz = om.getN('var')        ## total number of control vars of all types

    ## linear constraints & variable bounds
    A, l, u = om.linear_constraints()
    x0, xmin, xmax = om.getv()

    ## set up objective function of the form: f = 1/2 * X'*HH*X + CC'*X
    ## where X = [x;y;z]. First set up as quadratic function of w,
    ## f = 1/2 * w'*HHw*w + CCw'*w, where w = diag(M) * (N*X - Rhat). We
    ## will be building on the (optionally present) user supplied parameters.

    ## piece-wise linear costs
    any_pwl = ny > 0
    if any_pwl:
        Npwl = csr_matrix(ones(ny,1), vv.i1.y-1+ipwl, 1, 1, nxyz) ## sum of y vars
        Hpwl = 0
        Cpwl = 1
        fparm_pwl = array([1, 0, 0, 1])
    else:
        Npwl = csr_matrix((0, nxyz))
        Hpwl = array([])
        Cpwl = array([])
        fparm_pwl = array([])