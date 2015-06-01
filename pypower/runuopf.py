# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Runs an optimal power flow with unit-decommitment heuristic.
"""

from sys import stderr

from os.path import dirname, join

from pypower.ppoption import ppoption
from pypower.uopf import uopf
from pypower.printpf import printpf
from pypower.savecase import savecase


def runuopf(casedata=None, ppopt=None, fname='', solvedcase=''):
    """Runs an optimal power flow with unit-decommitment heuristic.

    @see: L{rundcopf}, L{runuopf}

    @author: Ray Zimmerman (PSERC Cornell)
    """
    ## default arguments
    if casedata is None:
        casedata = join(dirname(__file__), 'case9')
    ppopt = ppoption(ppopt)

    ##-----  run the unit de-commitment / optimal power flow  -----
    r = uopf(casedata, ppopt)

    ##-----  output results  -----
    if fname:
        fd = None
        try:
            fd = open(fname, "a")
        except Exception as detail:
            stderr.write("Error opening %s: %s.\n" % (fname, detail))
        finally:
            if fd is not None:
                printpf(r, fd, ppopt)
                fd.close()

    else:
        printpf(r, stdout, ppopt=ppopt)

    ## save solved case
    if solvedcase:
        savecase(solvedcase, r)

    return r
