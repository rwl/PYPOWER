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

from numpy import array, zeros, r_, argsort, flatnonzero as find

def busorder(bus, branch, scheme=0):
    """Reorders the bus matrix rows for improved LU factorisation and forward/
    backward substitution performance according to the schemes described in
    Section 4.3 of the book 'Computational Methods for Electric Power Systems'
    by Mariesa Crow.
    """
    if scheme == 0:
        # Order buses according to the number of branches connected to them.
        degree = _degree(bus, branch)
        idx = argsort(degree)
    elif scheme == 1:
        # Minimum degree/Markowitz/Tinney I algorithm. Updates the degree of
        # buses after placing those with the lowest degree in the ordering
        # scheme.
        idx = array([], int)
        degree = _degree(bus, branch)
        elim = find(degree == min(degree))
        idx = r_[idx, elim]

        print elim, idx
    elif scheme == 2:
        # Berry/Tinney II algorithm.
        raise NotImplementedError
    else:
        raise ValueError

    print degree

#    bus = bus[idx, :]

    return bus


def _degree(bus, branch):
    """Returns a vector of the number of branches in the given branch data
    matrix connected to each bus in the given bus data matrix.
    """
    nb = bus.shape[0]

    degree = zeros(nb)

    for b in range(nb):
        i = bus[b, 0]
        degree[b] = sum(branch[:, 0] == i) + sum(branch[:, 1] == i)

    return degree


if __name__ == "__main__":
    import case6ww
    ppc = case6ww.case6ww()
    bus = busorder(ppc["bus"], ppc["branch"], scheme=1)
    print bus
