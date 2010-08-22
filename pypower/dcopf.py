# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
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
    mpc, ppopt = opf_args(*args, **kw_args);
    ppopt = ppoption(ppopt, "PF_DC", 1)

    return opf(mpc, ppopt)