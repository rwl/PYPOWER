# Copyright (C) 1996-2011 Power System Engineering Research Center
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

"""Loads a PYPOWER case dictionary.
"""

from os.path import basename, splitext, exists

from copy import deepcopy

from numpy import array, zeros, ones, c_

from scipy.io import loadmat

from pypower.idx_gen import PMIN, MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN
from pypower.idx_brch import PF, QF, PT, QT, MU_SF, MU_ST, BR_STATUS


def loadcase(casefile,
        return_as_dict=False, expect_opf_data=True):
    """Returns the individual data matrices or an dict containing them
    as values.

    Here C{casefile} is either a dict containing the keys C{baseMVA}, C{bus},
    C{gen}, C{branch}, C{areas}, C{gencost}, or a string containing the name
    of the file. If C{casefile} contains the extension '.mat' or '.py', then
    the explicit file is searched. If C{casefile} containts no extension, then
    L{loadcase} looks for a '.mat' file first, then for a '.py' file.  If the
    file does not exist or doesn't define all matrices, the function returns
    an exit code as follows:

        0.  all variables successfully defined
        1.  input argument is not a string or dict
        2.  specified extension-less file name does not exist
        3.  specified .mat file does not exist
        4.  specified .py file does not exist
        5.  specified file fails to define all matrices or contains syntax
            error

    If the input data is not a dict containing a 'version' key, it is
    assumed to be a PYPOWER case file in version 1 format, and will be
    converted to version 2 format.

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    if return_as_dict == True:
        expect_opf_data = False

    info = 0

    # read data into case object
    if isinstance(casefile, basestring):
        # check for explicit extension
        if casefile.endswith(('.py', '.mat')):
            rootname, extension = splitext(casefile)
            fname = basename(rootname)
        else:
            # set extension if not specified explicitly
            rootname = casefile
            if exists(casefile + '.mat'):
                extension = '.mat'
            elif exists(casefile + '.py'):
                extension = '.py'
            else:
                info = 2
            fname = basename(rootname)

        lasterr = ''

        ## attempt to read file
        if info == 0:
            if extension == '.mat':       ## from MAT file
                try:
                    d = loadmat(rootname + extension, struct_as_record=True)
                    if 'ppc' in d or 'mpc' in d:    ## it's a MAT/PYPOWER dict
                        if 'ppc' in d:
                            struct = d['ppc']
                        else:
                            struct = d['mpc']
                        val = struct[0, 0]

                        s = {}
                        for a in val.dtype.names:
                            s[a] = val[a]
                    else:                 ## individual data matrices
                        d['version'] = '1'

                        s = {}
                        for k, v in d.iteritems():
                            s[k] = v

                    s['baseMVA'] = s['baseMVA'][0, 0]  # convert array to float

                except IOError, e:
                    info = 3
                    lasterr = str(e)
            elif extension == '.py':      ## from Python file
                try:
                    execfile(rootname + extension)

                    try:                      ## assume it returns a dict
                        s = eval(fname)()
                    except ValueError, e:
                        info = 4
                        lasterr = str(e)
                    ## if not try individual data matrices
                    if info == 0 and not isinstance(s, dict):
                        s = {}
                        s['version'] = '1'
                        if expect_opf_data:
                            try:
                                s['baseMVA'], s['bus'], s['gen'], s['branch'], \
                                s['areas'], s['gencost'] = eval(fname)()
                            except IOError, e:
                                info = 4
                                lasterr = str(e)
                        else:
                            if return_as_dict:
                                try:
                                    s['baseMVA'], s['bus'], s['gen'], \
                                        s['branch'], s['areas'], \
                                        s['gencost'] = eval(fname)()
                                except ValueError, e:
                                    try:
                                        s['baseMVA'], s['bus'], s['gen'], \
                                            s['branch'] = eval(fname)()
                                    except ValueError, e:
                                        info = 4
                                        lasterr = str(e)
                            else:
                                try:
                                    s['baseMVA'], s['bus'], s['gen'], \
                                        s['branch'] = eval(fname)()
                                except ValueError, e:
                                    info = 4
                                    lasterr = str(e)

                except IOError, e:
                    info = 4
                    lasterr = str(e)


                if info == 4 and exists(rootname + '.py'):
                    info = 5
                    err5 = lasterr

    elif isinstance(casefile, dict):
        s = deepcopy(casefile)
    else:
        info = 1

    # check contents of dict
    if info == 0:
        # check for required keys
        if ('baseMVA' not in s or 'bus' not in s \
            or 'gen' not in s or 'branch' not in s) or \
            (expect_opf_data and ('gencost' not in s or \
            'areas' not in s)):
            info = 5  ## missing some expected fields
            err5 = 'missing data'
        else:
            ## all fields present, copy to ppc
            ppc = deepcopy(s)
            if not hasattr(ppc, 'version'):  ## hmm, struct with no 'version' field
                if ppc['gen'].shape[1] < 21:    ## version 2 has 21 or 25 cols
                    ppc['version'] = '1'
                else:
                    ppc['version'] = '2'

            if (ppc['version'] == '1'):
                # convert from version 1 to version 2
                ppc['gen'], ppc['branch'] = ppc_1to2(ppc['gen'], ppc['branch']);
                ppc['version'] = '2'

    if info == 0:  # no errors
        if return_as_dict:
            return ppc
        else:
            result = [ppc['baseMVA'], ppc['bus'], ppc['gen'], ppc['branch']]
            if 'gencost' in ppc:
                    result.extend([ppc['areas'], ppc['gencost']])
            return result
    else:  # error encountered
        if info == 1:
            raise ValueError, 'Input arg should be a case or a string ' + \
                              'containing a filename'
        elif info == 2:
            raise ValueError, 'Specified case not a valid file'
        elif info == 3:
            raise ValueError, 'Specified MAT file does not exist'
        elif info == 4:
            raise ValueError, 'Specified Python file does not exist'
        elif info == 5:
            raise ValueError, 'Syntax error or undefined data ' + \
                              'matrix(ices) in the file'
        else:
            raise ValueError, 'Unknown error encountered loading case.'

        raise ValueError, lasterr

        return info


def ppc_1to2(gen, branch):
    ##-----  gen  -----
    ## use the version 1 values for column names
    shift = MU_PMAX - PMIN - 1
    tmp = array([MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN]) - shift
    mu_Pmax, mu_Pmin, mu_Qmax, mu_Qmin = tmp

    ## add extra columns to gen
    tmp = zeros((gen.shape[0], shift))
    if gen.shape[1] >= mu_Qmin:
        gen = c_[ gen[:, 0:PMIN + 1], tmp, gen[:, mu_Pmax:mu_Qmin] ]
    else:
        gen = c_[ gen[:, 0:PMIN + 1], tmp ]

    ##-----  branch  -----
    ## use the version 1 values for column names
    shift = PF - BR_STATUS - 1
    tmp = array([PF, QF, PT, QT, MU_SF, MU_ST]) - shift
    Pf, Qf, Pt, Qt, mu_Sf, mu_St = tmp

    ## add extra columns to branch
    tmp = ones((branch.shape[0], 1)) * array([-360, 360])
    tmp2 = zeros((branch.shape[0], 2))
    if branch.shape[1] >= mu_St - 1:
        branch = c_[ branch[:, 0:BR_STATUS + 1], tmp, branch[:, PF - 1:MU_ST + 1], tmp2 ]
    elif branch.shape[1] >= QT - 1:
        branch = c_[ branch[:, 0:BR_STATUS + 1], tmp, branch[:, PF - 1:QT + 1] ]
    else:
        branch = c_[ branch[:, 0:BR_STATUS + 1], tmp ]

    return gen, branch
