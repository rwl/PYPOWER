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

from optparse import OptionParser, OptionGroup, OptionValueError

from pypower import \
    ppver, ppoption, runpf, runopf, runuopf, runopf_w_res, case9

from pypower.ppoption import \
    PF_OPTIONS, OPF_OPTIONS, OUTPUT_OPTIONS, PDIPM_OPTIONS

from pypower.t.test_pypower import test_pf, test_opf, test_opf_w_res


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


def parse_options(args, usage, opf=False):
    """Parse command line options.

    @param opf: Include OPF options?
    """
    v = ppver('all')
    parser = OptionParser(
        usage="""usage: %%prog [casedata] [options] [fname] [solvedcase]

%s

If 'casedata' is provided it specifies the name of the input data file
containing the case data. The default value is 'case9'. If 'fname' is given
the pretty printed output will be appended to the file. If 'solvedcase' is
specified the solved case will be written to a case file in PYPOWER format
with the specified name. If solvedcase ends with '.mat' it saves the case as
a MAT-file otherwise it saves it as a Python file.""" % usage,
        version='PYPOWER (%%prog) Version %s, %s' % (v["Version"], v["Date"])
    )

    parser.add_option("-t", "--test", action="store_true", dest="test",
        default=False, help="run tests")


    ppopt = ppoption()

    if opf:
        opf_options = OptionGroup(parser, 'OPF Options')
        pdipm_options = OptionGroup(parser, 'PDIPM Options')

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

    casedata, fname, solvedcase = case9(), '', ''  # defaults

    nargs = len(args)
    if nargs > 3:
        parser.print_help()
        sys.exit(2)
    elif nargs == 3:
        casedata, fname, solvedcase = args
    elif nargs == 2:
        casedata, fname, = args
    elif nargs == 1:
        casedata = args[0]

    return options, casedata, ppopt, fname, solvedcase


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
    r = runopf(casedata, ppopt, fname, solvedcase)
    exit(r['success'])


def uopf(args=sys.argv[1:]):
    usage = 'Solves combined unit decommitment / optimal power flow.'
    options, casedata, ppopt, fname, solvedcase = \
            parse_options(args, usage, True)
    if options.test:
        sys.exit(test_opf())
    r = runuopf(casedata, ppopt, fname, solvedcase)
    exit(r['success'])


def opf_w_res(args=sys.argv[1:]):
    usage = 'Runs an optimal power flow with fixed zonal reserves.'
    options, casedata, ppopt, fname, solvedcase = \
            parse_options(args, usage, True)
    if options.test: sys.exit(test_opf_w_res())
    r = runopf_w_res(casedata, ppopt, fname, solvedcase)
    exit(r['success'])


if __name__ == '__main__':
    #pf(['-t'])
    pf(['--out_all=0', '--pf_alg=2'])
