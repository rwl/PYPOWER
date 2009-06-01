# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

""" Converts external to internal bus numbering.

    Ported from:
        D. Zimmerman, "ext2int.m", MATPOWER, version 3.2,
        Power System Engineering Research Center (PSERC), 2007

    See http://www.pserc.cornell.edu/matpower/ for more info.
"""

from cvxopt import matrix

from idx_bus import BUS_I
from idx_gen import GEN_BUS
from idx_brch import F_BUS, T_BUS
from idx_area import PRICE_REF_BUS

def ext2int(bus, gen, branch, areas):
    """ Converts external to internal bus numbering.

        Converts external bus numbers (possibly non-consecutive) to consecutive
        internal bus numbers which start at 1.
    """
    i2e = bus[:, BUS_I]
    e2i = matrix(0.0, (max(i2e), 1))
    e2i[i2e] = matrix(range(1, bus.size[0])).T

    bus[:, BUS_I]    = e2i[bus[:, BUS_I]]
    gen[:, GEN_BUS]  = e2i[gen[:, GEN_BUS]]
    branch[:, F_BUS] = e2i[branch[:, F_BUS]]
    branch[:, T_BUS] = e2i[branch[:, T_BUS]]

    areas[:, PRICE_REF_BUS] = e2i[areas[:, PRICE_REF_BUS]]
