# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
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

"""Same as built-in C{max}, except breaks ties randomly.
"""

from random import random
from numpy import nonzero, fix


def fairmax(x):
    """Same as built-in C{max}, except breaks ties randomly.

    Takes a vector as an argument and returns the same output as the
    built-in function C{max} with two output parameters, except that
    where the maximum value occurs at more than one position in the
    vector, the index is chosen randomly from these positions as opposed
    to just choosing the first occurance.

    @see: C{max}

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    val = max(x)                      ## find max value
    i   = nonzero(x == val)           ## find all positions where this occurs
    n   = len(i)                      ## number of occurences
    idx = i( fix(n * random()) + 1 )  ## select index randomly among occurances

    return val, idx
