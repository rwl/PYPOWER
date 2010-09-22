# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software, you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program, if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from pypower.ppoption import ppoption
from pypower.runopf import runopf

def rundcopf(casedata='case9', ppopt=None, fname='', solvedcase=''):
    """ Runs a DC optimal power flow.

    @see: L{runopf}, L{runduopf}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## default arguments
    ppopt = ppoption() if ppopt is None else ppopt

    ppopt = ppoption(ppopt, PF_DC=True)
    return runopf(casedata, ppopt, fname, solvedcase)