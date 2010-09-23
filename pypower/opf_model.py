# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

import logging

from numpy import ones, Inf
from scipy.sparse import csr_matrix as sparse

logger = logging.getLogger(__name__)

class opf_model(object):
    """This class implements the OPF model object used to encapsulate
    a given OPF problem formulation. It allows for access to optimization
    variables, constraints and costs in named blocks, keeping track of the
    ordering and indexing of the blocks as variables, constraints and costs
    are added to the problem.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """

    def __init__(self, ppc):
        #: PYPOWER case dict used to build the object.
        self.ppc = ppc

        self.var = {}
        self.nln = {}
        self.lin = {}
        self.cost = {}


    def add_constraints(self, name, AorN, l, u=None, varsets=None):
        """Adds a set of constraints to the model.

        Linear constraints are of the form L <= A * x <= U, where
        x is a vector made of of the vars specified in VARSETS (in
        the order given). This allows the A matrix to be defined only
        in terms of the relevant variables without the need to manually
        create a lot of zero columns. If VARSETS is empty, x is taken
        to be the full vector of all optimization variables. If L or
        U are empty, they are assumed to be appropriately sized vectors
        of -Inf and Inf, respectively.

        For non-linear constraints, the 3rd argument, N, is the number
        of constraints in the set. Currently, this is used internally
        by PYPOWER, but there is no way for the user to specify
        additional non-linear constraints.
        """
        if u is None:
        ## non-linear
            ## prevent duplicate named constraint sets
            if name in self.nln["idx"]["N"]:
                logger.error("opf_model.add_constraints: non-linear constraint set named '%s' already exists" % name)

            ## add info about this non-linear constraint set
            self.nln["idx"]["i1"][name] = self.nln["N"] + 1    ## starting index
            self.nln["idx"]["iN"][name] = self.nln["N"] + AorN ## ing index
            self.nln["idx"]["N"][name]  = AorN            ## number of constraints

            ## update number of non-linear constraints and constraint sets
            self.nln["N"]  = self.nln["idx"]["iN"][name]
            self.nln["NS"] = self.nln["NS"] + 1

            ## put name in ordered list of constraint sets
            self.nln["order"][self.nln["NS"]] = name
        else:                ## linear
            ## prevent duplicate named constraint sets
            if name in self.lin["idx"]["N"]:
                logger.error('opf_model.add_constraints: linear constraint set named ''%s'' already exists' % name)

            if varsets is None:
                varsets = []

            N, M = AorN.shape
            if len(l) == 0:                   ## default l is -Inf
                l = -Inf * ones(N)

            if len(u) == 0:                   ## default u is Inf
                u = Inf * ones(N)

            if len(varsets) == 0:
                varsets = self.var["order"]

            ## check sizes
            if l.shape[0] != N or u.shape[0] != N:
                logger.error('opf_model.add_constraints: sizes of A, l and u must match')

            nv = 0
            for k in range(len(varsets)):
                nv = nv + self.var["idx"]["N"][varsets[k]]

            if M != nv:
                logger.error('opf_model.add_constraints: number of columns of A does not match\nnumber of variables, A is %d x %d, nv = %d\n' % (N, M, nv))

            ## add info about this linear constraint set
            self.lin["idx"]["i1"][name]  = self["lin"]["N"] + 1   ## starting index
            self.lin["idx"]["iN"][name]  = self["lin"]["N"] + N   ## ing index
            self.lin["idx"]["N"][name]   = N              ## number of constraints
            self.lin["data"]["A"][name]  = AorN
            self.lin["data"]["l"][name]  = l
            self.lin["data"]["u"][name]  = u
            self.lin["data"]["vs"][name] = varsets

            ## update number of vars and var sets
            self.lin["N"]  = self.lin["idx"]["iN"][name]
            self.lin["NS"] = self.lin["NS"] + 1

            ## put name in ordered list of var sets
            self.lin["order"][self.lin["NS"]] = name


    def add_costs(self, name, cp, varsets):
        """Adds a set of user costs to the model.

        Adds a named block of user-defined costs to the model. Each set is
        defined by the CP struct described below. All user-defined sets of
        costs are combined together into a single set of cost parameters in
        a single CP struct by BULD_COST_PARAMS. This full aggregate set of
        cost parameters can be retreived from the model by GET_COST_PARAMS.

        Let x refer to the vector formed by combining the specified VARSETS,
        and f_u(x, CP) be the cost at x corresponding to the cost parameters
        contained in CP, where CP is a struct with the following fields:
            N      - nw x nx sparse matrix
            Cw     - nw x 1 vector
            H      - nw x nw sparse matrix (optional, all zeros by default)
            dd, mm - nw x 1 vectors (optional, all ones by default)
            rh, kk - nw x 1 vectors (optional, all zeros by default)

        These parameters are used as follows to compute f_u(x, CP)

            R  = N*x - rh

                    /  kk(i),  R(i) < -kk(i)
            K(i) = <   0,     -kk(i) <= R(i) <= kk(i)
                    \ -kk(i),  R(i) > kk(i)

            RR = R + K

            U(i) =  /  0, -kk(i) <= R(i) <= kk(i)
                    \  1, otherwise

            DDL(i) = /  1, dd(i) = 1
                     \  0, otherwise

            DDQ(i) = /  1, dd(i) = 2
                     \  0, otherwise

            Dl = diag(mm) * diag(U) * diag(DDL)
            Dq = diag(mm) * diag(U) * diag(DDQ)

            w = (Dl + Dq * diag(RR)) * RR

            f_u(x, CP) = 1/2 * w'*H*w + Cw'*w
        """
        ## prevent duplicate named cost sets
        if name in self.cost["idx"]["N"]:
            logger.error('opf_model.add_costs: cost set named ''%s'' already exists' % name)

        if varsets is None:
            varsets = []

        if len(varsets) == 0:
            varsets = self.var["order"]

        nw, nx = cp["N"].shape

        ## check sizes
        nv = 0
        for k in range(len(varsets)):
            nv = nv + self.var["idx"]["N"][varsets[k]]

        if nx != nv:
            if nw == 0:
                cp["N"] = sparse(nw, nx)
            else:
                logger.error('opf_model.add_costs: number of columns in N (%d x %d) does not match\nnumber of variables (%d)\n' % (nw, nx, nv))

        if cp["Cw"].shape[0] != nw:
            logger.error('opf_model.add_costs: number of rows of Cw (%d x %d) and N (%d x %d) must match\n' % (cp["Cw"].shape[0], nw, nx))

        if 'H' in cp & (cp["H"].shape[0] != nw | cp["H"].shape[1] != nw):
            logger.error('opf_model.add_costs: both dimensions of H (%d x %d) must match the number of rows in N (%d x %d)\n' % (cp["H"].shape, nw, nx))

        if 'dd' in cp & cp["dd"].shape[0] != nw:
            logger.error('opf_model.add_costs: number of rows of dd (%d x %d) and N (%d x %d) must match\n' % (cp["dd"].shape, nw, nx))

        if 'rh' in cp & cp["rh"].shape[0] != nw:
            logger.error('opf_model.add_costs: number of rows of rh (%d x %d) and N (%d x %d) must match\n' % (cp["rh"].shape, nw, nx))

        if 'kk' in cp & cp["kk"].shape[0] != nw:
            logger.error('opf_model.add_costs: number of rows of kk (%d x %d) and N (%d x %d) must match\n' % (cp["kk"].shape, nw, nx))

        if 'mm' in cp & cp["mm"].shape[0] != nw:
            logger.error('opf_model.add_costs: number of rows of mm (%d x %d) and N (%d x %d) must match\n' % (cp["mm"].shape, nw, nx))

        ## add info about this user cost set
        self.cost["idx"]["i1"][name]  = self.cost["N"] + 1     ## starting index
        self.cost["idx"]["iN"][name]  = self.cost["N"] + nw    ## ing index
        self.cost["idx"]["N"][name]   = nw                ## number of costs (nw)
        self.cost["data"]["N"][name]  = cp["N"]
        self.cost["data"]["Cw"][name] = cp["Cw"]
        self.cost["data"]["vs"][name] = varsets
        if 'H' in cp:
            self.cost["data"]["H"][name]  = cp["H"]

        if 'dd' in cp:
            self.cost["data"]["dd"]["name"] = cp["dd"]

        if 'rh' in cp:
            self.cost["data"]["rh"]["name"] = cp["rh"]

        if 'kk' in cp:
            self.cost["data"]["kk"]["name"] = cp["kk"]

        if 'mm' in cp:
            self.cost["data"]["mm"]["name"] = cp["mm"]

        ## update number of vars and var sets
        self.cost["N"]  = self.cost["idx"]["iN"]["name"]
        self.cost["NS"] = self.cost["NS"] + 1

        ## put name in ordered list of var sets
        self.cost["order"][self.cost["NS"]] = name
