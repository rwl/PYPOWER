# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

from random import random
from numpy import nonzero, fix

def fairmax(x):
    """Same as built-in MAX, except breaks ties randomly.

    Takes a vector as an argument and returns
    the same output as the built-in function MAX with two output
    parameters, except that where the maximum value occurs at more
    than one position in the  vector, the index is chosen randomly
    from these positions as opposed to just choosing the first occurance.

    @see: L{max}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    val = max(x);                     ## find max value
    i   = nonzero(x == val)           ## find all positions where this occurs
    n   = len(i)                      ## number of occurences
    idx = i( fix(n * random()) + 1 )  ## select index randomly among occurances

    return val, idx
