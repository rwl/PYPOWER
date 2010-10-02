# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
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
