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

from numpy import zeros, argsort

def busorder(bus, branch, scheme=1):
    """Reorders the bus matrix rows for improved Jabobian structure
    according to the schemes described in the book 'Computational
    Methods for Electric Power Systems' by Mariesa Crow.
    """
    nb = bus.shape[0]
    idx = bus[:, 0]

    if scheme == 1:
        nbrch = zeros(nb)

        for b in range(nb):
            i = bus[b, 0]
            nbrch[b] += sum(branch[:, 0] == i)
            nbrch[b] += sum(branch[:, 1] == i)

        idx = argsort(nbrch)
    elif scheme == 2:
        pass
    elif scheme == 3:
        raise NotImplementedError
    else:
        raise ValueError

    bus = bus[:, idx]

    return bus


if __name__ == "__main__":
    import case4gs
    ppc = case4gs.case4gs()
    bus = busorder(ppc["bus"], ppc["branch"])
    print bus
