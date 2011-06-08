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

import sys

from os.path import dirname, join

from optparse import OptionParser, OptionGroup, OptionValueError

from pypower.ppver import ppver
from pypower.ppoption import ppoption, PF_OPTIONS, OPF_OPTIONS, OUTPUT_OPTIONS
from pypower.runpf import runpf
from pypower.runopf import runopf
from pypower.runuopf import runuopf

TYPE_MAP = {bool: 'choice', float: 'float', int: 'int'}

AFFIRMATIVE = ('True', 'Yes', 'true', 'yes', '1', 'Y', 'y')
NEGATIVE = ('False', 'No', 'false', 'no', '0', 'N', 'n')

CASES = ('case4gs', 'case6ww', 'case9', 'case9Q', 'case14', 'case24_ieee_rts',
    'case30', 'case30Q', 'case30pwl', 'case39', 'case57', 'case118', 'case300')

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

    parser = OptionParser(usage='usage: %prog [options] [casefile]',
                          version='%%prog %s' % (ppver()['Version']))

    parser.add_option('-t', '--type',
            type='choice',
            choices=('pf', 'opf', 'udopf'),
            default='pf',
            metavar="PROBLEM_TYPE",
            help='Power flow is run by default. '
            'To run an optimal power flow set this option to "opf" '
            'or to "udopf" to solve using the unit-decommitment heuristic.')

    parser.add_option('-c', '--casedata',
            default=CASES[2],
            type='choice',
            choices=CASES,
            metavar="CASEDATA",
            help='Built-in case to solve. Ignored if casefile is specified. ('
            +', '.join(CASES)
            +') [default: %default]')

    parser.add_option('--fname',
            metavar="FNAME",
            default='',
            help='If FNAME is specified the pretty printed output will be '
            'appended to the file with the specified name, otherwise the '
            'output is written to stdout.')

    parser.add_option('--solvedcase',
            metavar="SOLVEDCASE",
            default='',
            help='If SOLVEDCASE is specified the solved case will be written '
            'to a case file in PYPOWER format with the specified name. If '
            'SOLVEDCASE ends with \'.mat\' the case is saved as a MAT-file '
            'otherwise it saves it as a Python file.')

    pf_options = OptionGroup(parser, "Power Flow Options")
    opf_options = OptionGroup(parser, "OPF Options")
    output_options = OptionGroup(parser, "Output Options")

    add_options(pf_options, PF_OPTIONS, ppopt)
    add_options(opf_options, OPF_OPTIONS, ppopt)
    add_options(output_options, OUTPUT_OPTIONS, ppopt)

    parser.add_option_group(pf_options)
    parser.add_option_group(opf_options)
    parser.add_option_group(output_options)

    options, args = parser.parse_args()

    if len(args) == 0:
#        casedata = join(dirname(__file__), options.casedata)
        casedata = options.casedata
    elif len(args) == 1:
        casedata = args[0]
    else:
        sys.stderr.write('too many arguments')
        parser.print_help()
        return 2

    fname = options.fname
    solvedcase = options.solvedcase

    if options.type == 'pf':
        _, success = runpf(casedata, ppopt, fname, solvedcase)
    elif options.type == 'opf':
        _, success = runopf(casedata, ppopt, fname, solvedcase)
    elif options.type == 'udopf':
        _, success = runuopf(casedata, ppopt, fname, solvedcase)
    else:
        raise OptionValueError

    return 0 if success else 2


if __name__ == '__main__':
    sys.exit(main())
