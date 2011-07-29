# Copyright (C) 2009-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
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

"""Removes a userfcn from the list to be called for a case.
"""

def remove_userfcn(ppc, stage, fcn):
    """Removes a userfcn from the list to be called for a case.

    A userfcn is a callback function that can be called automatically by
    PYPOWER at one of various stages in a simulation. This function removes
    the last instance of the userfcn for the given C{stage} with the function
    handle specified by C{fcn}.

    @see: L{add_userfcn}, L{run_userfcn}, L{toggle_reserves},
          L{toggle_iflims}, L{runopf_w_res}

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    n = len(ppc['userfcn'][stage])

    for k in range(n - 1, -1, -1):
        if ppc['userfcn'][stage][k]['fcn'] == fcn:
            del ppc['userfcn'][stage][k]
            break

    return ppc
