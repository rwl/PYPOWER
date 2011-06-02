# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

import sys

from numpy import shape

from pypower.ppoption import ppoption
from pypower.idx_gen import PG, GEN_BUS
from pypower.printpf import printpf

from pypower.extras.smartmarket.idx_disp import \
    PRICE, QUANTITY, FCOST, VCOST, SCOST, PENALTY


def printmkt(r, t, dispatch, success, fd=None, ppopt=None):
    """Prints results of ISO computation.

    Prints results of ISO computation to FD (a file descriptor which
    defaults to C{stdout}). C{ppopt} is a PYPOWER options vector (see
    C{ppoption} for details). Uses default options if this parameter is
    not given. The duration of the dispatch period (in hours) is given
    in C{t}. C{dispatch} and C{results} are the values returned by C{smartmkt}.

    @see C{smartmkt}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ##----- initialization -----
    ## default arguments
    if ppopt == None: ppopt = ppoption   ## use default options

    if fd == None: fd = sys.stdout       ## print to stdio by default

    gen = r['gen']

    ## options
    OUT_ALL         = ppopt['OUT_ALL']
    OUT_RAW         = ppopt['OUT_RAW]']

    ## parameters
    ng = shape(gen)[0]

    ##----- print the stuff -----
    pay = dispatch[:, PRICE] * dispatch[:, QUANTITY] * t
    cost = dispatch[:, FCOST] + dispatch[:, VCOST] + dispatch[:, SCOST] + dispatch[:, PENALTY]
    if OUT_ALL:
        ## dispatch data
        fd.write('\n================================================================================')
        fd.write('\n|     Market Summary                                                           |')
        fd.write('\n================================================================================')
        fd.write('\nDispatch period duration: %.2f hours' % t)
        fd.write('\nGen  Bus     Pg      Price    Revenue   Fix+Var   Strt/Stp   Total    Earnings')
        fd.write('\n #    #     (MW)    ($/MWh)     ($)     Cost ($)  Cost ($)  Cost ($)     ($)  ')
        fd.write('\n---  ---  --------  --------  --------  --------  --------  --------  --------')
        for i in range(shape(gen)[0]):
            if gen[i, PG]:
                fd.write('\n%3d%5d%9.2f%10.3f%10.2f%10.2f%10.2f%10.2f%10.2f' %
                    (i, gen[i, GEN_BUS], dispatch[i, QUANTITY], dispatch[i, PRICE], pay[i],
                    dispatch[i, FCOST] + dispatch[i, VCOST],
                    dispatch[i, SCOST], cost[i], pay[i] - cost[i]))
            else:
                if dispatch(i, SCOST) or dispatch(i, PENALTY):
                    fd.write('\n%3d%5d      -  %10.3f       -         -  %10.2f%10.2f%10.2f' %
                        (i, gen(i, GEN_BUS), dispatch(i, PRICE), dispatch(i, SCOST),
                        cost(i), pay(i) - cost(i)))
                else:
                    fd.write('\n%3d%5d      -  %10.3f       -         -         -         -         -' %
                        (i, gen(i, GEN_BUS), dispatch(i, PRICE)))
            if dispatch[i, PENALTY]:
                fd.write('%10.2f penalty (included in total cost)' % dispatch[i, PENALTY])

        fd.write('\n          --------            --------  --------  --------  --------  --------')
        fd.write('\nTotal:  %9.2f          %10.2f%10.2f%10.2f%10.2f%10.2f' %
            sum(dispatch[:, QUANTITY]), sum(pay), sum(dispatch[:, FCOST]) + sum(dispatch[:, VCOST]),
            sum(dispatch[:, SCOST]), sum(cost), sum(pay - cost))
        if sum(dispatch[:, PENALTY]):
            fd.write('%10.2f penalty (included in total cost)' % sum(dispatch[:, PENALTY]))
        fd.write('\n')

    ## print raw data for Perl database interface
    if OUT_RAW:
        fd.write('----------  raw PW::Dispatch data below  ----------\n')
        fd.write('dispatch\n')
        for i in range(ng):
            fd.write('%d\t%.8g\t%.8g\t%.8g\t%.8g\t%.8g\t%.8g\t%.8g\n' %
                (i, dispatch[i, [QUANTITY, PRICE, FCOST, VCOST, SCOST, PENALTY]], pay[i] - cost[i]))
        fd.write('----------  raw PW::Dispatch data above  ----------\n')

    ## print remaining opf output
    printpf(r, fd, ppopt)
