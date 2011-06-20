# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

from sys import stderr

from numpy import array
from scipy.sparse import issparse

from ppoption import ppoption
from loadcase import loadcase


def opf_args(baseMVA, bus=None, gen=None, branch=None, areas=None,
             gencost=None, Au=None, lbu=None, ubu=None, ppopt=None, N=None,
             fparm=None, H=None, Cw=None, z0=None, zl=None, zu=None,
             want_ppc=True):
    """Parses and initializes OPF input arguments.

    Returns the full set of initialized OPF input arguments, filling in
    default values for missing arguments. See Examples below for the
    possible calling syntax options.

       Input arguments options:

        opf_args(ppc)
        opf_args(ppc, ppopt)
        opf_args(ppc, userfcn, ppopt)
        opf_args(ppc, A, l, u)
        opf_args(ppc, A, l, u, ppopt)
        opf_args(ppc, A, l, u, ppopt, N, fparm, H, Cw)
        opf_args(ppc, A, l, u, ppopt, N, fparm, H, Cw, z0, zl, zu)

        opf_args(baseMVA, bus, gen, branch, areas, gencost)
        opf_args(baseMVA, bus, gen, branch, areas, gencost, ppopt)
        opf_args(baseMVA, bus, gen, branch, areas, gencost, userfcn, ppopt)
        opf_args(baseMVA, bus, gen, branch, areas, gencost, A, l, u)
        opf_args(baseMVA, bus, gen, branch, areas, gencost, A, l, u, ppopt)
        opf_args(baseMVA, bus, gen, branch, areas, gencost, A, l, u, ...
                                    ppopt, N, fparm, H, Cw)
        opf_args(baseMVA, bus, gen, branch, areas, gencost, A, l, u, ...
                                    ppopt, N, fparm, H, Cw, z0, zl, zu)

    The data for the problem can be specified in one of three ways:
    (1) a string (ppc) containing the file name of a MATPOWER case
      which defines the data matrices baseMVA, bus, gen, branch, and
      gencost (areas is not used at all, it is only included for
      backward compatibility of the API).
    (2) a struct (ppc) containing the data matrices as fields.
    (3) the individual data matrices themselves.

    The optional user parameters for user constraints (A, l, u), user costs
    (N, fparm, H, Cw), user variable initializer (z0), and user variable
    limits (zl, zu) can also be specified as fields in a case struct,
    either passed in directly or defined in a case file referenced by name.

    When specified, A, l, u represent additional linear constraints on the
    optimization variables, l <= A*[x z] <= u. If the user specifies an A
    matrix that has more columns than the number of "x" (OPF) variables,
    then there are extra linearly constrained "z" variables. For an
    explanation of the formulation used and instructions for forming the
    A matrix, see the manual.

    A generalized cost on all variables can be applied if input arguments
    N, fparm, H and Cw are specified.  First, a linear transformation
    of the optimization variables is defined by means of r = N * [x z].
    Then, to each element of r a function is applied as encoded in the
    fparm matrix (see manual). If the resulting vector is named w,
    then H and Cw define a quadratic cost on w: (1/2)*w'*H*w + Cw * w .
    H and N should be sparse matrices and H should also be symmetric.

    The optional ppopt vector specifies MATPOWER options. See ppoption
    for details and default values.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    nargin = len([arg for arg in [baseMVA, bus, gen, branch, areas, gencost,
                                  Au, lbu, ubu, ppopt, N, fparm, H, Cw,
                                  z0, zl, zu] if arg is not None])

    userfcn = array([])
    ## passing filename or dict
    if isinstance(baseMVA, basestring) or isinstance(baseMVA, dict):
        # ----opf( baseMVA,     bus,   gen, branch, areas, gencost,    Au, lbu,  ubu, ppopt,  N, fparm, H, Cw, z0, zl, zu)
        # 12  opf(casefile,      Au,   lbu,    ubu, ppopt,       N, fparm,    H,  Cw,    z0, zl,    zu)
        # 9   opf(casefile,      Au,   lbu,    ubu, ppopt,       N, fparm,    H,  Cw)
        # 5   opf(casefile,      Au,   lbu,    ubu, ppopt)
        # 4   opf(casefile,      Au,   lbu,    ubu)
        # 3   opf(casefile, userfcn, ppopt)
        # 2   opf(casefile,   ppopt)
        # 1   opf(casefile)
        if nargin in [1, 2, 3, 4, 5, 9, 12]:
            casefile = baseMVA
            if nargin == 12:
                zu    = fparm
                zl    = N
                z0    = ppopt
                Cw    = ubu
                H     = lbu
                fparm = Au
                N     = gencost
                ppopt = areas
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 9:
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = ubu
                H     = lbu
                fparm = Au
                N     = gencost
                ppopt = areas
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 5:
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = None
                fparm = array([])
                N     = None
                ppopt = areas
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 4:
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = None
                fparm = array([])
                N     = None
                ppopt = ppoption()
                ubu   = branch
                lbu   = gen
                Au    = bus
            elif nargin == 3:
                userfcn = bus
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = None
                fparm = array([])
                N     = None
                ppopt = gen
                ubu   = array([])
                lbu   = array([])
                Au    = None
            elif nargin == 2:
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = None
                fparm = array([])
                N     = None
                ppopt = bus
                ubu   = array([])
                lbu   = array([])
                Au    = None
            elif nargin == 1:
                zu    = array([])
                zl    = array([])
                z0    = array([])
                Cw    = array([])
                H     = None
                fparm = array([])
                N     = None
                ppopt = ppoption()
                ubu   = array([])
                lbu   = array([])
                Au    = None
        else:
            stderr.write('opf_args: Incorrect input arg order, number or type\n')

        ppc = loadcase(casefile)
        baseMVA, bus, gen, branch, gencost = \
            ppc['baseMVA'], ppc['bus'], ppc['gen'], ppc['branch'], ppc['gencost']
        if 'areas' in ppc:
            areas = ppc['areas']
        else:
            areas = array([])
        if (Au is None or len(Au) == 0) and 'A' in ppc:
            Au, lbu, ubu = ppc["A"], ppc["l"], ppc["u"]
        if (N is None or len(N) == 0) and 'N' in ppc:  ## these two must go together
            N, Cw = ppc["N"], ppc["Cw"]
        if (H is None or len(H) == 0) and 'H' in ppc:  ## will default to zeros
            H = ppc["H"]
        if (fparm is None or len(fparm) == 0) and 'fparm' in ppc:  ## will default to [1 0 0 1]
            fparm = ppc["fparm"]
        if (z0 is None or len(z0) == 0) and 'z0' in ppc:
            z0 = ppc["z0"]
        if (zl is None or len(zl) == 0) and 'zl' in ppc:
            zl = ppc["zl"]
        if (zu is None or len(zu) == 0) and 'zu' in ppc:
            zu = ppc["zu"]
        if (userfcn is None or len(userfcn) == 0) and 'userfcn' in ppc:
            userfcn = ppc['userfcn']
    else: ## passing individual data matrices
        # ----opf(baseMVA, bus, gen, branch, areas, gencost,      Au, lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 17  opf(baseMVA, bus, gen, branch, areas, gencost,      Au, lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 14  opf(baseMVA, bus, gen, branch, areas, gencost,      Au, lbu, ubu, ppopt, N, fparm, H, Cw)
        # 10  opf(baseMVA, bus, gen, branch, areas, gencost,      Au, lbu, ubu, ppopt)
        # 9   opf(baseMVA, bus, gen, branch, areas, gencost,      Au, lbu, ubu)
        # 8   opf(baseMVA, bus, gen, branch, areas, gencost, userfcn, ppopt)
        # 7   opf(baseMVA, bus, gen, branch, areas, gencost, ppopt)
        # 6   opf(baseMVA, bus, gen, branch, areas, gencost)
        if nargin in [6, 7, 8, 9, 10, 14, 17]:
            if nargin == 14:
                zu = array([])
                zl = array([])
                z0 = array([])
            elif nargin == 10:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
            elif nargin == 9:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                ppopt = ppoption()
            elif nargin == 8:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                ubu = array([])
                lbu = array([])
                Au = None
            elif nargin == 7:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                ubu = array([])
                lbu = array([])
                Au = None
            elif nargin == 6:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                ppopt = ppoption()
                ubu = array([])
                lbu = array([])
                Au = None
        else:
            stderr.write('opf_args: Incorrect input arg order, number or type\n')

        if want_ppc:
            ppc = {  'baseMVA': baseMVA,
                     'bus': bus,
                     'gen': gen,
                     'branch': branch,
                     'gencost': gencost  }

    nw = N.shape[0] if N is not None else 0
    if nw:
        if Cw.shape[0] != nw:
            stderr.write('opf_args.m: dimension mismatch between N and Cw in '
                         'generalized cost parameters\n')
        if any(fparm) and fparm.shape[0] != nw:
            stderr.write('opf_args.m: dimension mismatch between N and fparm '
                         'in generalized cost parameters\n')
        if any(H) and (H.shape[0] != nw | H.shape[0] != nw):
            stderr.write('opf_args.m: dimension mismatch between N and H in '
                         'generalized cost parameters\n')
        if Au.shape[0] > 0 and N.shape[1] != Au.shape[1]:
            stderr.write('opf_args.m: A and N must have the same number of '
                         'columns\n')
        ## make sure N and H are sparse
        if not issparse(N):
            stderr.write('opf_args.m: N must be sparse in generalized cost '
                         'parameters\n')
        if not issparse(H):
            stderr.write('opf_args.m: H must be sparse in generalized cost parameters\n')

    if Au is not None and not issparse(Au):
        stderr.write('opf_args.m: Au must be sparse\n')
    if ppopt == None or len(ppopt) == 0:
        ppopt = ppoption()
    if want_ppc:
        if areas is not None and len(areas) > 0:
            ppc["areas"] = areas
        if lbu is not None and len(lbu) > 0:
            ppc["A"], ppc["l"], ppc["u"] = Au, lbu, ubu
        if Cw is not None and len(Cw) > 0:
            ppc["N"], ppc["Cw"] = N, Cw
            if len(fparm) > 0:
                ppc["fparm"] = fparm
            #if len(H) > 0:
            ppc["H"] = H
        if z0 is not None and len(z0) > 0:
            ppc["z0"] = z0
        if zl is not None and len(zl) > 0:
            ppc["zl"] = zl
        if zu is not None and len(zu) > 0:
            ppc["zu"] = zu
        if userfcn is not None and len(userfcn) > 0:
            ppc["userfcn"] = userfcn

        return ppc, ppopt
    else:
        return baseMVA, bus, gen, branch, gencost, Au, lbu, ubu, \
            ppopt, N, fparm, H, Cw, z0, zl, zu, userfcn, areas
