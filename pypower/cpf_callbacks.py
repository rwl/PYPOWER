"""Callback functions for CPF
"""

from numpy import c_, amax


def cpf_default_callback(k, V_c, lam_c, V_p, lam_p, cb_data, cb_state, cb_args, results=None, is_final=False):
    """Default callback function for CPF
    """

    # initialize plotting options
    pass

    # -----  FINAL call  -----
    if is_final:
        # assemble results struct
        results = cb_state
        results["max_lam"] = amax(cb_state["lam_c"])
        results["iterations"] = k

        # finish final lambda-V nose curve plot
        pass

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
        pass

    # -----  ITERATION call  -----
    else:
        # update state
        cb_state["V_p"] = c_[cb_state["V_p"], V_p]
        cb_state["lam_p"] = c_[cb_state["lam_p"], lam_p]
        cb_state["V_c"] = c_[cb_state["V_c"], V_c]
        cb_state["lam_c"] = c_[cb_state["lam_c"], lam_c]
        cb_state["iterations"] = k

        # plot single step of the lambda-V nose curve
        pass

    return cb_state, results
