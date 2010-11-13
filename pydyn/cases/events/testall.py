# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
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

from numpy import array

def testall():
    """ PyDyn event data file.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    # event = [time type]
    event = array([
            [0.2,     1],
            [0.3,     1],
            [1,       1],
            [1.1,     1],
            [1.2,     2],
            [1.2,     2],
            [1.2,     2],
            [1.4,     1]
    ])

    # buschange = [time bus(row)  attribute(col) new_value]
    buschange = array([
            [0.2,  6,  6,  -1e10],
            [0.3,  6,  6,   0   ],
            [1,    5,  6,  -1e10],
            [1.1,  5,  6,   0   ],
            [1.4,  7,  3,   0.9 ],
            [1.4,  7,  4,   0.5 ]
    ])

    # linechange = [time  line(row)  attribute(col) new_value]
    linechange = array([
            [1.2,  2,   3,   0.1],
            [1.2,  2,   4,   0.2],
            [1.2,  2,   5,   0.3]
    ])

    return event, buschange, linechange
