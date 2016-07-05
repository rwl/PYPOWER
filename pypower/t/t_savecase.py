# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for C{savecase} based on runpf and runopf.
"""

import os

from os.path import join

import tempfile

import numpy as np

from numpy import array

from pypower.api import case24_ieee_rts

from pypower.loadcase import loadcase
from pypower.ppoption import ppoption
from pypower.runpf import runpf
from pypower.runopf import runopf
from pypower.savecase import savecase

from pypower.t.t_begin import t_begin
from pypower.t.t_ok import t_ok


def t_savecase(quiet=False):
    """Tests that C{savecase} saves case files in MAT and PY file formats."""

    t_begin(12, quiet)

    MATCASE = 'test_savedcase.mat'
    PYCASE = 'test_savedcase.py'
    file_formats = [MATCASE, PYCASE]

    pf_case = {'case': case24_ieee_rts(),
               'run_func': runpf,
               'run_label': 'PF run'}
    opf_case = {'case': case24_ieee_rts(),
                'run_func': runopf,
                'run_label': 'OPF run'}
    case_unsolved = {'case': case24_ieee_rts(),
                     'run_func': None,
                     'run_label': 'pre-run'}
    cases = [pf_case, opf_case, case_unsolved]

    tmpdir = tempfile.mkdtemp()

    for case in cases:
        for i, filename in enumerate([f for f in file_formats]):
            file_format = save_format(filename)  # 'mat' or 'py'
            saved_umask = os.umask(0o22)
            path = join(tmpdir, filename)

            ppc = case['case']
            pf_func = case['run_func']
            run_type = case['run_label']

            # Test saving of results if case has been solved
            if pf_func:
                ppopt = ppoption(VERBOSE=0, OUT_ALL=0)
                # Run power flow type specified, assign solution to case
                ppc = pf_func(ppc, ppopt)
                # runpf.py returns a tuple containing the result
                if isinstance(ppc, tuple):
                    ppc = ppc[0]

            try:
                savedcase = savecase(path, ppc, comment=None, version='2')
            except IOError:
                t_ok(False, ['Savecase: ', 'IOError.'])
            else:
                # Do tests
                msg_prefix = message_prefix(file_format, run_type)

                loaded_case = loadcase(savedcase)

                msg_desc = ' file name matches argument'
                t_ok(savedcase == path, msg_prefix + msg_desc)

                msg_desc = ' file content matches case'
                # Boolean: saved key-value pairs do/do not correspond to case
                saved_case_matches_ppc = verify_saved_case(loaded_case, ppc)
                t_ok(saved_case_matches_ppc, msg_prefix + msg_desc)

                os.remove(path)
            finally:
                os.umask(saved_umask)
    os.rmdir(tmpdir)


def save_format(file):
    """Return 'mat' or 'py' based on file name extension."""
    ext = os.path.splitext(file)[1]
    return ext[-(len(ext) - 1):]


def message_prefix(file_format, run_type):
    """Text describing saved case file format and run results type."""
    format_str = ' format' if file_format == 'mat' else '  format'
    if run_type == ['PF run']:
        run_str = run_type + ': '
    else:
        run_str = run_type + ':'
    return 'Savecase: ' + file_format + format_str + ' - ' + run_str


def verify_saved_case(loaded_case, ppc):
    """Verify that expected keys exist and values match original case and
    results if case has been run.
    """
    saved_case_matches_ppc = True

    # Compare keys and values
    original_keys = iter(ppc)

    for k in original_keys:
        # These results fields from dict are not saved in py files.
        if k in ['success', 'et', 'order', 'om', 'f', 'lin', 'mu', 'raw',
                 'var', 'x', 'nln']:
            continue
        else:
            value = loaded_case[k]
            if isinstance(value, np.ndarray) and value.shape != (1,):
                if np.array_equal(value, array(ppc[k])):
                    continue
                else:
                    ncols = value.shape[1]
                    # With some types of results, fields saved to py files
                    # are saved with less precision than in raw results.
                    # This is consistent with MATPOWER savecase.
                    if ((k == 'bus' and ncols == 17) or
                            (k == 'gen' and (ncols == 14 or ncols == 25)) or
                            (k == 'branch' and ncols >= 14)):
                        if not np.allclose(value, array(ppc[k]), atol=1e-04):
                            saved_case_matches_ppc = False
                            break
            # Scalars and 'baseMVA', which has shape (1,) from loadcase()
            elif value == ppc[k]:
                continue
            else:
                saved_case_matches_ppc = False
                break

    return saved_case_matches_ppc


def mat_keys_from_py(ppc_keys):
    """If saved case format will be mat file, ignore Python-only dict keys."""
    keys_to_ignore = set(['__globals__', '__header__', '__version__'])
    return set([k for k in ppc_keys if k not in keys_to_ignore])


if __name__ == '__main__':
    t_savecase(quiet=False)
