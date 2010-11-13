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

from numpy import zeros

def Loadevents(casefile_ev):
    """ Loads event data.

    @param casefile_ev: m-file with event data
    @return: triple of the form (event = list with time and type of events,
        buschange = time, bus number, bus parameter, new value,
        linechange = time, branch number, branch parameter, new value)

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    if isinstance(casefile_ev):
        event = casefile_ev["event"]
        type1 = casefile_ev["buschange"]
        type2 = casefile_ev["linechange"]
    else:
        ev = __import__(casefile_ev)
        event, type1, type2 = eval("ev.%s" % casefile_ev)

    buschange = zeros(event.shape[0], 4)
    linechange = zeros(event.shape[0], 4)

    i1 = 0
    i2 = 0

    for i in range(event.shape[0]):
        if event[i, 2] == 1:
            buschange[i, :] = type1[i1, :]
            i1 = i1 + 1
        elif event[i, 2] == 2:
            linechange[i, :] = type2[i2, :]
            i2 = i2 + 1

    return event, buschange, linechange
