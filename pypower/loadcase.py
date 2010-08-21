# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2009-2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

import logging

from os.path import basename, splitext, isfile

from matfile import read as read_matfile
from mfile import read as read_mfile

logger = logging.getLogger(__name__)

def loadcase(casefile, return_as_struct=False):
    """ Returns the individual data matrices or a struct containing them as
    fields.

    Here casefile is either a struct containing the fields baseMVA, bus,
    gen, branch, areas, gencost, or a string containing the name of the
    file. If casefile contains the extension '.mat' or '.m', then the
    explicit file is searched. If casefile containts no extension, then
    LOADCASE looks for a '.mat' file first, then for a '.m' file.  If the
    file does not exist or doesn't define all matrices, the routine aborts
    with an appropriate error message.  Alternatively, it can be called
    with the syntax:

    [baseMVA, bus, gen, branch, areas, gencost, info] = loadcase(casefile)
    [baseMVA, bus, gen, branch, info] = loadcase(casefile)
    [mpc, info] = loadcase(casefile)

    In this case, the function will not abort, but info will contain an
    exit code as follows:

        0:  all variables successfully defined
        1:  input argument is not a string or struct
        2:  specified extension-less file name does not exist in search
            path
        3:  specified .MAT file does not exist in search path
        4:  specified .M file does not exist in search path
        5:  specified file fails to define all matrices or contains syntax
            error

    If the input data is not a struct containing a 'version' field, it is
    assumed to be a MATPOWER case file in version 1 format, and will be
    converted to version 2 format.
    """
    info = 0

    # read data into dict
    if isinstance(casefile, basestring):
        base_name = basename(casefile)
        # check for explicit extension
        if base_name.endswith('.m', '.mat'):
            rootname, extension = splitext(base_name)
        else:
            rootname = base_name
            if isfile(base_name + '.mat'):
                extension = '.mat'
            elif isfile(base_name + '.m'):
                extension = '.m'
            else:
                info = 2

        if info == 0:
            if extension == '.mat': # from MAT file
                try:
                    s = read_matfile(rootname + extension)
                    if s.has_key('mpc'):
                        s = s['mpc']
                except:
                    info = 3

            elif extension == '.m': # from M file
                try: # assume it returns a dict
                    s = read_mfile

                except:
                    info = 4

            if info == 4 and isfile(rootname + '.m'):
                info = 5

    elif isinstance(casefile, dict):
        s = casefile
    else:
        info = 1

    # check contents of dict
    if info == 0:
        # check for required keys
        if not (s.has_key('baseMVA') and s.has_key('bus') \
            and s.has_key('gen') and s.has_key('branch')):
            info = 5
        elif not (s.has_key('areas') and s.has_key('gencost')):
            info = 5
        else:
            ppc = s

    if info == 0: # no errors
        baseMVA = ppc['baseMVA']
        bus = ppc['bus']
        gen = ppc['gen']
        branch = ppc['branch']
        if ppc.has_key('gencost'):
            areas = ppc['areas']
            gencost = ppc['gencost']
    else:
        if info == 1:
            logger.error('loadcase: input arg should be a dict or a string '
                'containing a filename')
        elif info == 2:
            logger.error('loadcase: specified case not a valid file')
        elif info == 3:
            logger.error('loadcase: specified MAT file does not exist')
        elif info == 4:
            logger.error('loadcase: specified M file does not exist')
        elif info == 5:
            logger.error('loadcase: syntax error or undefined data '
                'matrix(ices) in the file')
        else:
            logger.error('loadcase: unknown error')

    return baseMVA, bus, gen, branch, areas, gencost, info
