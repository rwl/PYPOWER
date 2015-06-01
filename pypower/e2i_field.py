# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Converts fields of ppc from external to internal indexing.
"""
from pypower._compat import PY2
from pypower.e2i_data import e2i_data  #@UnusedImport


if not PY2:
    basestring = str


def e2i_field(ppc, field, ordering, dim=0):
    """Converts fields of C{ppc} from external to internal indexing.

    This function performs several different tasks, depending on the
    arguments passed.

    When given a case dict that has already been converted to
    internal indexing, this function can be used to convert other data
    structures as well by passing in 2 or 3 extra parameters in
    addition to the case dict.

    The 2nd argument is a string or list of strings, specifying
    a field in the case dict whose value should be converted by
    a corresponding call to L{e2i_data}. In this case, the converted value
    is stored back in the specified field, the original value is
    saved for later use and the updated case dict is returned.
    If C{field} is a list of strings, they specify nested fields.

    The 3rd and optional 4th arguments are simply passed along to
    the call to L{e2i_data}.

    Examples:
        ppc = e2i_field(ppc, ['reserves', 'cost'], 'gen')

        Reorders rows of ppc['reserves']['cost'] to match internal generator
        ordering.

        ppc = e2i_field(ppc, ['reserves', 'zones'], 'gen', 1)

        Reorders columns of ppc['reserves']['zones'] to match internal
        generator ordering.

    @see: L{i2e_field}, L{e2i_data}, L{ext2int}
    """
    if isinstance(field, basestring):
        key = '["%s"]' % field
    else:
        key = '["%s"]' % '"]["'.join(field)

        v_ext = ppc["order"]["ext"]
        for fld in field:
            if fld not in v_ext:
                v_ext[fld] = {}
                v_ext = v_ext[fld]

    exec('ppc["order"]["ext"]%s = ppc%s.copy()' % (key, key))
    exec('ppc%s = e2i_data(ppc, ppc%s, ordering, dim)' % (key, key))

    return ppc
