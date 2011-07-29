# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

"""Compares two solved power flow cases.
"""

from sys import stdout

from numpy import argmax

from pypower.loadcase import loadcase


def compare(case1, case2):
    """Compares two solved power flow (or optimal power flow) cases and prints
    a summary of the differences.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    ## set up index name matrices
    buscols = [ 'BUS_I',
                'BUS_TYPE',
                'PD',
                'QD',
                'GS',
                'BS',
                'BUS_AREA',
                'VM',
                'VA',
                'BASE_KV'   ]
    buscols = buscols.extend([
                'ZONE',
                'VMAX',
                'VMIN',
                'LAM_P',
                'LAM_Q',
                'MU_VMAX',
                'MU_VMIN'   ])

    gencols = [ 'GEN_BUS',
                'PG',
                'QG',
                'QMAX',
                'QMIN',
                'VG',
                'MBASE',
                'GEN_STATUS',
                'PMAX',
                'PMIN'      ]
    gencols = gencols.extend([
                'MU_PMAX',
                'MU_PMIN',
                'MU_QMAX',
                'MU_QMIN'   ])

    brcols = [  'F_BUS',
                'T_BUS',
                'BR_R',
                'BR_X',
                'BR_B',
                'RATE_A',
                'RATE_B',
                'RATE_C',
                'TAP',
                'SHIFT'     ]
    brcols = brcols.extend([
                'BR_STATUS',
                'PF',
                'QF',
                'PT',
                'QT',
                'MU_SF',
                'MU_ST' ])

    ## read data & convert to internal bus numbering
    baseMVA1, bus1, gen1, branch1, area1, gencost1 = loadcase(case1)
    baseMVA2, bus2, gen2, branch2, area2, gencost2 = loadcase(case2)

    ## print results
    stdout.write('----------------  --------------  --------------  --------------  -----\n')
    stdout.write(' matrix / col         case 1          case 2        difference     row \n')
    stdout.write('----------------  --------------  --------------  --------------  -----\n')

    ## bus comparison
    temp = max(abs(bus1 - bus2))
    i = argmax(abs(bus1 - bus2))
    v = max(temp)
    gmax = argmax(temp)
    i = i[gmax]
    stdout.write('bus\n')
    for j in range(buscols.shape[0]):
        v = max(abs(bus1[:, j] - bus2[:, j]))
        i = argmax(abs(bus1[:, j] - bus2[:, j]))
        if v:
            if j == gmax:
                s = ' *'
            else:
                s = ''
            stdout.write('  %-12s%16g%16g%16g%7d%s\n' % (buscols[j, :], bus1[i, j], bus2[i, j], v, i, s))

    ## gen comparison
    temp = max(abs(gen1 - gen2))
    i = argmax(abs(gen1 - gen2))
    v = max(temp)
    gmax = argmax(temp)
    i = i[gmax]
    stdout.write('\ngen\n')
    for j in range(gencols.shape[0]):
        v = max(abs(gen1[:, j] - gen2[:, j]))
        i = argmax(abs(gen1[:, j] - gen2[:, j]))
        if v:
            if j == gmax:
                s = ' *'
            else:
                s = ''
            stdout.write('  %-12s%16g%16g%16g%7d%s\n' % (gencols[j, :], gen1[i, j], gen2[i, j], v, i, s))

    ## branch comparison
    temp = max(abs(branch1 - branch2))
    i = argmax(abs(branch1 - branch2))
    v = max(temp)
    gmax = argmax(temp)
    i = i[gmax]
    stdout.write('\nbranch\n')
    for j in range(brcols.shape[0]):
        v = max(abs(branch1[:, j] - branch2[:, j]))
        i = argmax(abs(branch1[:, j] - branch2[:, j]))
        if v:
            if j == gmax:
                s = ' *'
            else:
                s = ''
            stdout.write('  %-12s%16g%16g%16g%7d%s\n' % (brcols[j, :], branch1[i, j], branch2[i, j], v, i, s))

    return
