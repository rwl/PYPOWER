# Copyright (C) 2011 Richard Lincoln
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

from optparse import OptionParser, OptionGroup, OptionValueError

from pypower.ppver import ppver
from pypower.ppoption import ppoption, PF_OPTIONS, OPF_OPTIONS, OUTPUT_OPTIONS

TYPE_MAP = {bool: 'choice', float: 'float', int: 'int'}

AFFIRMATIVE = ('True', 'Yes', 'true', 'yes', '1', 'Y', 'y')
NEGATIVE = ('False', 'No', 'false', 'no', '0', 'N', 'n')


def option_callback(option, opt, value, parser, *args, **kw_args):
    if isinstance(value, str):
        if value in AFFIRMATIVE:
            value = True
        elif value in NEGATIVE:
            value = False
        else:
            choices = ", ".join(map(repr, option.choices))
            raise OptionValueError(
                _("option %s: invalid choice: %r (choose from %s)")
                % (opt, value, choices))

    opt_name = opt[2:].upper()

    ppopt = args[0]
    ppopt[opt_name] = value


def add_options(group, options, *callback_args, **callback_kwargs):
    for name, default_val, help in options:
        long_opt = '--%s' % name

        kw_args = {
            'default': default_val,
            'help': '%s [default: %%default]' % help,
            'type': TYPE_MAP.get(type(default_val), 'string'),
            'action': "callback",
            'callback': option_callback,
            'callback_args': callback_args,
            'callback_kwargs': callback_kwargs
        }

        if isinstance(default_val, bool):
            kw_args['choices'] = AFFIRMATIVE + NEGATIVE

        group.add_option(long_opt, **kw_args)


def main():
    ppopt = ppoption()

    parser = OptionParser(usage='usage: %prog [options]',
                          version='%%prog %s' % (ppver()['Version']))

    pf_options = OptionGroup(parser, "Power Flow Options")
    opf_options = OptionGroup(parser, "OPF Options")
    output_options = OptionGroup(parser, "Output Options")

    add_options(pf_options, PF_OPTIONS, ppopt)
    add_options(opf_options, OPF_OPTIONS, ppopt)
    add_options(output_options, OUTPUT_OPTIONS, ppopt)

    parser.add_option_group(pf_options)
    parser.add_option_group(opf_options)
    parser.add_option_group(output_options)

    parser.print_help()


    ags = ["--verbose=2", '--pf_tol=1e-6', '--out_all=0', "--pf_dc=true"]

    options, args = parser.parse_args(ags)

    print ppopt['VERBOSE'], ppopt['PF_TOL'], ppopt['OUT_ALL'], ppopt['PF_DC']


if __name__ == '__main__':
    main()