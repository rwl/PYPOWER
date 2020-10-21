"""Runs a full AC continuation power flow.
"""

from sys import stdout, stderr

from os.path import dirname, join

from time import time

from numpy import c_, r_, ix_, zeros, pi, ones, exp, linalg, angle, inf, nan, full
from numpy import flatnonzero as find

from pypower.bustypes import bustypes
from pypower.ext2int import ext2int
from pypower.loadcase import loadcase
from pypower.makeSbus import makeSbus
from pypower.makeYbus import makeYbus
from pypower.newtonpf import newtonpf
from pypower.ppoption import ppoption
from pypower.ppver import ppver
from pypower.cpf_predictor import cpf_predictor
from pypower.cpf_corrector import cpf_corrector
from pypower.pfsoln import pfsoln
from pypower.i2e_data import i2e_data
from pypower.int2ext import int2ext
from pypower.printpf import printpf
from pypower.savecase import savecase

from pypower.idx_bus import VM, VA, PD, QD
from pypower.idx_brch import PF, PT, QF, QT
from pypower.idx_gen import PG, QG, VG, GEN_BUS, GEN_STATUS

import pypower.cpf_callbacks as cpf_callbacks


def runcpf(basecasedata=None, targetcasedata=None, ppopt=None, fname='', solvedcase=''):

    # default arguments
    if basecasedata is None:
        basecasedata = join(dirname(__file__), 'case9')
    if targetcasedata is None:
        targetcasedata = join(dirname(__file__), 'case9target')
    ppopt = ppoption(ppopt)

    # options
    verbose = ppopt["VERBOSE"]
    step = ppopt["CPF_STEP"]
    parameterization = ppopt["CPF_PARAMETERIZATION"]
    adapt_step = ppopt["CPF_ADAPT_STEP"]
    cb_args = ppopt["CPF_USER_CALLBACK_ARGS"]

    # set up callbacks
    callback_names = ["cpf_default_callback"]
    if len(ppopt["CPF_USER_CALLBACK"]) > 0:
        if isinstance(ppopt["CPF_USER_CALLBACK"], list):
            callback_names = r_[callback_names, ppopt["CPF_USER_CALLBACK"]]
        else:
            callback_names.append(ppopt["CPF_USER_CALLBACK"])
    callbacks = []
    for callback_name in callback_names:
        callbacks.append(getattr(cpf_callbacks, callback_name))

    # read base case data
    ppcbase = loadcase(basecasedata)
    nb = ppcbase["bus"].shape[0]

    # add zero columns to branch for flows if needed
    if ppcbase["branch"].shape[1] < QT:
        ppcbase["branch"] = c_[ppcbase["branch"],
                               zeros((ppcbase["branch"].shape[0],
                                      QT - ppcbase["branch"].shape[1] + 1))]

    # convert to internal indexing
    ppcbase = ext2int(ppcbase)
    baseMVAb, busb, genb, branchb = \
        ppcbase["baseMVA"], ppcbase["bus"], ppcbase["gen"], ppcbase["branch"]

    # get bus index lists of each type of bus
    ref, pv, pq = bustypes(busb, genb)

    # generator info
    onb = find(genb[:, GEN_STATUS] > 0)  # which generators are on?
    gbusb = genb[onb, GEN_BUS].astype(int)  # what buses are they at?

    # read target case data
    ppctarget = loadcase(targetcasedata)

    # add zero columns to branch for flows if needed
    if ppctarget["branch"].shape[1] < QT:
        ppctarget["branch"] = c_[ppctarget["branch"],
                                 zeros((ppctarget["branch"].shape[0],
                                        QT - ppctarget["branch"].shape[1] + 1))]

    # convert to internal indexing
    ppctarget = ext2int(ppctarget)
    baseMVAt, bust, gent, brancht = \
        ppctarget["baseMVA"], ppctarget["bus"], ppctarget["gen"], ppctarget["branch"]

    # get bus index lists of each type of bus
    # ref, pv, pq = bustypes(bust, gent)

    # generator info
    ont = find(gent[:, GEN_STATUS] > 0)  # which generators are on?
    # gbust = gent[ont, GEN_BUS].astype(int)  # what buses are they at?

    # -----  run the power flow  -----
    t0 = time()
    if verbose > 0:
        v = ppver('all')
        stdout.write('PYPOWER Version %s, %s' % (v["Version"], v["Date"]))
        stdout.write(' -- AC Continuation Power Flow\n')

    # initial state
    # V0    = ones(bus.shape[0])            ## flat start
    V0 = busb[:, VM] * exp(1j * pi/180 * busb[:, VA])
    vcb = ones(V0.shape)    # create mask of voltage-controlled buses
    vcb[pq] = 0     # exclude PQ buses
    k = find(vcb[gbusb])    # in-service gens at v-c buses
    V0[gbusb[k]] = genb[onb[k], VG] / abs(V0[gbusb[k]]) * V0[gbusb[k]]

    # build admittance matrices
    Ybus, Yf, Yt = makeYbus(baseMVAb, busb, branchb)

    # compute base case complex bus power injections (generation - load)
    Sbusb = makeSbus(baseMVAb, busb, genb)
    # compute target case complex bus power injections (generation - load)
    Sbust = makeSbus(baseMVAt, bust, gent)

    # scheduled transfer
    Sxfr = Sbust - Sbusb

    # Run the base case power flow solution
    if verbose > 2:
        ppopt_pf = ppoption(ppopt, VERBOSE=max(0, verbose-1))
    else:
        ppopt_pf = ppoption(ppopt, VERBOSE=max(0, verbose-2))

    lam = 0
    V, success, iterations = newtonpf(Ybus, Sbusb, V0, ref, pv, pq, ppopt_pf)
    if verbose > 2:
        print('step %3d : lambda = %6.3f\n' % (0, 0))
    elif verbose > 1:
        print('step %3d : lambda = %6.3f, %2d Newton steps\n' % (0, 0, iterations))

    lamprv = lam    # lam at previous step
    Vprv = V    # V at previous step
    continuation = 1
    cont_steps = 0

    # input args for callbacks
    cb_data = {
        "ppc_base": ppcbase,
        "ppc_target": ppctarget,
        "Sxfr": Sxfr,
        "Ybus": Ybus,
        "Yf": Yf,
        "Yt": Yt,
        "ref": ref,
        "pv": pv,
        "pq": pq,
        "ppopt": ppopt
    }
    cb_state = {}

    # invoke callbacks
    for k in range(len(callbacks)):
        cb_state, _ = callbacks[k](cont_steps, V, lam, V, lam,
                                   cb_data, cb_state, cb_args)

    if linalg.norm(Sxfr) == 0:
        if verbose:
            print('base case and target case have identical load and generation\n')

        continuation = 0
        V0 = V
        lam0 = lam

    # tangent predictor z = [dx;dlam]
    z = zeros(2*len(V)+1)
    z[-1] = 1.0
    while continuation:
        cont_steps = cont_steps + 1
        # prediction for next step
        V0, lam0, z = cpf_predictor(V, lam, Ybus, Sxfr, pv, pq, step, z,
                                    Vprv, lamprv, parameterization)

        # save previous voltage, lambda before updating
        Vprv = V
        lamprv = lam

        # correction
        V, success, i, lam = cpf_corrector(Ybus, Sbusb, V0, ref, pv, pq,
                                           lam0, Sxfr, Vprv, lamprv, z, step, parameterization, ppopt_pf)

        if not success:
            continuation = 0
            if verbose:
                print('step %3d : lambda = %6.3f, corrector did not converge in %d iterations\n' % (
                    cont_steps, lam, i))
            break

        if verbose > 2:
            print('step %3d : lambda = %6.3f\n' % (cont_steps, lam))
        elif verbose > 1:
            print('step %3d : lambda = %6.3f, %2d corrector Newton steps\n' %
                  (cont_steps, lam, i))

        # invoke callbacks
        for k in range(len(callbacks)):
            cb_state, _ = callbacks[k](cont_steps, V, lam, V0, lam0,
                                       cb_data, cb_state, cb_args)

        if isinstance(ppopt["CPF_STOP_AT"], str):
            if ppopt["CPF_STOP_AT"].upper() == "FULL":
                if abs(lam) < 1e-8:     # traced the full continuation curve
                    if verbose:
                        print(
                            '\nTraced full continuation curve in %d continuation steps\n' % cont_steps)
                    continuation = 0
                elif lam < lamprv and lam - step < 0:    # next step will overshoot
                    step = lam      # modify step-size
                    parameterization = 1    # change to natural parameterization
                    adapt_step = False      # disable step-adaptivity

            else:   # == 'NOSE'
                if lam < lamprv:    # reached the nose point
                    if verbose:
                        print(
                            '\nReached steady state loading limit in %d continuation steps\n' % cont_steps)
                    continuation = 0

        else:
            if lam < lamprv:
                if verbose:
                    print(
                        '\nReached steady state loading limit in %d continuation steps\n' % cont_steps)
                continuation = 0
            elif abs(ppopt["CPF_STOP_AT"] - lam) < 1e-8:     # reached desired lambda
                if verbose:
                    print('\nReached desired lambda %3.2f in %d continuation steps\n' % (
                        ppopt["CPF_STOP_AT"], cont_steps))
                continuation = 0
            # will reach desired lambda in next step
            elif lam + step > ppopt["CPF_STOP_AT"]:
                step = ppopt["CPF_STOP_AT"] - lam   # modify step-size
                parameterization = 1    # change to natural parameterization
                adapt_step = False      # disable step-adaptivity

        if adapt_step and continuation:
            pvpq = r_[pv, pq]
            # Adapt stepsize
            cpf_error = linalg.norm(r_[angle(V[pq]), abs(
                V[pvpq]), lam] - r_[angle(V0[pq]), abs(V0[pvpq]), lam0], inf)
            if cpf_error < ppopt["CPF_ERROR_TOL"]:
                # Increase stepsize
                step = step * ppopt["CPF_ERROR_TOL"] / cpf_error
                if step > ppopt["CPF_STEP_MAX"]:
                    step = ppopt["CPF_STEP_MAX"]
            else:
                # decrese stepsize
                step = step * ppopt["CPF_ERROR_TOL"] / cpf_error
                if step < ppopt["CPF_STEP_MIN"]:
                    step = ppopt["CPF_STEP_MIN"]

    # invoke callbacks
    if success:
        cpf_results = {}
        for k in range(len(callbacks)):
            cb_state, cpf_results = callbacks[k](cont_steps, V, lam, V0, lam0,
                                                 cb_data, cb_state, cb_args, results=cpf_results, is_final=True)
    else:
        cpf_results = {}
        cpf_results["iterations"] = i

    # update bus and gen matrices to reflect the loading and generation
    # at the noise point
    bust[:, PD] = busb[:, PD] + lam * (bust[:, PD] - busb[:, PD])
    bust[:, QD] = busb[:, QD] + lam * (bust[:, QD] - busb[:, QD])
    gent[:, PG] = genb[:, PG] + lam * (gent[:, PG] - genb[:, PG])

    # update data matrices with solution
    bust, gent, brancht = pfsoln(
        baseMVAt, bust, gent, brancht, Ybus, Yf, Yt, V, ref, pv, pq)

    ppctarget["et"] = time() - t0
    ppctarget["success"] = success

    # -----  output results  -----
    # convert back to original bus numbering & print results
    ppctarget["bus"], ppctarget["gen"], ppctarget["branch"] = bust, gent, brancht
    if success:
        n = cpf_results["iterations"] + 1
        cpf_results["V_p"] = i2e_data(
            ppctarget, cpf_results["V_p"], full((nb, n), nan), "bus", 0)
        cpf_results["V_c"] = i2e_data(
            ppctarget, cpf_results["V_c"], full((nb, n), nan), "bus", 0)
    results = int2ext(ppctarget)
    results["cpf"] = cpf_results

    # zero out result fields of out-of-service gens & branches
    if len(results["order"]["gen"]["status"]["off"]) > 0:
        results["gen"][ix_(results["order"]["gen"]
                           ["status"]["off"], [PG, QG])] = 0

    if len(results["order"]["branch"]["status"]["off"]) > 0:
        results["branch"][ix_(results["order"]["branch"]
                              ["status"]["off"], [PF, QF, PT, QT])] = 0

    if fname:
        fd = None
        try:
            fd = open(fname, "a")
        except Exception as detail:
            stderr.write("Error opening %s: %s.\n" % (fname, detail))
        finally:
            if fd is not None:
                printpf(results, fd, ppopt)
                fd.close()
    else:
        printpf(results, stdout, ppopt)

    # save solved case
    if solvedcase:
        savecase(solvedcase, results)

    if ppopt["CPF_PLOT_LEVEL"]:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            stderr.write(
                "Error: Please install \"Matpotlib\" package for plotting function!\n")
        
        plt.show()

    return results, success


if __name__ == '__main__':
    runcpf()
