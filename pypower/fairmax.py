# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

"""Same as built-in C{max}, except breaks ties randomly.
"""

from random import random
from numpy import fix, flatnonzero as find


def fairmax(x):
    """Like numpy C{max} and C{argmax}, except breaks ties randomly.

    Takes a vector as an argument and returns the same output as the
    built-in function C{max} with two output parameters, except that
    where the maximum value occurs at more than one position in the
    vector, the index is chosen randomly from these positions as opposed
    to just choosing the first occurrence.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    val = max(x)                      ## find max value
    i   = find(x == val)              ## find all positions where this occurs
    n   = len(i)                      ## number of occurences
    idx = i[ fix(n * random()) + 1 ]  ## select index randomly among occurances

    return val, idx
