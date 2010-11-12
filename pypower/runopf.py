# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 [the "License"]
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
