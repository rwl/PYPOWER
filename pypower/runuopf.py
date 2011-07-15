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

"""Runs an optimal power flow with unit-decommitment heuristic.
"""

from sys import stderr

from ppoption import ppoption
from uopf import uopf
from printpf import printpf
from savecase import savecase


def runuopf(casedata='case9', ppopt=None, fname='', solvedcase=''):
    """Runs an optimal power flow with unit-decommitment heuristic.

    @see: L{rundcopf}, L{runuopf}
    """
    ## default arguments
    ppopt = ppoption(ppopt)

    ##-----  run the unit de-commitment / optimal power flow  -----
    r = uopf(casedata, ppopt)

    ##-----  output results  -----
    if fname:
        fd = None
        try:
            fd = open(fname, "wb")
        except Exception, detail:
            stderr.write("Error opening %s: %s.\n" % (fname, detail))
        finally:
            if fd is not None:
                printpf(r, fd, ppopt)
                fd.close()

    printpf(r, ppopt=ppopt)

    ## save solved case
    if solvedcase:
        savecase(solvedcase, r)

    return r
