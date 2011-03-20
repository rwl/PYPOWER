# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
#
# PYDYN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYDYN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYDYN. If not, see <http://www.gnu.org/licenses/>.

from numpy import copy

def Loadgen(casefile_dyn, output):
    """ Loads generator data.

    @param casefile_dyn: m-file or struct with dynamic data
    @param output: print progress info?
    @return: generator parameter matrix

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Load data
    if isinstance(casefile_dyn, dict):
        gen = casefile_dyn["gen"]
    else:
        dyn = __import__(casefile_dyn)
        gen, _, _, _, _, _ = eval("dyn.%s" % casefile_dyn)

    Pgen = copy(gen)

    genmodel = Pgen[:, 0]

    ## Define generator models
    d = range(len(genmodel))
    type1 = d[genmodel == 1]
    type2 = d[genmodel == 2]

    ## Check transient saliency
    xd_tr = Pgen[type2, 7]
    xq_tr = Pgen[type2, 8]

    if sum(xd_tr != xq_tr) >= 1:
        if output:
            print 'Warning: transient saliency not supported'
        Pgen[type2, 8] = Pgen[type2, 7]

    return Pgen
