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

from numpy import array, zeros, r_, copy, argsort, Inf, flatnonzero as find

def busorder(bus, branch, scheme=0):
    """Reorders the bus matrix rows for improved LU factorisation and forward/
    backward substitution performance according to the schemes described in
    Section 4.3 of the book 'Computational Methods for Electric Power Systems'
    by Mariesa Crow.

    @param bus: bus data matrix
    @param branch: branch data matrix
    @param scheme: Ordering scheme. 1 - Buses are ordered according to the
    number of branches connected to them. 2 - Minimum degree/Markowitz/Tinney I
    algorithm.Updates the degree of buses after placing those with the lowest
    degree in the ordering scheme and eliminating the associated branches.
    @return: reordered bus data matrix
    """
    if scheme == 0:
        degree = _degree(bus, branch)
        idx = argsort(degree)
    elif scheme == 1:
        # Eliminate branches from a copy of the given branch data.
        brch = copy(branch)

        idx = array([], int)  # new bus indexes
        elim = array([], int) # indexes of buses to be eliminated

        while len(idx) < bus.shape[0]:
            # Eliminate branches connected from or to buses already ordered.
            il = zeros(brch.shape[0], bool)
            for i in bus[:, 0][elim]:
                il |= (brch[:, 0] == i) | (brch[:, 1] == i)
            brch = brch[find(il == False), :]

            degree = _degree(bus, brch)
            # Ignore degrees of buses already ordered.
            degree[idx] = Inf
            elim = find(degree == min(degree))
            idx = r_[idx, elim]
    elif scheme == 2:
        # Berry/Tinney II algorithm.
        raise NotImplementedError
    else:
        raise ValueError

    bus = bus[idx, :]

    return bus


def _degree(bus, branch):
    """Returns a vector of the number of branches in the given branch data
    matrix connected to each bus in the given bus data matrix.
    """
    nb = bus.shape[0]

    degree = zeros(nb)

    for i in range(nb):
        k = bus[i, 0]
        degree[i] = sum(branch[:, 0] == k) + sum(branch[:, 1] == k)

    return degree


if __name__ == "__main__":
    import case6ww
    ppc = case6ww.case6ww()
    bus = busorder(ppc["bus"], ppc["branch"], scheme=1)
    print bus
