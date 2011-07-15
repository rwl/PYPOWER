# Copyright (C) 2009-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

"""Runs the userfcn callbacks for a given stage.
"""

from pypower.util import feval


def run_userfcn(userfcn, stage, *args):
    """Runs the userfcn callbacks for a given stage.

    Example::
        ppc = om.get_mpc()
        om = run_userfcn(ppc['userfcn'], 'formulation', om)

    @param userfcn: the 'userfcn' field of ppc, populated by L{add_userfcn}
    @param stage: the name of the callback stage begin executed
    (additional arguments) some stages require additional arguments.

    @see: L{add_userfcn}, L{remove_userfcn}, L{toggle_reserves},
          L{toggle_iflims}, L{runopf_w_res}.
    """
    rv = args[0]
    if (len(userfcn) > 0) and (stage in userfcn):
        for k in range(len(userfcn[stage])):
            if 'args' in userfcn[stage][k]:
                args = userfcn[stage][k]['args']
            else:
                args = []

            if stage in ['ext2int', 'formulation', 'int2ext']:
                # ppc     = userfcn_*_ext2int(ppc, args)
                # om      = userfcn_*_formulation(om, args)
                # results = userfcn_*_int2ext(results, args)
                rv = userfcn[stage][k]['fcn'](rv, args)
            elif stage in ['printpf', 'savecase']:
                # results = userfcn_*_printpf(results, fd, ppopt, args)
                # ppc     = userfcn_*_savecase(mpc, fd, prefix, args)
                rv = feval(userfcn[stage][k]['fcn'], rv, args[1], args[2], args)

    return rv
