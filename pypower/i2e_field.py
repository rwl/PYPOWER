# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from pypower.i2e_data import i2e_data  #@UnusedImport


def i2e_field(ppc, field, ordering, dim=0):
    """Converts fields of MPC from internal to external bus numbering.

    For a case dict using internal indexing, this function can be
    used to convert other data structures as well by passing in 2 or 3
    extra parameters in addition to the case dict.

    If the 2nd argument is a string or list of strings, it
    specifies a field in the case dict whose value should be
    converted by L{i2e_data}. In this case, the corresponding
    C{oldval} is taken from where it was stored by L{ext2int} in
    ppc['order']['ext'] and the updated case dict is returned.
    If C{field} is a list of strings, they specify nested fields.

    The 3rd and optional 4th arguments are simply passed along to
    the call to L{i2e_data}.

    Examples:
        ppc = i2e_field(ppc, ['reserves', 'cost'], 'gen')

        Reorders rows of ppc['reserves']['cost'] to match external generator
        ordering.

        ppc = i2e_field(ppc, ['reserves', 'zones'], 'gen', 1)

        Reorders columns of ppc.reserves.zones to match external
        generator ordering.

    @see: L{e2i_field}, L{i2e_data}, L{int2ext}.
    """
    if 'int' not in ppc['order']:
        ppc['order']['int'] = {}

    if isinstance(field, str):
        key = '["%s"]' % field
    else:  # nested dicts
        key = '["%s"]' % '"]["'.join(field)

        v_int = ppc["order"]["int"]
        for fld in field:
            if fld not in v_int:
                v_int[fld] = {}
                v_int = v_int[fld]

    exec('ppc["order"]["int"]%s = ppc%s.copy()' % (key, key))
    exec('ppc%s = i2e_data(ppc, ppc%s, ppc["order"]["ext"]%s, ordering, dim)' %
         (key, key, key))

    return ppc
