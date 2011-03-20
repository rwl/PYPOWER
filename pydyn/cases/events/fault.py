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

def fault():
    """ PyDyn event data file.

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    # event = [time type]
    event = array([
        [0.2, 1],
        [0.4, 1]
    ])

    # buschange = [time bus(row)  attribute(col) new_value]
    buschange = array([
        [0.2, 2, 6, -1e10],
        [0.4, 2, 6,     0]
    ])

    # linechange = [time  line(row)  attribute(col) new_value]
    linechange = array([])

    return event, buschange, linechange
