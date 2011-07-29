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

from pypower.ppoption import ppoption
from pypower.uopf import uopf
from pypower.printpf import printpf
from pypower.savecase import savecase
from pypower.loadcase import loadcase
from pypower.ext2int import ext2int
from pypower.int2ext import int2ext


def runuopf(casename='case9', ppopt=None, fname='', solvedcase=''):
    """Runs an optimal power flow with unit-decommitment heuristic.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## default arguments
    ppopt = ppoption(ppopt)

    ## read data & convert to internal bus numbering
    baseMVA, bus, gen, branch, areas, gencost = loadcase(casename)
    i2e, bus, gen, branch, areas = ext2int(bus, gen, branch, areas)

    ## run unit commitment / optimal power flow
    bus, gen, branch, f, success, et = uopf(baseMVA, bus, gen, gencost, branch, areas, ppopt)

    ## convert back to original bus numbering & print results
    bus, gen, branch, areas = int2ext(i2e, bus, gen, branch, areas)

    ##-----  output results  -----
    if fname:
        fd = None
        try:
            fd = open(fname, "wb")
        except Exception, detail:
            stderr.write("Error opening %s: %s.\n" % (fname, detail))
        finally:
            if fd is not None:
                printpf(baseMVA, bus, gen, branch, f, success, et, fd, ppopt)
                fd.close()

    printpf(baseMVA, bus, gen, branch, f, success, et, fd, ppopt)

    ## save solved case
    if solvedcase:
        savecase(solvedcase, solvedcase, baseMVA, bus, gen, branch, areas, gencost)

    return baseMVA, bus, gen, gencost, branch, f, success, et
