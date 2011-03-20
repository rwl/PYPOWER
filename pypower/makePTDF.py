# Copyright (C) 2006-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
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

import logging

from numpy import zeros, nonzero

from idx_bus import BUS_TYPE, REF, BUS_I
from makeBdc import makeBdc

logger = logging.getLogger(__name__)

def makePTDF(baseMVA, bus, branch, slack):
    """Builds the DC PTDF matrix for a given choice of slack.
    Returns the DC PTDF
    matrix for a given choice of slack. The matrix is nbr x nb, where
    nbr is the number of branches and nb is the number of buses. The SLACK
    can be a scalar (single slack bus) or an nb x 1 column vector of
    weights specifying the proportion of the slack taken up at each bus.
    If the SLACK is not specified the reference bus is used by default.

    For convenience, SLACK can also be an nb x nb matrix, where each
    column specifies how the slack should be handled for injections
    at that bus.

    @see: L{makeLODF}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## use reference bus for slack by default
    if slack is None:
        slack = nonzero(bus[:, BUS_TYPE] == REF)
        slack = slack[0]

    ## set the slack bus to be used to compute initial PTDF
    if len(slack) == 1:
        slack_bus = slack
    else:
        slack_bus = 0      ## use bus 1 for temp slack bus

    nb = bus.shape[0]
    nbr = branch.shape[0]
    noref   = range(1, nb)      ## use bus 1 for voltage angle reference
    noslack = nonzero(range(nb) != slack_bus)

    ## check that bus numbers are equal to indices to bus (one set of bus numbers)
    if any(bus[:, BUS_I] != range(nb)):
        logger.error('makePTDF: buses must be numbered consecutively in '
                     'bus matrix')

    ## compute PTDF for single slack_bus
    Bbus, Bf, Pbusinj, Pfinj = makeBdc(baseMVA, bus, branch)
    H = zeros((nbr, nb))
    H[:, noslack] = (Bf[:, noref] / Bbus[noslack, noref]).todense()
            ##    = full(Bf(:, noref) * inv(Bbus(noslack, noref)))

    ## distribute slack, if requested
    if len(slack) != 1:
        if slack.shape[1] == 1:  ## slack is a vector of weights
            slack = slack / sum(slack)   ## normalize weights

            ## conceptually, we want to do ...
            ##    H = H * (eye(nb,nb) - slack * ones(1, nb))
            ## ... we just do it more efficiently
            v = H * slack
            for k in range(nb):
                H[:, k] = H[:, k] - v
        else:
            H = H * slack

    return H
