# Copyright (C) 2010-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
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
