# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Main entry-points for PYPOWER.
"""

import sys
from sys import stderr

from optparse import OptionParser, OptionGroup, OptionValueError

from pypower.api import \
    ppver, ppoption, runpf, runopf, runuopf, runopf_w_res

from pypower.api import \
    case4gs, case6ww, case9, case9Q, case14, case24_ieee_rts, case30, \
    case30Q, case30pwl, case39, case57, case118, case300, t_case30_userfcns

from pypower.ppoption import \
    PF_OPTIONS, OPF_OPTIONS, OUTPUT_OPTIONS, PDIPM_OPTIONS

from pypower.t.test_pypower import test_pf, test_opf


TYPE_MAP = {bool: 'choice', float: 'float', int: 'int'}

AFFIRMATIVE = ('True', 'Yes', 'true', 'yes', '1', 'Y', 'y')
NEGATIVE = ('False', 'No', 'false', 'no', '0', 'N', 'n')

CASES = {'case4gs': case4gs, 'case6ww': case6ww, 'case9': case9,
    'case9Q': case9Q, 'case14': case14, 'case24_ieee_rts': case24_ieee_rts,
    'case30': case30, 'case30Q': case30Q, 'case30pwl': case30pwl,
    'case39': case39, 'case57': case57, 'case118': case118, 'case300': case300,
    'case30_userfcns': t_case30_userfcns}


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

    parser.add_option("-c", "--testcase", default='case9',
                      choices=list(CASES.keys()),
                      help="built-in test case, choose from: %s" % str(
                          list(CASES.keys()))[1:-1])

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
        pdipm_options = OptionGroup(parser, 'PDIPM Options')

        opf_options.add_option("-u", "--uopf", action="store_true",
            help="""runs an optimal power flow with the unit-decommitment
heuristic""")

        opf_options.add_option("-r", "--w_res", action="store_true",
            help="""runs an optimal power flow with fixed zonal reserves""")

        add_options(opf_options, OPF_OPTIONS, ppopt)
        add_options(pdipm_options, PDIPM_OPTIONS, ppopt)

        parser.add_option_group(opf_options)
        parser.add_option_group(pdipm_options)
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
        try:
            casedata = CASES[options.testcase]()
        except KeyError:
            stderr.write("Invalid case choice: %r (choose from %s)\n" % \
                (options.testcase, list(CASES.keys())))
            sys.exit(2)

    return options, casedata, ppopt, options.fname, options.solvedcase


def exit(success):
    sys.exit(0 if success else 2)


def pf(args=sys.argv[1:]):
    usage = 'Runs a power flow.'
    options, casedata, ppopt, fname, solvedcase = \
            parse_options(args, usage)
    if options.test:
        sys.exit(test_pf())
    _, success = runpf(casedata, ppopt, fname, solvedcase)
    exit(success)


def opf(args=sys.argv[1:]):
    usage = 'Runs an optimal power flow.'
    options, casedata, ppopt, fname, solvedcase = \
            parse_options(args, usage, True)

    if options.test:
        sys.exit(test_opf())

    if options.uopf:
        if options.w_res:
            stderr.write('uopf and opf_w_res are mutex\n')
        r = runuopf(casedata, ppopt, fname, solvedcase)
    elif options.w_res:
        r = runopf_w_res(casedata, ppopt, fname, solvedcase)
    else:
        r = runopf(casedata, ppopt, fname, solvedcase)
    exit(r['success'])


if __name__ == '__main__':
    pf(['-h'])
#    pf(['-c', 'case9', '--out_all=-1', '-s', '/tmp/out.py'])
