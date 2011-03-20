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

def Loadgov(casefile_dyn):
    """ Loads governor data

    @param casefile_dyn: m-file or struct with dynamic data
    @return: governor parameter matrix

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Load data
    if isinstance(casefile_dyn, dict):
        gov = casefile_dyn["gov"]
    else:
        dyn = __import__(casefile_dyn)
        _, _, gov, _, _, _ = eval("dyn.%s" % casefile_dyn)

    ## Consecutive numbering or rows
    Pgov = copy(gov)

    for i in range(len(gov[0, :])):
        Pgov[gov[:, 0], i] = gov[:, i]

    return Pgov
