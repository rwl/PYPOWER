# Copyright (C) 2011 Richard Lincoln
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

"""Main entry-points for PYPOWER.
"""

import sys
from sys import stderr

from os.path import dirname, join

from optparse import OptionParser, OptionGroup, OptionValueError

from pypower.api import \
    ppver, ppoption, runpf, runopf, runuopf

from pypower.ppoption import \
    PF_OPTIONS, OPF_OPTIONS, OUTPUT_OPTIONS

from pypower.t.test_pypower import test_pf, test_opf


TYPE_MAP = {bool: 'choice', float: 'float', int: 'int'}

AFFIRMATIVE = ('True', 'Yes', 'true', 'yes', '1', 'Y', 'y')
NEGATIVE = ('False', 'No', 'false', 'no', '0', 'N', 'n')

CASES = ['case4gs', 'case6ww', 'case9', 'case9Q', 'case14', 'case30',
         'case30Q', 'case30pwl', 'case39', 'case57', 'case118', 'case300']


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


def parse_options(args, usage, opf=False):
    """Parse command line options.

    @param opf: Include OPF options?
    """
    v = ppver('all')
    parser = OptionParser(
        usage="""usage: %%prog [options] [casedata]

%s

If 'casedata' is provided it specifies the name of the input data file
containing the case data.""" % usage,
        version='PYPOWER (%%prog) Version %s, %s' % (v["Version"], v["Date"])
    )

    parser.add_option("-t", "--test", action="store_true", dest="test",
        default=False, help="run tests and exit")

    parser.add_option("-c", "--testcase", default='case9', choices=CASES,
        help="built-in test case, choose from: %s" % str(CASES[1:-1]))

    parser.add_option("-o", "--outfile", dest='fname', default='',
        type='string', help="""pretty printed output will be
appended to a file with the name specified. Defaults to stdout.""")

    parser.add_option("-s", "--solvedcase", default='', type='string',
        help="""the solved case will be written
to a case file with the specified name in PYPOWER format. If solvedcase ends
with '.mat' the case is saves  as a MAT-file otherwise it saves it as a Python
file.""")

    ppopt = ppoption()

    if opf:
        opf_options = OptionGroup(parser, 'OPF Options')

        opf_options.add_option("-u", "--uopf", action="store_true",
            help="""runs an optimal power flow with the unit-decommitment
heuristic""")

        add_options(opf_options, OPF_OPTIONS, ppopt)

        parser.add_option_group(opf_options)
    else:
        pf_options = OptionGroup(parser, 'Power Flow Options')

        add_options(pf_options, PF_OPTIONS, ppopt)

        parser.add_option_group(pf_options)

    output_options = OptionGroup(parser, 'Output Options')

    add_options(output_options, OUTPUT_OPTIONS, ppopt)

    parser.add_option_group(output_options)


    options, args = parser.parse_args(args)

#    casedata, fname, solvedcase = case9(), '', ''  # defaults

    nargs = len(args)
    if nargs > 1:
        stderr.write('Too many arguments')
        parser.print_help()
        sys.exit(2)
    elif nargs == 1:
        casedata = args[0]
    else:
        casedata = join(dirname(__file__), options.testcase)

    return options, casedata, ppopt, options.fname, options.solvedcase


def exit(success):
    sys.exit(0 if success else 2)


def pf(args=sys.argv[1:]):
    usage = 'Runs a power flow.'
    options, casedata, ppopt, fname, solvedcase = \
            parse_options(args, usage)
    if options.test:
        sys.exit(test_pf())
    _, _, _, _, success, _ = runpf(casedata, ppopt, fname, solvedcase)
    exit(success)


def opf(args=sys.argv[1:]):
    usage = 'Runs an optimal power flow.'
    options, casedata, ppopt, fname, solvedcase = \
            parse_options(args, usage, True)

    if options.test:
        sys.exit(test_opf())

    if options.uopf:
        r = runuopf(casedata, ppopt, fname, solvedcase)
    else:
        r = runopf(casedata, ppopt, fname, solvedcase)
    exit(r[6])  ## success


if __name__ == '__main__':
    pf(['-h'])
#    pf(['-c', 'case9', '--out_all=-1', '-s', '/tmp/out.py'])
