# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
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

from time import time

from numpy import zeros, ones, exp, pi, copy
from numpy import flatnonzero as find

from pypower.loadcase import loadcase
from pypower.ext2int import ext2int
from pypower.bustypes import bustypes
from pypower.makeYbus import makeYbus

from pypower.cpf.cpf_correctVoltage import cpf_correctVoltage
from pypower.cpf.cpf_correctlmbda import cpf_correctlmbda
from pypower.cpf.cpf_predict import cpf_predict

from pypower.idx_bus import *
from pypower.idx_gen import *
from pypower.idx_brch import *

def cpf(casedata, loadvarloc, sigmaForlmbda=0.1, sigmaForVoltage=0.025):
    """Run continuation power flow (CPF) solver.

    @param loadvarloc: load variation location(in external bus numbering).
        Single bus supported so far.
    @param sigmaForlmbda: stepsize for lmbda
    @param sigmaForVoltage: stepsize for voltage

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## options
    max_iter = 400                 # deps on selection of stepsizes
    verbose = 1
    ## instead of using condition number as criteria for switching between
    ## modes...
    # # condNumThresh_Phase1 = 0.2e-2  # condition number shreshold for voltage prediction-correction (lmbda increasing)
    # # condNumThresh_Phase2 = 0.2e-2  # condition number shreshold for lmbda prediction-correction
    # # condNumThresh_Phase3 = 0.1e-5  # condition number shreshold for voltage prediction-correction in backward direction (lmbda decreasing)
    ## ...we use PV curve slopes as the criteria for switching modes
    slopeThresh_Phase1 = 0.5       # PV curve slope shreshold for voltage prediction-correction (with lmbda increasing)
    slopeThresh_Phase2 = 0.3       # PV curve slope shreshold for lmbda prediction-correction

    ## load the case & convert to internal bus numbering
    baseMVA, bus, gen, branch = loadcase(casedata)
    i2e, bus, gen, branch = ext2int(bus, gen, branch)
    e2i = zeros(max(i2e), 1)
    e2i[i2e] = range(bus.shape[0])
    loadvarloc_i = e2i[loadvarloc]

    ## get bus index lists of each type of bus
    ref, pv, pq = bustypes(bus, gen)

    ## generator info
    on = find(gen[:, GEN_STATUS] > 0)      ## which generators are on?
    gbus = gen[on, GEN_BUS]                ## what buses are they at?

    ## form Ybus matrix
    Ybus, Yf, Yt = makeYbus(baseMVA, bus, branch)

    ## set up indexing
    npv = len(pv)
    npq = len(pq)
    pv_bus = len(find(pv == loadvarloc_i)) > 0

    ## initialize parameters
    # set lmbda to be increasing
    flag_lmbdaIncrease = True  # flag indicating lmbda is increasing or decreasing
    if bus[loadvarloc_i, PD] == 0:
        initQPratio = 0
        print '\t[Warning]:\tLoad real power at bus %d is 0. Q/P ratio will be fixed at 0.\n' % loadvarloc
    else:
        initQPratio = bus[loadvarloc_i, QD] / bus[loadvarloc_i, PD]

    lmbda0 = 0
    lmbda = lmbda0
    Vm = ones(bus.shape[0])          ## flat start
    Va = bus(ref[0], VA) * Vm
    V  = Vm * exp(1j * pi/180 * Va)
    V[gbus] = gen[on, VG] / abs(V[gbus]) * V[gbus]

    pointCnt = 0

    ## do voltage correction (ie, power flow) to get initial voltage profile
    lmbda_predicted = lmbda
    V_predicted = V
    V, lmbda, success, iterNum = cpf_correctVoltage(baseMVA, bus, gen, Ybus, V_predicted, lmbda_predicted, initQPratio, loadvarloc_i)
    ## record data
    pointCnt = pointCnt + 1
    corrected_list[:, pointCnt] = Vlmbda

    ##------------------------------------------------
    ## do cpf prediction-correction iterations
    ##------------------------------------------------
    t0 = time()
    ## --- Start Phase 1: voltage prediction-correction (lmbda increasing)
    if verbose > 0:
        print 'Start Phase 1: voltage prediction-correction (lmbda increasing).\n'

    i = 0
    while i < max_iter:
        ## update iteration counter
        i = i + 1

        # save good data
        V_saved = copy(V)
        lmbda_saved = copy(lmbda)

        ## do voltage prediction to find predicted point (predicting voltage)
        V_predicted, lmbda_predicted, J = cpf_predict(Ybus, ref, pv, pq, V, lmbda, sigmaForlmbda, 1, initQPratio, loadvarloc, flag_lmbdaIncrease)

        ## do voltage correction to find corrected point
        V, lmbda, success, iterNum = cpf_correctVoltage(baseMVA, bus, gen, Ybus, V_predicted, lmbda_predicted, initQPratio, loadvarloc_i)

        ## calculate slope (dP/dlmbda) at current point
        slope = abs(V(loadvarloc_i) - V_saved(loadvarloc_i))/(lmbda - lmbda_saved)

        ## instead of using condition number as criteria for switching between
        ## modes...
        ##    if rcond(J) <= condNumThresh_Phase1 | success == false % Jacobian matrix is ill-conditioned, or correction step fails
        ## ...we use PV curve slopes as the criteria for switching modes
        if abs(slope) >= slopeThresh_Phase1 | success == false: # Approaching nose area of PV curve, or correction step fails
            # restore good data
            V = V_saved
            lmbda = lmbda_saved
            if verbose > 0:
                print '\t[Info]:\tApproaching nose area of PV curve, or voltage correction fails.\n'
            break
        else:
            if verbose > 2:
                print '\nVm_predicted\tVm_corrected\n'
                [[abs(V_predicted), lmbda_predicted], [abs(V), lmbda]]

            ## record data
            pointCnt = pointCnt + 1
            predicted_list[:, pointCnt-1] = [V_predicted, lmbda_predicted]
            corrected_list[:, pointCnt] = [Vlmbda]

    pointCnt_Phase1 = pointCnt # collect number of points obtained at this phase
    if verbose > 0:
        print '\t[Info]:\t%d data points contained in phase 1.\n' % pointCnt_Phase1

    ## --- Switch to Phase 2: lmbda prediction-correction (voltage decreasing)
    if verbose > 0:
        print 'Switch to Phase 2: lmbda prediction-correction (voltage decreasing).\n'

    k = 0
    while k < max_iter:
        ## update iteration counter
        k = k + 1

        # save good data
        V_saved = copy(V)
        lmbda_saved = copy(lmbda)

        ## do lmbda prediction to find predicted point (predicting lmbda)
        V_predicted, lmbda_predicted, J = cpf_predict(Ybus, ref, pv, pq, V, lmbda, sigmaForVoltage, 2, initQPratio, loadvarloc)
        ## do lmbda correction to find corrected point
        Vm_assigned = abs(V_predicted)
        V, lmbda, success, iterNum = cpf_correctlmbda(baseMVA, bus, gen, Ybus, Vm_assigned, V_predicted, lmbda_predicted, initQPratio, loadvarloc, ref, pv, pq)

        ## calculate slope (dP/dlmbda) at current point
        slope = abs(V(loadvarloc_i) - V_saved(loadvarloc_i)) / (lmbda - lmbda_saved)

        ## instead of using condition number as criteria for switching between
        ## modes...
        ##    if rcond(J) >= condNumThresh_Phase2 | success == false % Jacobian matrix is good-conditioned, or correction step fails
        ## ...we use PV curve slopes as the criteria for switching modes
        if abs(slope) <= slopeThresh_Phase2 | success == false: # Leaving nose area of PV curve, or correction step fails
            # restore good data
            V = copy(V_saved)
            lmbda = copy(lmbda_saved)

            ## ---change to voltage prediction-correction (lmbda decreasing)
            if verbose > 0:
                print '\t[Info]:\tLeaving nose area of PV curve, or lmbda correction fails.\n'
            break
        else:
            if verbose > 2:
                print '\nVm_predicted\tVm_corrected\n'
                [[abs(V_predicted), lmbda_predicted] [abs(V), lmbda]]

            ## record data
            pointCnt = pointCnt + 1
            predicted_list[:, pointCnt-1] = [V_predicted, lmbda_predicted]
            corrected_list[:, pointCnt] = [Vlmbda]

    pointCnt_Phase2 = pointCnt - pointCnt_Phase1 # collect number of points obtained at this phase
    if verbose > 0:
        print '\t[Info]:\t%d data points contained in phase 2.\n' % pointCnt_Phase2

    ## --- Switch to Phase 3: voltage prediction-correction (lmbda decreasing)
    if verbose > 0:
        print 'Switch to Phase 3: voltage prediction-correction (lmbda decreasing).\n'

    # set lmbda to be decreasing
    flag_lmbdaIncrease = False
    i = 0
    while i < max_iter:
        ## update iteration counter
        i = i + 1

        ## do voltage prediction to find predicted point (predicting voltage)
        V_predicted, lmbda_predicted, J = cpf_predict(Ybus, ref, pv, pq, V, lmbda, sigmaForlmbda, 1, initQPratio, loadvarloc, flag_lmbdaIncrease)

        ## do voltage correction to find corrected point
        V, lmbda, success, iterNum = cpf_correctVoltage(baseMVA, bus, gen, Ybus, V_predicted, lmbda_predicted, initQPratio, loadvarloc_i)

        ## calculate slope (dP/dlmbda) at current point
        slope = abs(V(loadvarloc_i) - V_saved(loadvarloc_i)) / (lmbda - lmbda_saved)

        if lmbda < 0: # lmbda is less than 0, then stops CPF simulation
            if verbose > 0:
                print '\t[Info]:\tlmbda is less than 0.\n\t\t\tCPF finished.\n'
            break

        ## instead of using condition number as criteria for switching between
        ## modes...
        ##    if rcond(J) <= condNumThresh_Phase3 | success == false % Jacobian matrix is ill-conditioned, or correction step fails
        ## ...we use PV curve slopes as the criteria for switching modes
        if success == False: # voltage correction step fails.
            if verbose > 0:
                print '\t[Info]:\tVoltage correction step fails..\n'
            break
        else:
            if verbose > 2:
                print '\nVm_predicted\tVm_corrected\n'
                [[abs(V_predicted), lmbda_predicted] [abs(V), lmbda]]

            ## record data
            pointCnt = pointCnt + 1
            predicted_list[:, pointCnt-1] = [V_predicted, lmbda_predicted]
            corrected_list[:, pointCnt] = [Vlmbda]

    pointCnt_Phase3 = pointCnt - pointCnt_Phase2 - pointCnt_Phase1 # collect number of points obtained at this phase
    if verbose > 0:
        print '\t[Info]:\t%d data points contained in phase 3.\n' % pointCnt_Phase3

    et = time() - t0

    ## combine the prediction and correction data in the sequence of appearance
    # NOTE: number of prediction data is one less than that of correction data
    predictedCnt = predicted_list.shape[1]
    combined_list[:, 0] = corrected_list[:, 0]
    for i in range(predictedCnt):
        combined_list[:, 2*i]     = predicted_list[:, i]
        combined_list[:, 2*i+1]   = corrected_list[:, i+1]

    ## convert back to original bus numbering & print results
    bus, gen, branch = int2ext(i2e, bus, gen, branch)

    ## add bus number as the first column to the prediction, correction, and combined data list
    nb          = bus.shape[0]
    max_lmbda  = max(corrected_list[nb+1, :])
    predicted_list = [[bus[:, BUS_I], 0] predicted_list]
    corrected_list = [[bus[:, BUS_I], 0] corrected_list]
    combined_list  = [[bus[:, BUS_I], 0] combined_list]

    if verbose > 1:
        Vm_corrected = abs(corrected_list)
        Vm_predicted = abs(predicted_list)
        Vm_combined  = abs(combined_list)
        Vm_corrected
        Vm_predicted
        Vm_combined
        pointCnt_Phase1
        pointCnt_Phase2
        pointCnt_Phase3
        pointCnt

    return max_lmbda, predicted_list, corrected_list, combined_list, success, et
