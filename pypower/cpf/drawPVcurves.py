# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from numpy import flatnonzero as find

from pylab import figure, hold, plot, legend, title

from pypower.loadcase import loadcase


def drawPVcurves(casedata, loadvarloc, corrected_list, combined_list,
                 flag_combinedCurve, busesToDraw=None):
    """Draw PV curves for specified buses.

    @param corrected_list, combined_list: data points obtained from CPF solver
    @param loadvarloc: load variation location(in external bus numbering).
    Single bus supported so far.
    @param flag_combinedCurve: flag indicating if the prediction-correction
    curve will be drawn
    @param busesToDraw: bus indices whose PV curve will be be drawn

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if busesToDraw is None:
        busesToDraw = loadvarloc # draw the curve for the load changing bus

    ## load the case & convert to internal bus numbering
    baseMVA, bus, gen, branch = loadcase(casedata)
    nb = bus.shape[0]

    correctedDataNum = corrected_list.shape[1] - 1
    combinedDataNum  = combined_list.shape[1] - 1

    ## prepare data for drawing
    lambda_corrected = corrected_list[nb+1, range(1, correctedDataNum + 1)]
    lambda_combined  = combined_list[nb+1, range(1, combinedDataNum + 1)]

    print 'Start plotting CPF curve(s)...\n'
    for j in range(len(busesToDraw)):#for i = 1+npv+1:1+npv+npq
        i = find(corrected_list[:, 0] == busesToDraw[j]) # find row index

        ## get voltage magnitudes
        Vm_corrected = abs(corrected_list[i, range(1, correctedDataNum + 1)])
        Vm_combined  = abs(combined_list[i, range(1, combinedDataNum + 1)])

        ## create a new figure
        figure()
        hold(True)

        ## plot PV curve
        plot(lambda_corrected, Vm_corrected, 'bx-')

        ## plot CPF prediction-correction curve
        if flag_combinedCurve == True:
            plot(lambda_combined, Vm_combined, 'r.-')
            legend('CPF Curve', 'Prediction-Correction Curve')
            legend('Location', 'Best')


        ## add plot title
        title('Vm at bus %s w.r.t. load (p.u.) at %s' % (busesToDraw[j], loadvarloc))

    print 'Plotting is done.\n'
