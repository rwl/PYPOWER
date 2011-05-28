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

from pypower.cpf.cpf import cpf
from pypower.cpf.drawPVcurves import drawPVcurves

def test_cpf():
    """Test continuation power flow (CPF).

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    casename = 'case30'#'case6bus' #'case30'

    ## test cpf
    print '\n------------testing continuation power flow (CPF) solver\n'
    loadvarloc = 7#6#7                 # bus number at which load changes
    sigmaForLambda = 0.2#0.05          # stepsize for Lambda
    sigmaForVoltage = 0.05#0.025       # stepsize for voltage
    max_lambda, predicted_list, corrected_list, combined_list, success, et = \
        cpf(casename, loadvarloc, sigmaForLambda, sigmaForVoltage)
    print 'maximum lambda is %f\n\n' % max_lambda

    ## draw PV curve
    flag_combinedCurve = True
    busesToDraw = []#range(3, 6)
    drawPVcurves(casename, loadvarloc, corrected_list, combined_list,
                 flag_combinedCurve, busesToDraw)
