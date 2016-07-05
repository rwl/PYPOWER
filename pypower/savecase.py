# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Saves a PYPOWER case file.
"""

from sys import stderr

from os.path import basename

from numpy import array, c_, r_, any
from scipy.io import savemat

from pypower._compat import PY2
from pypower.run_userfcn import run_userfcn

from pypower.idx_bus import MU_VMIN, VMIN
from pypower.idx_gen import PMIN, MU_PMAX, MU_PMIN, MU_QMIN, MU_QMAX, APF
from pypower.idx_brch import \
    MU_ST, MU_SF, BR_STATUS, PF, PT, QT, QF, ANGMAX, MU_ANGMAX
from pypower.idx_area import PRICE_REF_BUS
from pypower.idx_cost import MODEL, NCOST, PW_LINEAR, POLYNOMIAL


if not PY2:
    basestring = str
    writemode = "w"
else:
    writemode = "wb"


def savecase(fname, ppc, comment=None, version='2'):
    """Saves a PYPOWER case file, given a filename and the data.

    Writes a PYPOWER case file, given a filename and data dict. The C{fname}
    parameter is the name of the file to be created or overwritten. Returns
    the filename, with extension added if necessary. The optional C{comment}
    argument is either string (single line comment) or a list of strings which
    are inserted as comments. When using a PYPOWER case dict, if the
    optional C{version} argument is '1' it will modify the data matrices to
    version 1 format before saving.

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    """
    ppc_ver = ppc["version"] = version
    baseMVA, bus, gen, branch = \
        ppc["baseMVA"], ppc["bus"], ppc["gen"], ppc["branch"]
    areas = ppc["areas"] if "areas" in ppc else None
    gencost = ppc["gencost"] if "gencost" in ppc else None

    ## modifications for version 1 format
    if ppc_ver == "1":
        raise NotImplementedError
#        ## remove extra columns of gen
#        if gen.shape[1] >= MU_QMIN:
#            gen = c_[gen[:, :PMIN], gen[:, MU_PMAX:MU_QMIN]]
#        else:
#            gen = gen[:, :PMIN]
#        ## use the version 1 values for column names
#        shift = MU_PMAX - PMIN - 1
#        tmp = array([MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN]) - shift
#        MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN = tmp
#
#        ## remove extra columns of branch
#        if branch.shape[1] >= MU_ST:
#            branch = c_[branch[:, :BR_STATUS], branch[:, PF:MU_ST]]
#        elif branch.shape[1] >= QT:
#            branch = c_[branch[:, :BR_STATUS], branch[:, PF:QT]]
#        else:
#            branch = branch[:, :BR_STATUS]
#        ## use the version 1 values for column names
#        shift = PF - BR_STATUS - 1
#        tmp = array([PF, QF, PT, QT, MU_SF, MU_ST]) - shift
#        PF, QF, PT, QT, MU_SF, MU_ST = tmp

    ## verify valid filename
    l = len(fname)
    rootname = ""
    if l > 2:
        if fname[-3:] == ".py":
            rootname = fname[:-3]
            extension = ".py"
        elif l > 4:
            if fname[-4:] == ".mat":
                rootname = fname[:-4]
                extension = ".mat"

    if not rootname:
        rootname = fname
        extension = ".py"
        fname = rootname + extension

    indent = '    '  # four spaces
    indent2 = indent + indent

    ## open and write the file
    if extension == ".mat":     ## MAT-file
        ppc_mat = {}
        ppc_mat['version'] = ppc_ver
        ppc_mat['baseMVA'] = baseMVA
        ppc_keys = ['bus', 'gen', 'branch']
        # Assign non-scalar values as NumPy arrays
        for key in ppc_keys:
            ppc_mat[key] = array(ppc[key])
        if 'areas' in ppc:
            ppc_mat['areas'] = array(ppc['areas'])
        if 'gencost' in ppc:
            ppc_mat['gencost'] = array(ppc['gencost'])
        if "A" in ppc and len(ppc["A"]) > 0:
            ppc_mat["A"] = array(ppc["A"])
            if "l" in ppc and len(ppc["l"]) > 0:
                ppc_mat["l"] = array(ppc["l"])
            if "u" in ppc and len(ppc["u"]) > 0:
                ppc_mat["u"] = array(ppc["u"])
        if "N" in ppc and len(ppc["N"]) > 0:
            ppc_mat["N"] = array(ppc["N"])
            if "H" in ppc and len(ppc["H"]) > 0:
                ppc_mat["H"] = array(ppc["H"])
            if "fparm" in ppc and len(ppc["fparm"]) > 0:
                ppc_mat["fparm"] = array(ppc["fparm"])
            ppc_mat["Cw"] = array(ppc["Cw"])
        if 'z0' in ppc or 'zl' in ppc or 'zu' in ppc:
            if 'z0' in ppc and len(ppc['z0']) > 0:
                ppc_mat['z0'] = array(ppc['z0'])
            if 'zl' in ppc and len(ppc['zl']) > 0:
                ppc_mat['zl'] = array(ppc['zl'])
            if 'zu' in ppc and len(ppc['zu']) > 0:
                ppc_mat['zu'] = array(ppc['zu'])
        if 'userfcn' in ppc and len(ppc['userfcn']) > 0:
            ppc_mat['userfcn'] = array(ppc['userfcn'])
        elif 'userfcn' in ppc:
            ppc_mat['userfcn'] = ppc['userfcn']
        for key in ['x', 'f']:
            if key in ppc:
                ppc_mat[key] = ppc[key]
        for key in ['lin', 'order', 'nln', 'var', 'raw', 'mu']:
            if key in ppc:
                ppc_mat[key] = array(ppc[key])

        savemat(fname, ppc_mat)
    else:                       ## Python file
        try:
            fd = open(fname, writemode)
        except Exception as detail:
            stderr.write("savecase: %s.\n" % detail)
            return fname

        ## function header, etc.
        if ppc_ver == "1":
            raise NotImplementedError
#            if (areas != None) and (gencost != None) and (len(gencost) > 0):
#                fd.write('function [baseMVA, bus, gen, branch, areas, gencost] = %s\n' % rootname)
#            else:
#                fd.write('function [baseMVA, bus, gen, branch] = %s\n' % rootname)
#            prefix = ''
        else:
            fd.write('def %s():\n' % basename(rootname))
            prefix = 'ppc'
        if comment:
            if isinstance(comment, basestring):
                fd.write('#%s\n' % comment)
            elif isinstance(comment, list):
                for c in comment:
                    fd.write('#%s\n' % c)
        fd.write('\n%s## PYPOWER Case Format : Version %s\n' % (indent, ppc_ver))
        if ppc_ver != "1":
            fd.write("%sppc = {'version': '%s'}\n" % (indent, ppc_ver))
        fd.write('\n%s##-----  Power Flow Data  -----##\n' % indent)
        fd.write('%s## system MVA base\n' % indent)
        fd.write("%s%s['baseMVA'] = %.9g\n" % (indent, prefix, baseMVA))

        ## bus data
        ncols = bus.shape[1]
        fd.write('\n%s## bus data\n' % indent)
        fd.write('%s# bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin' % indent)
        if ncols >= MU_VMIN + 1:             ## opf SOLVED, save with lambda's & mu's
            fd.write('lam_P lam_Q mu_Vmax mu_Vmin')
        fd.write("\n%s%s['bus'] = array([\n" % (indent, prefix))
        if ncols < MU_VMIN + 1:              ## opf NOT SOLVED, save without lambda's & mu's
            for i in range(bus.shape[0]):
                fd.write('%s[%d, %d, %.9g, %.9g, %.9g, %.9g, %d, %.9g, %.9g, %.9g, %d, %.9g, %.9g],\n' % ((indent2,) + tuple(bus[i, :VMIN + 1])))
        else:                            ## opf SOLVED, save with lambda's & mu's
            for i in range(bus.shape[0]):
                fd.write('%s[%d, %d, %.9g, %.9g, %.9g, %.9g, %d, %.9g, %.9g, %.9g, %d, %.9g, %.9g, %.4f, %.4f, %.4f, %.4f],\n' % ((indent2,) + tuple(bus[i, :MU_VMIN + 1])))
        fd.write('%s])\n' % indent)

        ## generator data
        ncols = gen.shape[1]
        fd.write('\n%s## generator data\n' % indent)
        fd.write('%s# bus Pg Qg Qmax Qmin Vg mBase status Pmax Pmin' % indent)
        if ppc_ver != "1":
            fd.write(' Pc1 Pc2 Qc1min Qc1max Qc2min Qc2max ramp_agc ramp_10 ramp_30 ramp_q apf')
        if ncols >= MU_QMIN + 1:             # opf SOLVED, save with mu's
            fd.write(' mu_Pmax mu_Pmin mu_Qmax mu_Qmin')
        fd.write("\n%s%s['gen'] = array([\n" % (indent, prefix))
        if ncols < MU_QMIN + 1:              ## opf NOT SOLVED, save without mu's
            if ppc_ver == "1":
                for i in range(gen.shape[0]):
                    fd.write('%s[%d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d, %.9g, %.9g],\n' % ((indent2,) + tuple(gen[i, :PMIN + 1])))
            else:
                for i in range(gen.shape[0]):
                    fd.write('%s[%d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g],\n' % ((indent2,) + tuple(gen[i, :APF + 1])))
        else:
            if ppc_ver == "1":
                for i in range(gen.shape[0]):
                    fd.write('%s[%d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d, %.9g, %.9g, %.4f, %.4f, %.4f, %.4f],\n' % ((indent2,) + tuple(gen[i, :MU_QMIN + 1])))
            else:
                for i in range(gen.shape[0]):
                    fd.write('%s[%d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.4f, %.4f, %.4f, %.4f],\n' % ((indent2,) + tuple(gen[i, :MU_QMIN + 1])))
        fd.write('%s])\n' % indent)

        ## branch data
        ncols = branch.shape[1]
        fd.write('\n%s## branch data\n' % indent)
        fd.write('%s# fbus tbus r x b rateA rateB rateC ratio angle status' % indent)
        if ppc_ver != "1":
            fd.write(' angmin angmax')
        if ncols >= QT + 1:                  ## power flow SOLVED, save with line flows
            fd.write(' Pf Qf Pt Qt')
        if ncols >= MU_ST + 1:               ## opf SOLVED, save with mu's
            fd.write(' mu_Sf mu_St')
            if ppc_ver != "1":
                fd.write(' mu_angmin mu_angmax')
        fd.write('\n%s%s[\'branch\'] = array([\n' % (indent, prefix))
        if ncols < QT + 1:                   ## power flow NOT SOLVED, save without line flows or mu's
            if ppc_ver == "1":
                for i in range(branch.shape[0]):
                    fd.write('%s[%d, %d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d],\n' % ((indent2,) + tuple(branch[i, :BR_STATUS + 1])))
            else:
                for i in range(branch.shape[0]):
                    fd.write('%s[%d, %d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d, %.9g, %.9g],\n' % ((indent2,) + tuple(branch[i, :ANGMAX + 1])))
        elif ncols < MU_ST + 1:            ## power flow SOLVED, save with line flows but without mu's
            if ppc_ver == "1":
                for i in range(branch.shape[0]):
                    fd.write('%s[%d, %d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d, %.4f, %.4f, %.4f, %.4f],\n' % ((indent2,) + tuple(branch[i, :QT + 1])))
            else:
                for i in range(branch.shape[0]):
                    fd.write('%s[%d, %d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d, %.9g, %.9g, %.4f, %.4f, %.4f, %.4f],\n' % ((indent2,) + tuple(branch[i, :QT + 1])))
        else:                            ## opf SOLVED, save with lineflows & mu's
            if ppc_ver == "1":
                for i in range(branch.shape[0]):
                    fd.write('%s[%d, %d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f],\n' % ((indent2,) + tuple(branch[i, :MU_ST + 1])))
            else:
                for i in range(branch.shape[0]):
                    fd.write('%s[%d, %d, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %.9g, %d, %.9g, %.9g, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f],\n' % ((indent2,) + tuple(branch[i, :MU_ANGMAX + 1])))
        fd.write('%s])\n' % indent)

        ## OPF data
        if (areas is not None) and (len(areas) > 0) or (gencost is not None) and (len(gencost) > 0):
            fd.write('\n%s##-----  OPF Data  -----##' % indent)
        if (areas is not None) and (len(areas) > 0):
            ## area data
            fd.write('\n%s## area data\n' % indent)
            fd.write('%s# area refbus\n' % indent)
            fd.write("%s%s['areas'] = array([\n" % (indent, prefix))
            if len(areas) > 0:
                for i in range(areas.shape[0]):
                    fd.write('%s[%d, %d],\n' % ((indent2,) + tuple(areas[i, :PRICE_REF_BUS + 1])))
            fd.write('%s])\n' % indent)
        if gencost is not None and len(gencost) > 0:
            ## generator cost data
            fd.write('\n%s## generator cost data\n' % indent)
            fd.write('%s# 1 startup shutdown n x1 y1 ... xn yn\n' % indent)
            fd.write('%s# 2 startup shutdown n c(n-1) ... c0\n' % indent)
            fd.write('%s%s[\'gencost\'] = array([\n' % (indent, prefix))
            if len(gencost > 0):
                if any(gencost[:, MODEL] == PW_LINEAR):
                    n1 = 2 * max(gencost[gencost[:, MODEL] == PW_LINEAR,  NCOST])
                else:
                    n1 = 0
                if any(gencost[:, MODEL] == POLYNOMIAL):
                    n2 =     max(gencost[gencost[:, MODEL] == POLYNOMIAL, NCOST])
                else:
                    n2 = 0
                n = int( max([n1, n2]) )
                if gencost.shape[1] < n + 4:
                    stderr.write('savecase: gencost data claims it has more columns than it does\n')
                template = '%s[%d, %.9g, %.9g, %d'
                for i in range(n):
                    template = template + ', %.9g'
                template = template + '],\n'
                for i in range(gencost.shape[0]):
                    fd.write(template % ((indent2,) + tuple(gencost[i])))
            fd.write('%s])\n' % indent)

        ## generalized OPF user data
        if ("A" in ppc) and (len(ppc["A"]) > 0) or ("N" in ppc) and (len(ppc["N"]) > 0):
            fd.write('\n%s##-----  Generalized OPF User Data  -----##' % indent)

        ## user constraints
        if ("A" in ppc) and (len(ppc["A"]) > 0):
            ## A
            fd.write('\n%s## user constraints\n' % indent)
            print_sparse(fd, prefix + "['A']", ppc["A"])
            if ("l" in ppc) and (len(ppc["l"]) > 0) and ("u" in ppc) and (len(ppc["u"]) > 0):
                fd.write('%slu = array([\n' % indent)
                for i in range(len(ppc["l"])):
                    fd.write('%s[%.9g, %.9g],\n' % (indent2, ppc["l"][i], ppc["u"][i]))
                fd.write('%s])\n' % indent)
                fd.write("%s%s['l'] = lu[:, 0]\n" % (indent, prefix))
                fd.write("%s%s['u'] = lu[:, 1]\n\n" % (indent, prefix))
            elif ("l" in ppc) and (len(ppc["l"]) > 0):
                fd.write("%s%s['l'] = array([\n" % (indent, prefix))
                for i in range(len(l)):
                    fd.write('%s[%.9g],\n' % (indent2, ppc["l"][i]))
                fd.write('%s])\n\n' % indent)
            elif ("u" in ppc) and (len(ppc["u"]) > 0):
                fd.write("%s%s['u'] = array([\n" % (indent, prefix))
                for i in range(len(l)):
                    fd.write('%s[%.9g],\n' % (indent2, ppc["u"][i]))
                fd.write('%s])\n\n' % indent)

        ## user costs
        if ("N" in ppc) and (len(ppc["N"]) > 0):
            fd.write('\n%s## user costs\n' % indent)
            print_sparse(fd, prefix + "['N']", ppc["N"])
            if ("H" in ppc) and (len(ppc["H"]) > 0):
                print_sparse(fd, prefix + "['H']", ppc["H"])
            if ("fparm" in ppc) and (len(ppc["fparm"]) > 0):
                fd.write("%sCw_fparm = array([\n" % indent)
                for i in range(ppc["Cw"]):
                    fd.write('%s[%.9g, %d, %.9g, %.9g, %.9g],\n' % ((indent2,) + tuple(ppc["Cw"][i]) + tuple(ppc["fparm"][i, :])))
                fd.write('%s])\n' % indent)
                fd.write('%s%s[\'Cw\']    = Cw_fparm[:, 0]\n' % (indent, prefix))
                fd.write("%s%s['fparm'] = Cw_fparm[:, 1:5]\n" % (indent, prefix))
            else:
                fd.write("%s%s['Cw'] = array([\n" % (indent, prefix))
                for i in range(len(ppc["Cw"])):
                    fd.write('%s[%.9g],\n' % (indent2, ppc["Cw"][i]))
                fd.write('%s])\n' % indent)

        ## user vars
        if ('z0' in ppc) or ('zl' in ppc) or ('zu' in ppc):
            fd.write('\n%s## user vars\n' % indent)
            if ('z0' in ppc) and (len(ppc['z0']) > 0):
                fd.write('%s%s["z0"] = array([\n' % (indent, prefix))
                for i in range(len(ppc['z0'])):
                    fd.write('%s[%.9g],\n' % (indent2, ppc["z0"]))
                fd.write('%s])\n' % indent)
            if ('zl' in ppc) and (len(ppc['zl']) > 0):
                fd.write('%s%s["zl"] = array([\n' % (indent2, prefix))
                for i in range(len(ppc['zl'])):
                    fd.write('%s[%.9g],\n' % (indent2, ppc["zl"]))
                fd.write('%s])\n' % indent)
            if ('zu' in ppc) and (len(ppc['zu']) > 0):
                fd.write('%s%s["zu"] = array([\n' % (indent, prefix))
                for i in range(len(ppc['zu'])):
                    fd.write('%s[%.9g],\n' % (indent2, ppc["zu"]))
                fd.write('%s])\n' % indent)

        ## execute userfcn callbacks for 'savecase' stage
        if 'userfcn' in ppc:
            run_userfcn(ppc["userfcn"], 'savecase', ppc, fd, prefix)

        fd.write('\n%sreturn ppc\n' % indent)

        ## close file
        fd.close()

    return fname


def print_sparse(fd, varname, A):
    A = A.tocoo()
    i, j, s = A.row, A.col, A.data
    m, n = A.shape

    if len(s) == 0:
        fd.write('%s = sparse((%d, %d))\n' % (varname, m, n))
    else:
        fd.write('ijs = array([\n')
    for k in range(len(i)):
        fd.write('[%d, %d, %.9g],\n' % (i[k], j[k], s[k]))

    fd.write('])\n')
    fd.write('%s = sparse(ijs[:, 0], ijs[:, 1], ijs[:, 2], %d, %d)\n' % (varname, m, n))
