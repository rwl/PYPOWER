"""Callback functions for CPF
"""

from numpy import c_, r_, amax, argmax, array
from scipy.sparse import issparse

import sys
import os


def cpf_default_callback(k, V_c, lam_c, V_p, lam_p, cb_data, cb_state, cb_args, results=None, is_final=False):
    """Default callback function for CPF
    """

    # initialize plotting options
    plot_level = cb_data["ppopt"]["CPF_PLOT_LEVEL"]
    plot_bus = cb_data["ppopt"]["CPF_PLOT_BUS"]

    if plot_level:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            sys.stderr.write(
                "Error: Please install \"Matpotlib\" package for plotting function!\n")

        if plot_bus == '':  # no bus specified
            if len(cb_data["Sxfr"][cb_data["pq"]]) != 0:
                idx = argmax(abs(cb_data["Sxfr"][cb_data["pq"]]), axis=0)
                idx = cb_data["pq"][idx]
            else:   # or bus 1 if there are none
                idx = 0
            idx_e = int(cb_data["ppc_target"]["order"]["bus"]["i2e"][idx])

        else:
            idx_e = plot_bus
            if issparse(cb_data["ppc_target"]["order"]["bus"]["e2i"][idx_e]):
                idx = int(cb_data["ppc_target"]["order"]
                          ["bus"]["e2i"][idx_e].toarray())
            else:
                idx = int(cb_data["ppc_target"]["order"]["bus"]["e2i"][idx_e])

            if idx == 0:
                sys.stderr.write(
                    "cpf_default_callback: %d is not a valid bus number for PPOPT[\"CPF_PLOT_BUS\"]\n" % idx_e)

    # -----  FINAL call  -----
    if is_final:
        # assemble results struct
        results = cb_state
        results["max_lam"] = amax(cb_state["lam_c"])
        results["iterations"] = k

        # finish final lambda-V nose curve plot
        if plot_level:
            plt.plot(cb_state["lam_c"],
                     abs(cb_state["V_c"][idx, :]), '-', color=(0.25, 0.25, 1))
            plt.axis([0, amax([1, amax(cb_state["lam_p"]), amax(cb_state["lam_c"])])*1.05, 0,
                      amax([1, amax(abs(cb_state["V_p"][idx])), amax(abs(cb_state["V_c"][idx]))*1.05])])
            plt.pause(sys.float_info.epsilon)
            plt.ioff()

    elif k == 0:
        # initialize state
        cb_state = {
            "V_p": V_p,
            "lam_p": lam_p,
            "V_c": V_c,
            "lam_c": lam_c,
            "iterations": 0
        }

        # initialize lambda-V nose curve plot
        if plot_level:
            plt.ion()
            plt.plot(cb_state["lam_p"],
                     abs(cb_state["V_p"][idx]), '-', color=(0.25, 0.25, 1))
            plt.title('Voltage at Bus %d' % idx_e)
            plt.xlabel('$\\lambda$')
            plt.ylabel('Voltage Magnitude')
            plt.axis([0, amax([1, amax(cb_state["lam_p"]), amax(cb_state["lam_c"])])*1.05, 0,
                      amax([1, amax(abs(cb_state["V_p"][idx])), amax(abs(cb_state["V_c"][idx]))*1.05])])
            plt.pause(sys.float_info.epsilon)

    # -----  ITERATION call  -----
    else:
        # update state
        cb_state["V_p"] = c_[cb_state["V_p"], V_p]
        cb_state["lam_p"] = r_[cb_state["lam_p"], lam_p]
        cb_state["V_c"] = c_[cb_state["V_c"], V_c]
        cb_state["lam_c"] = r_[cb_state["lam_c"], lam_c]
        cb_state["iterations"] = k

        # plot single step of the lambda-V nose curve
        if plot_level > 1:
            plt.plot(r_[cb_state["lam_c"][k-1], cb_state["lam_p"][k]],
                     r_[abs(cb_state["V_c"][idx, k-1]),
                        abs(cb_state["V_p"][idx, k])],
                     '-', color=0.85*array([1, 0.75, 0.75]))
            plt.plot(r_[cb_state["lam_p"][k], cb_state["lam_c"][k]],
                     r_[abs(cb_state["V_p"][idx, k]),
                        abs(cb_state["V_c"][idx, k])],
                     '-', color=0.85*array([0.75, 1, 0.75]))
            plt.plot(cb_state["lam_p"][k], abs(cb_state["V_p"][idx, k]),
                     'x', color=0.85*array([1, 0.75, 0.75]))
            plt.plot(cb_state["lam_c"][k], abs(
                cb_state["V_c"][idx, k]), '-o', markerfacecolor='none', color=(0.25, 0.25, 1))
            plt.axis([0, amax([1, amax(cb_state["lam_p"]), amax(cb_state["lam_c"])])*1.05, 0,
                      amax([1, amax(abs(cb_state["V_p"][idx])), amax(abs(cb_state["V_c"][idx]))*1.05])])
            plt.pause(sys.float_info.epsilon)
            
        if plot_level > 2:
            os.system("pause")

    return cb_state, results
