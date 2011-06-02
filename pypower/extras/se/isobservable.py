# Copyright (C) 2009-2011 Rui Bo <eeborui@hotmail.com>
# Copyright (C) 2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

from numpy import array, rank, Inf, linalg, r_

from pypower.se.getVarName import getVarName

def isobservable(H, pv, pq):
    """Test for observability.

    @return: 1 if the system is observable, 0 otherwise.
    """
    ## options
    tol     = 1e-5  # ppopt[1]
    check_reason = 1    # check reason for system being not observable
                        # 0: no check
                        # 1: check (NOTE: may be time consuming due to svd calculation)

    ## test if H is full rank
    m, n  = H.shape
    r     = rank(H)
    if r < min(m, n):
        TorF = 0
    else:
        TorF = 1

    ## look for reasons for system being not observable
    if check_reason and not TorF:
        ## look for variables not being observed
        idx_trivialColumns = array([])
        varNames = {}
        for j in range(n):
            normJ = linalg.norm(H[:, j], Inf)
            if normJ < tol:  # found a zero column
                idx_trivialColumns = r_[idx_trivialColumns, j]
                varName = getVarName(j, pv, pq)
                varNames[len(idx_trivialColumns)] = varName

        if len(idx_trivialColumns) > 0: # found zero-valued column vector
            print 'Warning: The following variables are not observable since they are not related with any measurement!'
            varNames
            idx_trivialColumns
        else:  # no zero-valued column vector
            ## look for dependent column vectors
            for j in range(n):
                rr = rank(H[:, range(j)])
                if rr != j:  # found dependent column vector
                    ## look for linearly depedent vector
                    colJ = H[:, j]  # j(th) column of H
                    varJName = getVarName(j, pv, pq)
                    for k in range(j - 1):
                        colK = H[:, k]
                        if rank(r_[colK, colJ]) < 2:  # k(th) column vector is linearly dependent of j(th) column vector
                            varKName = getVarName(k, pv, pq)
                            print 'Warning: %d(th) column vector (w.r.t. %s) of H is linearly dependent of %d(th) column vector (w.r.t. %s)!' % j, varJName, k, varKName
                            return TorF
        print 'Warning: No specific reason was found for system being not observable.'

    return TorF
