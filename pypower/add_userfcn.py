# Copyright (C) 2009-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
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

from sys import stderr


def add_userfcn(ppc, stage, fcn, args=None, allow_multiple=False):
    """Appends a userfcn to the list to be called for a case.

    A userfcn is a callback function that can be called automatically by
    PYPOWER at one of various stages in a simulation.

    PPC   : the case dict
    STAGE : the name of the stage at which this function should be
            called: ext2int, formulation, int2ext, printpf
    FCN   : the name of the userfcn
    ARGS  : (optional) the value to be passed as an argument to the
            userfcn (typically a struct)
    ALLOW_MULTIPLE : (optional) if TRUE, allows the same function to
           be added more than once.

    Currently there are 5 different callback stages defined. Each stage has
    a name, and by convention, the name of a user-defined callback function
    ends with the name of the stage. The following is a description of each
    stage, when it is called and the input and output arguments which vary
    depending on the stage. The reserves example (see RUNOPF_W_RES) is used
    to illustrate how these callback userfcns might be used.

    1. ext2int

    Called from EXT2INT immediately after the case is converted from
    external to internal indexing. Inputs are a PYPOWER case dict (MPC),
    freshly converted to internal indexing and any (optional) ARGS value
    supplied via ADD_USERFCN. Output is the (presumably updated) MPC. This is
    typically used to reorder any input arguments that may be needed in
    internal ordering by the formulation stage.

    E.g. ppc = userfcn_reserves_ext2int(ppc, args)

    2. formulation

    Called from OPF after the OPF Model (OM) object has been initialized
    with the standard OPF formulation, but before calling the solver. Inputs
    are the OM object and any (optional) ARGS supplied via ADD_USERFCN.
    Output is the OM object. This is the ideal place to add any additional
    vars, constraints or costs to the OPF formulation.

    E.g. om = userfcn_reserves_formulation(om, args)

    3. int2ext

    Called from INT2EXT immediately before the resulting case is converted
    from internal back to external indexing. Inputs are the RESULTS struct
    and any (optional) ARGS supplied via ADD_USERFCN. Output is the RESULTS
    struct. This is typically used to convert any results to external
    indexing and populate any corresponding fields in the RESULTS struct.

    E.g. results = userfcn_reserves_int2ext(results, args)

    4. printpf

    Called from PRINTPF after the pretty-printing of the standard OPF
    output. Inputs are the RESULTS struct, the file descriptor to write to,
    a MATPOWER options vector, and any (optional) ARGS supplied via
    ADD_USERFCN. Output is the RESULTS struct. This is typically used for
    any additional pretty-printing of results.

    E.g. results = userfcn_reserves_printpf(results, fd, ppopt, args)

    5. savecase

    Called from SAVECASE when saving a case struct to an M-file after
    printing all of the other data to the file. Inputs are the case struct,
    the file descriptor to write to, the variable prefix (typically 'ppc.')
    and any (optional) ARGS supplied via ADD_USERFCN. Output is the case
    struct. This is typically used to write any non-standard case struct
    fields to the case file.

    E.g. ppc = userfcn_reserves_printpf(ppc, fd, prefix, args)

    @see: C{run_userfcn}, C{remove_userfcn}, C{toogle_reserves},
          C{toggle_iflims}, C{runopf_w_res}.
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    if args is None:
        args = []

    if stage not in ['ext2int', 'formulation', 'int2ext', 'printpf', 'savecase']:
        stderr.write('add_userfcn : \'%s\' is not the name of a valid callback stage\n' % stage)

    n = 0
    if 'userfcn' in ppc:
        if stage in ppc['userfcn']:
            n = len(ppc['userfcn'][stage]) + 1
            if not allow_multiple:
                for k in range(n - 1):
                    if ppc['userfcn'][stage][k]['fcn'] == fcn:
                        stderr.write('add_userfcn: the function \'%s\' has already been added\n' % fcn.func_name)

    ppc['userfcn'][stage][n]['fcn'] = fcn
    if len(args) > 0:
        ppc['userfcn'][stage][n]['args'] = args

    return ppc
