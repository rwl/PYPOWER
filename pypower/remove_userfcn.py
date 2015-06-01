# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

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
    """
    n = len(ppc['userfcn'][stage])

    for k in range(n - 1, -1, -1):
        if ppc['userfcn'][stage][k]['fcn'] == fcn:
            del ppc['userfcn'][stage][k]
            break

    return ppc
