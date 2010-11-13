# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

import logging

from ppoption import ppoption
from opf import opf
from printpf import printpf
from savecase import savecase

logger = logging.getLogger(__name__)

def runopf(casedata='case9', ppopt=None, fname='', solvedcase=''):
    """ Runs an optimal power flow.

    @see: L{rundcopf}, L{runuopf}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## default arguments
    ppopt = ppoption() if ppopt is None else ppopt

    ##-----  run the optimal power flow  -----
    r, success = opf(casedata, ppopt)

    ##-----  output results  -----
    if fname:
        fd = None
        try:
            fd = open(fname, "wb")
        except Exception, detail:
            logger.error("Error opening %s: %s." % (fname, detail))
        finally:
            if fd is not None:
                printpf(r, fd, ppopt)
                fd.close()

    printpf(r, ppopt=ppopt)

    ## save solved case
    if solvedcase:
        savecase(solvedcase, r)

    return r, success
