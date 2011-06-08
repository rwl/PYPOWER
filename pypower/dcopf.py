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

from opf_args import opf_args
from ppoption import ppoption
from opf import opf

def dcopf(*args, **kw_args):
    """Solves a DC optimal power flow.

    This is a simple wrapper function around L{opf} that sets the C{PF_DC}
    option to 1 before calling L{opf}.
    See L{opf} for the details of input and output arguments.

    @see: L{rundcopf}.
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ppc, ppopt = opf_args(*args, **kw_args);
    ppopt = ppoption(ppopt, PF_DC=1)

    return opf(ppc, ppopt)