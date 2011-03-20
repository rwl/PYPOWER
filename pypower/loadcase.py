# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
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

from os.path import basename, splitext, isfile

from numpy import array

logger = logging.getLogger(__name__)

def loadcase(casefile):
    """ Returns a dict containing case data matrices as values.

    Here casefile is either a dict containing the keys baseMVA, bus,
    gen, branch, areas, gencost, or a string containing the name of the
    file. If casefile contains the extension '.pkl' or '.py', then the
    explicit file is searched. If casefile containts no extension, then
    C{loadcase} looks for a '.pkl' file first, then for a '.py' file.  If the
    file does not exist or doesn't define all matrices, the function returns
    an exit code as follows:

        0:  all variables successfully defined
        1:  input argument is not a string or struct
        2:  specified extension-less file name does not exist in search
            path
        3:  specified .pkl file does not exist in search path
        4:  specified .py file does not exist in search path
        5:  specified file fails to define all matrices or contains syntax
            error

    If the input data is not a dict containing a 'version' key, it is
    assumed to be a PYPOWER case file in version 1 format, and will be
    converted to version 2 format.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    info = 0

    # read data into dict
    if isinstance(casefile, basestring):
#        base_name = casefile#basename(casefile)
        # check for explicit extension
        if casefile.endswith(('.py', '.pkl')):
            rootname, extension = splitext(casefile)
        else:
            rootname = casefile
            if isfile(casefile + '.pkl'):
                extension = '.pkl'
            elif isfile(casefile + '.py'):
                extension = '.py'
            else:
                info = 2

        if info == 0:
            globals = {}
            locals = {}
            try:
                execfile(rootname + extension)
            except IOError:
                info = 3 if extension == ".pkl" else 4

            if info == 4 and isfile(rootname + '.py'):
                info = 5
            else:
                func = basename(rootname)
                ppc = eval(func + "()")
#                if func in locals:
#                    ppc = eval(func + "()")
#                else:
#                    info = 5

    elif isinstance(casefile, dict):
        ppc = casefile
    else:
        info = 1

    # check contents of dict
    if info == 0:
        # check for required keys
        if not (ppc.has_key('baseMVA') and ppc.has_key('bus') \
            and ppc.has_key('gen') and ppc.has_key('branch')):
            info = 5
#        elif not (ppc.has_key('areas') and ppc.has_key('gencost')):
#            info = 5
        else:
            ppc = ppc

    if info != 0: # error encountered
        if info == 1:
            logger.error('Input arg should be a dict or a string '
                         'containing a filename')
        elif info == 2:
            logger.error('Specified case not a valid file')
        elif info == 3:
            logger.error('Specified MAT file does not exist')
        elif info == 4:
            logger.error('Specified M file does not exist')
        elif info == 5:
            logger.error('Syntax error or undefined data '
                         'matrix(ices) in the file')
        else:
            logger.error('Unknown error encountered loading case.')

        return info

    return ppc
