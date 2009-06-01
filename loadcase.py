# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

""" Loads a MATPOWER case file and returns a dictionary containing data
    matrices.

    Ported from:
        D. Zimmerman, "loadcase.m", MATPOWER, version 3.2,
        Power System Engineering Research Center (PSERC), 2007

    See http://www.pserc.cornell.edu/matpower/ for more info.
"""

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
