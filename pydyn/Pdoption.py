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

from numpy import array

def Pdoption():
    """ Returns default option vector.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    ## Options vector
    options = array([
        1,              # method
        1e-4,           # tolerance
        1e-3,           # minstepsize
        1e2,            # maxstepsize

        1,              # output
        1               # plots
    ])

    return options
