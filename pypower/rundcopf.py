# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Runs a DC optimal power flow.
"""

from os.path import dirname, join

from pypower.ppoption import ppoption
from pypower.runopf import runopf


def rundcopf(casedata=None, ppopt=None, fname='', solvedcase=''):
    """Runs a DC optimal power flow.

    @see: L{runopf}, L{runduopf}

    @author: Ray Zimmerman (PSERC Cornell)
    """
    ## default arguments
    if casedata is None:
        casedata = join(dirname(__file__), 'case9')
    ppopt = ppoption(ppopt, PF_DC=True)

    return runopf(casedata, ppopt, fname, solvedcase)
