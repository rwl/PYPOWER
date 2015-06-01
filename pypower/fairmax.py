# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

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
    """
    val = max(x)                      ## find max value
    i   = nonzero(x == val)           ## find all positions where this occurs
    n   = len(i)                      ## number of occurences
    idx = i( fix(n * random()) + 1 )  ## select index randomly among occurances

    return val, idx
