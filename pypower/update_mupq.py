# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY], without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

"""Updates values of generator limit shadow prices.
"""

from pypower.idx_gen import MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN


def update_mupq(baseMVA, gen, mu_PQh, mu_PQl, data):
    """Updates values of generator limit shadow prices.

    Updates the values of C{MU_PMIN}, C{MU_PMAX}, C{MU_QMIN}, C{MU_QMAX} based
    on any shadow prices on the sloped portions of the generator
    capability curve constraints.

    @param mu_PQh: shadow prices on upper sloped portion of capability curves
    @param mu_PQl: shadow prices on lower sloped portion of capability curves
    @param data: "data" dict returned by L{makeApq}

    @see: C{makeApq}.
    """
    ipqh, ipql, Apqhdata, Apqldata = \
        data['ipqh'], data['ipql'], data['h'], data['l']

    # If we succeeded and there were generators with general PQ curve
    # characteristics, this is the time to re-compute the multipliers,
    # splitting any nonzero multiplier on one of the linear bounds among the
    # Pmax, Pmin, Qmax or Qmin limits, producing one multiplier for a P limit and
    # another for a Q limit. For upper Q limit, if we are neither at Pmin nor at
    # Pmax, the limit is taken as Pmin if the Qmax line's normal has a negative P
    # component, Pmax if it has a positive P component. Messy but there really
    # are many cases.
    muPmax = gen[:, MU_PMAX]
    muPmin = gen[:, MU_PMIN]
    if len(mu_PQh) > 0:
        #gen[:, [MU_PMIN, MU_PMAX, MU_QMIN, MU_QMAX]]
        k = 0
        for i in ipqh:
            if muPmax[i] > 0:
                gen[i, MU_PMAX] = gen[i, MU_PMAX] - mu_PQh[k] * Apqhdata[k, 0] / baseMVA
            elif muPmin[i] > 0:
                gen[i, MU_PMIN] = gen[i, MU_PMIN] + mu_PQh[k] * Apqhdata[k, 0] / baseMVA
            else:
                if Apqhdata[k, 0] >= 0:
                    gen[i, MU_PMAX] = gen[i, MU_PMAX] - mu_PQh[k] * Apqhdata[k, 0] / baseMVA
                else:
                    gen[i, MU_PMIN] = gen[i, MU_PMIN] + mu_PQh[k] * Apqhdata[k, 0] / baseMVA

            gen[i, MU_QMAX] = gen[i, MU_QMAX] - mu_PQh[k] * Apqhdata[k, 1] / baseMVA
            k = k + 1


    if len(mu_PQl) > 0:
        #gen[:, [MU_PMIN, MU_PMAX, MU_QMIN, MU_QMAX]]
        k = 0
        for i in ipql:
            if muPmax[i] > 0:
                gen[i, MU_PMAX] = gen[i, MU_PMAX] - mu_PQl[k] * Apqldata[k, 0] / baseMVA
            elif muPmin[i] > 0:
                gen[i, MU_PMIN] = gen[i, MU_PMIN] + mu_PQl[k] * Apqldata[k, 0] / baseMVA
            else:
                if Apqldata[k, 0] >= 0:
                    gen[i, MU_PMAX] = gen[i, MU_PMAX] - mu_PQl[k] * Apqldata[k, 0] / baseMVA
                else:
                    gen[i, MU_PMIN] = gen[i, MU_PMIN] + mu_PQl[k] * Apqldata[k, 0] / baseMVA

            gen[i, MU_QMIN] = gen[i, MU_QMIN] + mu_PQl[k] * Apqldata[k, 1] / baseMVA
            k = k + 1

    #gen[:, [MU_PMIN, MU_PMAX, MU_QMIN, MU_QMAX]]
    #-[ mu_PQl[:2], mu_PQh[:2] ] / baseMVA
    #-[ mu_PQl[:2] * Apqldata[:2, 0], mu_PQh[:2] * Apqhdata[:2, 0] ] / baseMVA
    #-[ mu_PQl[:2] * Apqldata[:2, 1], mu_PQh[:2] * Apqhdata[:2, 1] ] / baseMVA

    return gen
