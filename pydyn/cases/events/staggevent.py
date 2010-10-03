# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0, (the "License")
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

from numpy import array

def staggevent():
    """ PyDyn event data file.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    # event = [time type]
    event = array([
        [0.0, 1],
        [0.0, 1],
        [0.1, 1],
        [0.1, 1]
    ])

    # buschange = [time bus(row)  attribute(col) new_value]
    buschange = array([
        [0.0, 2, 6, -1e10],
        [0.0, 2, 5,  1e10],
        [0.1, 2, 6,     0],
        [0.1, 2, 5,     0]
    ])

    # linechange = [time  line(row)  attribute(col) new_value]
    linechange = array([])

    return event, buschange, linechange
