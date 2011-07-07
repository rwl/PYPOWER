# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

"""Runs a DC optimal power flow with unit-decommitment heuristic.
"""

from ppoption import ppoption
from runuopf import runuopf


def runduopf(casedata='case9', ppopt=None, fname='', solvedcase=''):
    """Runs a DC optimal power flow with unit-decommitment heuristic.

    @see: L{rundcopf}, L{runuopf}
    """
    ## default arguments
    ppopt = ppoption(ppopt, PF_DC=True)

    return runuopf(casedata, ppopt, fname, solvedcase)