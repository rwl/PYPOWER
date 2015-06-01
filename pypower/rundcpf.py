# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Runs a DC power flow.
"""

from os.path import dirname, join

from pypower.ppoption import ppoption
from pypower.runpf import runpf


def rundcpf(casedata=None, ppopt=None, fname='', solvedcase=''):
    """Runs a DC power flow.

    @see: L{runpf}

    @author: Ray Zimmerman (PSERC Cornell)
    """
    ## default arguments
    if casedata is None:
        casedata = join(dirname(__file__), 'case9')
    ppopt = ppoption(ppopt, PF_DC=True)

    return runpf(casedata, ppopt, fname, solvedcase)
