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

"""Runs an optimal power flow.
"""

from sys import stdout, stderr

from os.path import dirname, join

from pypower.ppoption import ppoption
from pypower.loadcase import loadcase
from pypower.opf import opf
from pypower.printpf import printpf
from pypower.savecase import savecase


def runopf(casedata=None, ppopt=None, fname='', solvedcase=''):
    """Runs an optimal power flow.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## default arguments
    if casedata is None:
        casedata = join(dirname(__file__), 'case9')
    ppopt = ppoption(ppopt)

    ## read data
    baseMVA, bus, gen, branch, areas, gencost = loadcase(casedata)

    ##-----  run the optimal power flow  -----
    bus, gen, branch, f, success, _, et, _, _, _, _ = \
            opf(baseMVA, bus, gen, branch, areas, gencost, ppopt)

    ##-----  output results  -----
    if fname:
        fd = None
        try:
            fd = open(fname, "wb")
        except IOError, detail:
            stderr.write("Error opening %s: %s.\n" % (fname, detail))
        finally:
            if fd is not None:
                printpf(baseMVA, bus, gen, branch, f, success, et, fd, ppopt)
                fd.close()

    printpf(baseMVA, bus, gen, branch, f, success, et, stdout, ppopt)

    ## save solved case
    if solvedcase:
        savecase(solvedcase, baseMVA, bus, gen, branch, areas, gencost)

    return baseMVA, bus, gen, gencost, branch, f, success, et


if __name__ == '__main__':
    runopf()
