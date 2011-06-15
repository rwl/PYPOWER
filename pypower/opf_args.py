# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

from sys import stderr

from numpy import array
from scipy.sparse import spmatrix

from ppoption import ppoption
from loadcase import loadcase


def opf_args(*args):
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
    nargin = len(args)

    want_ppc = 1
    userfcn = array([])
    ## passing filename or struct
    baseMVA = args[0]
    if isinstance(baseMVA, str) or isinstance(baseMVA, dict):
        # - - - -opf(baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 12  opf(casefile, Au, lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 9   opf(casefile, Au, lbu, ubu, ppopt, N, fparm, H, Cw)
        # 5   opf(casefile, Au, lbu, ubu, ppopt)
        # 4   opf(casefile, Au, lbu, ubu)
        # 3   opf(casefile, userfcn, ppopt)
        # 2   opf(casefile, ppopt)
        # 1   opf(casefile)
        if nargin in [1, 2, 3, 4, 5, 9, 12]:
            if nargin == 12:
                casefile, Au, lbu, ubu, ppopt, \
                    N, fparm, H, Cw, z0, zl, zu = args
            elif nargin == 9:
                zu = array([])
                zl = array([])
                z0 = array([])
                casefile, Au, lbu, ubu, ppopt, N, fparm, H, Cw = args
            elif nargin == 5:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                casefile, Au, lbu, ubu, ppopt = args
            elif nargin == 4:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                ppopt = ppoption
                casefile, Au, lbu, ubu = args
            elif nargin == 3:
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
                casefile, userfcn, ppopt = args
            elif nargin == 2:
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
                casefile, ppopt = args
            elif nargin == 1:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                ppopt = ppoption
                ubu = array([])
                lbu = array([])
                Au = None
                casefile = args
        else:
            stderr.write('opf_args: Incorrect input arg order, number or type\n')

        ppc = loadcase(casefile)
        baseMVA, bus, gen, branch, gencost = \
            ppc.baseMVA, ppc.bus, ppc.gen, ppc.branch, ppc.gencost
        if ppc.has_key('areas'):
            areas = ppc.areas
        else:
            areas = array([])
        if not any(Au) & ppc.has_key('A'):
            Au, lbu, ubu = ppc["A"], ppc["l"], ppc["u"]
        if not any(N) & ppc.has_key('N'): ## these two must go together
            N, Cw = ppc["N"], ppc["Cw"]
        if not any(H) & ppc.has_key('H'): ## will default to zeros
            H = ppc["H"]
        if not any(fparm) & ppc.has_key('fparm'): ## will default to [1 0 0 1]
            fparm = ppc["fparm"]
        if not any(z0) & ppc.has_key('z0'):
            z0 = ppc["z0"]
        if not any(zl) & ppc.has_key('zl'):
            zl = ppc["zl"]
        if not any(zu) & ppc.has_key('zu'):
            zu = ppc["zu"]
        if not any(userfcn) & ppc.has_key('userfcn'):
            userfcn = ppc.userfcn
    else: ## passing individual data matrices
        # - - - -opf(baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 17  opf(baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu)
        # 14  opf(baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt, N, fparm, H, Cw)
        # 10  opf(baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu, ppopt)
        # 9   opf(baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu)
        # 8   opf(baseMVA, bus, gen, branch, areas, gencost, userfcn, ppopt)
        # 7   opf(baseMVA, bus, gen, branch, areas, gencost, ppopt)
        # 6   opf(baseMVA, bus, gen, branch, areas, gencost)
        if nargin in [6, 7, 8, 9, 10, 14, 17]:
            if nargin == 17:
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu,
                ppopt, N, fparm, H, Cw, z0, zl, zu = args
            elif nargin == 14:
                zu = array([])
                zl = array([])
                z0 = array([])
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu,
                ppopt, N, fparm, H, Cw = args
            elif nargin == 10:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu,
                ppopt = args
            elif nargin == 9:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                ppopt = ppoption
                baseMVA, bus, gen, branch, areas, gencost, Au, lbu, ubu = args
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
                baseMVA, bus, gen, branch, areas, gencost, userfcn, ppopt =args
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
                baseMVA, bus, gen, branch, areas, gencost, ppopt = args
            elif nargin == 6:
                zu = array([])
                zl = array([])
                z0 = array([])
                Cw = array([])
                H = None
                fparm = array([])
                N = None
                ppopt = ppoption
                ubu = array([])
                lbu = array([])
                Au = None
                baseMVA, bus, gen, branch, areas, gencost = args
        else:
            stderr.write('opf_args: Incorrect input arg order, number or type\n')

        if want_ppc:
            ppc = {  'baseMVA': baseMVA,
                     'bus': bus,
                     'gen': gen,
                     'branch': branch,
                     'gencost': gencost  }
    nw = N.shape[0]
    if nw:
        if Cw.shape[0] != nw:
            stderr.write('opf_args.m: dimension mismatch between N and Cw in '
                         'generalized cost parameters\n')
        if any(fparm) & fparm.shape[0] != nw:
            stderr.write('opf_args.m: dimension mismatch between N and fparm '
                         'in generalized cost parameters\n')
        if any(H) & (H.shape[0] != nw | H.shape[0] != nw):
            stderr.write('opf_args.m: dimension mismatch between N and H in '
                         'generalized cost parameters\n')
        if Au.shape[0] > 0 & N.shape[1] != Au.shape[1]:
            stderr.write('opf_args.m: A and N must have the same number of '
                         'columns\n')
        ## make sure N and H are sparse
        if not isinstance(N, spmatrix):
            stderr.write('opf_args.m: N must be sparse in generalized cost '
                         'parameters\n')
        if not isinstance(H, spmatrix):
            stderr.write('opf_args.m: H must be sparse in generalized cost parameters\n')

    if not isinstance(Au, spmatrix):
        stderr.write('opf_args.m: Au must be sparse\n')
    if len(ppopt) == 0:
        ppopt = ppoption
    if want_ppc:
        if any(areas):
            ppc["areas"] = areas
        if any(Au):
            ppc["A"], ppc["l"], ppc["u"] = Au, lbu, ubu
        if any(N):
            ppc["N"], ppc["Cw"] = N, Cw
            if any(fparm):
                ppc["fparm"] = fparm
            if any(H):
                ppc["H"] = H
        if any(z0):
            ppc["z0"] = z0
        if any(zl):
            ppc["zl"] = zl
        if any(zu):
            ppc["zu"] = zu
        if any(userfcn):
            ppc["userfcn"] = userfcn
        baseMVA = ppc
        bus = ppopt

        return ppc, Au, lbu, ubu, ppopt, N, fparm, H, Cw, z0, zl, zu
    else:
        return baseMVA, bus, gen, branch, gencost, Au, lbu, ubu, \
            ppopt, N, fparm, H, Cw, z0, zl, zu, userfcn, areas
