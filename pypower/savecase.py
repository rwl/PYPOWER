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

import logging

from numpy import array, c_, r_
from scipy.io import savemat

from run_userfcn import run_userfcn

from idx_bus import *
from idx_gen import *
from idx_brch import *
from idx_area import *
from idx_cost import *

logger = logging.getLogger(__name__)

def savecase(fname, comment, ppc, version=2):
    """ Saves a PYPOWER case file, given a filename and the data.

    Writes a PYPOWER case file, given a filename and data struct or list of
    data matrices. The FNAME parameter is the name of the file to be created or
    overwritten. Returns the filename,
    with extension added if necessary. The optional COMMENT argument is
    either string (single line comment) or a cell array of strings which
    are inserted as comments. When using a PYPOWER case dict, if the
    optional VERSION argument is '1' it will modify the data matrices to
    version 1 format before saving.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ppc_ver = ppc["version"] = version
    baseMVA, bus, gen, branch = ppc["baseMVA"], ppc["bus"], ppc["gen"], ppc["branch"]
    areas = ppc["areas"] if "areas" in ppc else None
    gencost = ppc["gencost"] if "gencost" in ppc else None

    ## modifications for version 1 format
    if ppc_ver == "1":
        ## remove extra columns of gen
        if gen.shape[1] >= MU_QMIN:
            gen = c_[gen[:, :PMIN], gen[:, MU_PMAX:MU_QMIN]]
        else:
            gen = gen[:, :PMIN]
        ## use the version 1 values for column names
        shift = MU_PMAX - PMIN - 1
        tmp = array([MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN]) - shift
        MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN = tmp

        ## remove extra columns of branch
        if branch.shape[1] >= MU_ST:
            branch = c_[branch[:, :BR_STATUS], branch[:, PF:MU_ST]]
        elif branch.shape[1] >= QT:
            branch = c_[branch[:, :BR_STATUS], branch[:, PF:QT]]
        else:
            branch = branch[:, :BR_STATUS]
        ## use the version 1 values for column names
        shift = PF - BR_STATUS - 1
        tmp = array([PF, QF, PT, QT, MU_SF, MU_ST]) - shift
        PF, QF, PT, QT, MU_SF, MU_ST = tmp

    ## verify valid filename
    l = len(fname)
    rootname = ""
    if l > 2:
        if fname[-2:] == ".m":
            rootname = fname[:-2]
            extension = ".m"
        elif l > 4:
            if fname[-4:] == ".mat":
                rootname = fname[:-4]
                extension = ".mat"

    if not rootname:
        rootname = fname
        extension = ".m"
        fname = rootname + extension

    ## open and write the file
    if extension == ".mat":     ## MAT-file
        savemat(fname, ppc)
    else:                       ## M-file
        try:
            fd = open(fname, "wb")
        except Exception, detail:
            logger.error("savecase: %s." % detail)
            return fname

        ## function header, etc.
        if ppc_ver == "1":
            if areas != None and gencost != None and len(gencost) > 0:
                fd.write('function [baseMVA, bus, gen, branch, areas, gencost] = %s\n' % rootname)
            else:
                fd.write('function [baseMVA, bus, gen, branch] = %s\n' % rootname)
            prefix = ''
        else:
            fd.write('function mpc = %s\n' % rootname)
            prefix = 'mpc.'
        if comment:
            if isinstance(comment, basestring):
                fd.write('%%%s\n' % comment)
            elif isinstance(comment, list):
                for c in comment:
                    fd.write('%%%s\n' % c)
        fd.write('\n%%%% MATPOWER Case Format : Version %s\n' % ppc_ver)
        if ppc_ver != "1":
            fd.write('mpc.version = ''%s'';\n' % ppc_ver)
        fd.write('\n%%%%-----  Power Flow Data  -----%%%%\n')
        fd.write('%%%% system MVA base\n')
        fd.write('%sbaseMVA = %g;\n' % (prefix, baseMVA))

        ## bus data
        ncols = bus.shape[1]
        fd.write('\n%%%% bus data\n')
        fd.write('%%\tbus_i\ttype\tPd\tQd\tGs\tBs\tarea\tVm\tVa\tbaseKV\tzone\tVmax\tVmin')
        if ncols >= MU_VMIN:             ## opf SOLVED, save with lambda's & mu's
            fd.write('\tlam_P\tlam_Q\tmu_Vmax\tmu_Vmin')
        fd.write('\n%sbus = [\n' % prefix)
        if ncols < MU_VMIN:              ## opf NOT SOLVED, save without lambda's & mu's
            for i in range(bus.shape[0]):
                fd.write('\t%d\t%d\t%g\t%g\t%g\t%g\t%d\t%.8g\t%.8g\t%g\t%d\t%g\t%g;\n' % tuple(bus[i, :VMIN]))
        else:                            ## opf SOLVED, save with lambda's & mu's
            for i in range(bus.shape[0]):
                fd.write('\t%d\t%d\t%g\t%g\t%g\t%g\t%d\t%.8g\t%.8g\t%g\t%d\t%g\t%g\t%.4f\t%.4f\t%.4f\t%.4f;\n' % tuple(bus[:, :MU_VMIN]))
        fd.write('];\n')

        ## generator data
        ncols = gen.shape[1]
        fd.write('\n%%%% generator data\n')
        fd.write('%%\tbus\tPg\tQg\tQmax\tQmin\tVg\tmBase\tstatus\tPmax\tPmin')
        if ppc_ver != "1":
            fd.write('\tPc1\tPc2\tQc1min\tQc1max\tQc2min\tQc2max\tramp_agc\tramp_10\tramp_30\tramp_q\tapf')
        if ncols >= MU_QMIN:             # opf SOLVED, save with mu's
            fd.write('\tmu_Pmax\tmu_Pmin\tmu_Qmax\tmu_Qmin')
        fd.write('\n%sgen = [\n' % prefix)
        if ncols < MU_QMIN:              ## opf NOT SOLVED, save without mu's
            if ppc_ver == "1":
                for i in range(gen.shape[0]):
                    fd.write('\t%d\t%g\t%g\t%g\t%g\t%.8g\t%g\t%d\t%g\t%g;\n' % tuple(gen[i, :PMIN]))
            else:
                for i in range(gen.shape[0]):
                    fd.write('\t%d\t%g\t%g\t%g\t%g\t%.8g\t%g\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g;\n' % tuple(gen[i, :APF]))
        else:
            if ppc_ver == "1":
                for i in range(gen.shape[0]):
                    fd.write('\t%d\t%g\t%g\t%g\t%g\t%.8g\t%g\t%d\t%g\t%g\t%.4f\t%.4f\t%.4f\t%.4f;\n' % tuple(gen[i, :MU_QMIN]))
            else:
                for i in range(gen.shape[0]):
                    fd.write('\t%d\t%g\t%g\t%g\t%g\t%.8g\t%g\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%.4f\t%.4f\t%.4f\t%.4f;\n' % tuple(gen[i, :MU_QMIN]))
        fd.write('];\n')

        ## branch data
        ncols = branch.shape[1]
        fd.write('\n%%%% branch data\n')
        fd.write('%%\tfbus\ttbus\tr\tx\tb\trateA\trateB\trateC\tratio\tangle\tstatus')
        if ppc_ver != "1":
            fd.write('\tangmin\tangmax')
        if ncols >= QT:                  ## power flow SOLVED, save with line flows
            fd.write('\tPf\tQf\tPt\tQt')
        if ncols >= MU_ST:               ## opf SOLVED, save with mu's
            fd.write('\tmu_Sf\tmu_St')
            if ppc_ver != "1":
                fd.write('\tmu_angmin\tmu_angmax')
        fd.write('\n%sbranch = [\n' % prefix)
        if ncols < QT:                   ## power flow NOT SOLVED, save without line flows or mu's
            if ppc_ver == "1":
                for i in range(branch.shape[0]):
                    fd.write('\t%d\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%d;\n' % tuple(branch[i, :BR_STATUS]))
            else:
                for i in range(branch.shape[0]):
                    fd.write('\t%d\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%d\t%g\t%g;\n' % tuple(branch[i, :ANGMAX]))
        elif ncols < MU_ST:            ## power flow SOLVED, save with line flows but without mu's
            if ppc_ver == "1":
                for i in range(branch.shape[0]):
                    fd.write('\t%d\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%d\t%.4f\t%.4f\t%.4f\t%.4f;\n' % tuple(branch[i, :QT]))
            else:
                for i in range(branch.shape[0]):
                    fd.write('\t%d\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%d\t%g\t%g\t%.4f\t%.4f\t%.4f\t%.4f;\n' % tuple(branch[i, :QT]))
        else:                            ## opf SOLVED, save with lineflows & mu's
            if ppc_ver == "1":
                for i in range(branch.shape[0]):
                    fd.write('\t%d\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f;\n' % tuple(branch[i, :MU_ST]))
            else:
                for i in range(branch.shape[0]):
                    fd.write('\t%d\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%d\t%g\t%g\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f;\n' % tuple(branch[i, :MU_ANGMAX]))
        fd.write('];\n')

        ## OPF data
        if areas != None and len(areas) > 0 or gencost != None and len(gencost) > 0:
            fd.write('\n%%%%-----  OPF Data  -----%%%%')
        if areas != None and len(areas) > 0:
            ## area data
            fd.write('\n%%%% area data\n')
            fd.write('%%\tarea\trefbus\n')
            fd.write('%sareas = [\n' % prefix)
            if len(areas) > 0:
                for i in range(areas.shape[0]):
                    fd.write('\t%d\t%d;\n' % tuple(areas[i, :PRICE_REF_BUS]))
            fd.write('];\n')
        if gencost != None and len(gencost) > 0:
            ## generator cost data
            fd.write('\n%%%% generator cost data\n')
            fd.write('%%\t1\tstartup\tshutdown\tn\tx1\ty1\t...\txn\tyn\n')
            fd.write('%%\t2\tstartup\tshutdown\tn\tc(n-1)\t...\tc0\n')
            fd.write('%sgencost = [\n' % prefix)
            if len(gencost > 0):
                n1 = 2 * max(gencost[gencost[:, MODEL] == PW_LINEAR,  NCOST]);
                n2 =     max(gencost[gencost[:, MODEL] == POLYNOMIAL, NCOST]);
                n = max(r_[n1, n2]);
                if gencost.shape[1] < n + 4:
                    logger.error('savecase: gencost data claims it has more columns than it does')
                template = '\t%d\t%g\t%g\t%d'
                for i in range(n):
                    template = template + '\t%g'
                template = template + ';\n'
                for i in range(gencost.shape[0]):
                    fd.write(template % tuple(gencost[i]))
            fd.write('];\n')

        ## generalized OPF user data
        if ppc["A"] != None and len(ppc["A"]) > 0 or ppc["N"] != None and len(ppc["N"]) > 0:
            fd.write('\n%%%%-----  Generalized OPF User Data  -----%%%%')

        ## user constraints
        if ppc["A"] != None and len(ppc["A"]) > 0:
            ## A
            fd.write('\n%%%% user constraints\n')
            print_sparse(fd, prefix + 'A', ppc["A"])
            if ppc["l"] != None and len(ppc["l"]) > 0 and ppc["u"] != None and len(ppc["u"]) > 0:
                fd.write('lu = [\n')
                for i in range(len(l)):
                    fd.write('\t%g\t%g;\n' % (ppc["l"][i], ppc["u"][i]))
                fd.write('];\n')
                fd.write('%sl = lu(:, 1);\n' % prefix)
                fd.write('%su = lu(:, 2);\n\n', prefix)
            elif ppc["l"] != None and len(ppc["l"]) > 0:
                fd.write('%sl = [\n' % prefix)
                for i in range(len(l)):
                    fd.write('\t%g;\n', ppc["l"][i])
                fd.write('];\n\n')
            elif ppc["u"] != None and len(ppc["u"]) > 0:
                fd.write('%su = [\n' % prefix)
                for i in range(len(l)):
                    fd.write('\t%g;\n', ppc["u"][i])
                fd.write('];\n\n')

        ## user costs
        if ppc["N"] != None and len(ppc["N"]) > 0:
            fd.write('\n%%%% user costs\n')
            print_sparse(fd, prefix + 'N', ppc["N"])
            if ppc["H"] != None and len(ppc["H"]) > 0:
                print_sparse(fd, prefix + 'H', ppc["H"])
            if ppc["fparm"] != None and len(ppc["fparm"]) > 0:
                fd.write('Cw_fparm = [\n')
                for i in range(ppc["Cw"]):
                    fd.write('\t%g\t%d\t%g\t%g\t%g;\n' % tuple(ppc["Cw"][i]) + tuple(ppc["fparm"][i, :]))
                fd.write('];\n')
                fd.write('%sCw    = Cw_fparm(:, 1);\n' % prefix)
                fd.write('%sfparm = Cw_fparm(:, 2:5);\n' % prefix)
            else:
                fd.write('%sCw = [\n', prefix)
                for i in range(len(ppc["Cw"])):
                    fd.write('\t%g;\n', ppc["Cw"][i])
                fd.write('];\n')

        ## user vars
        if ppc['z0'] != None or ppc['zl'] != None or ppc['zu'] != None:
            fd.write('\n%%%% user vars\n')
            if ppc['z0'] != None and len(ppc['z0']) > 0:
                fd.write('%sz0 = [\n' % prefix)
                for i in range(len(ppc['z0'])):
                    fd.write('\t%g;\n' % ppc["z0"])
                fd.write('];\n')
            if ppc['zl'] != None and len(ppc['zl']) > 0:
                fd.write('%szl = [\n' % prefix)
                for i in range(len(ppc['zl'])):
                    fd.write('\t%g;\n' % ppc["zl"])
                fd.write('];\n')
            if ppc['zu'] != None and len(ppc['zu']) > 0:
                fd.write('%szu = [\n' % prefix)
                for i in range(len(ppc['zu'])):
                    fd.write('\t%g;\n' % ppc["zu"])
                fd.write('];\n')

        ## execute userfcn callbacks for 'savecase' stage
        if 'userfcn' in ppc:
            run_userfcn(ppc["userfcn"], 'savecase', ppc, fd, prefix)

        ## close file
        fd.close()

    return fname


def print_sparse(fd, varname, A):
    A = A.tocoo()
    i, j, s = A.row, A.col, A.data
    m, n = A.shape

    if len(s) == 0:
        fd.write('%s = sparse(%d, %d);\n' % (varname, m, n))
    else:
        fd.write('ijs = [\n')
    for k in range(len(i)):
        fd.write('\t%d\t%d\t%g;\n' % (i[k], j[k], s[k]))

    fd.write('];\n')
    fd.write('%s = sparse(ijs(:, 1), ijs(:, 2), ijs(:, 3), %d, %d);\n' % (varname, m, n))
