# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for DC line extension in L{{toggle_dcline}.
"""

from os.path import dirname, join

from numpy import array, ones, zeros, Inf, r_, ix_, argsort, arange
from numpy import flatnonzero as find

from pypower.ppoption import ppoption
from pypower.loadcase import loadcase
from pypower.runopf import runopf
from pypower.runpf import runpf
from pypower.rundcopf import rundcopf
from pypower.rundcpf import rundcpf
from pypower.toggle_dcline import toggle_dcline

from pypower.idx_bus import \
    BUS_I, BUS_AREA, BASE_KV, VMIN, VM, VA, LAM_P, LAM_Q, MU_VMIN, MU_VMAX, \
    BUS_TYPE, PV, PD, QD

from pypower.idx_gen import \
    GEN_BUS, PMIN, QMAX, QMIN, MBASE, APF, PG, QG, VG, MU_PMAX, MU_QMIN, \
    PC1, PC2, QC1MIN, QC1MAX, QC2MIN, QC2MAX

from pypower.idx_brch import \
    ANGMAX, PF, QT, MU_SF, MU_ST, MU_ANGMAX, MU_ANGMIN, ANGMIN, RATE_A

from pypower import idx_dcline as c

from pypower.t.t_begin import t_begin
from pypower.t.t_end import t_end
from pypower.t.t_ok import t_ok
from pypower.t.t_is import t_is


def t_dcline(quiet=False):
    """Tests for DC line extension in L{{toggle_dcline}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    num_tests = 50

    t_begin(num_tests, quiet)

    tdir = dirname(__file__)
    casefile = join(tdir, 't_case9_dcline')
    if quiet:
        verbose = False
    else:
        verbose = False

    t0 = ''
    ppopt = ppoption(OPF_VIOLATION=1e-6, PDIPM_GRADTOL=1e-8,
            PDIPM_COMPTOL=1e-8, PDIPM_COSTTOL=1e-9)
    ppopt = ppoption(ppopt, OPF_ALG=560, OPF_ALG_DC=200)
    ppopt = ppoption(ppopt, OUT_ALL=0, VERBOSE=verbose)

    ## set up indices
    ib_data     = r_[arange(BUS_AREA + 1), arange(BASE_KV, VMIN + 1)]
    ib_voltage  = arange(VM, VA + 1)
    ib_lam      = arange(LAM_P, LAM_Q + 1)
    ib_mu       = arange(MU_VMAX, MU_VMIN + 1)
    ig_data     = r_[[GEN_BUS, QMAX, QMIN], arange(MBASE, APF + 1)]
    ig_disp     = array([PG, QG, VG])
    ig_mu       = arange(MU_PMAX, MU_QMIN + 1)
    ibr_data    = arange(ANGMAX + 1)
    ibr_flow    = arange(PF, QT + 1)
    ibr_mu      = array([MU_SF, MU_ST])
    ibr_angmu   = array([MU_ANGMIN, MU_ANGMAX])

    ## load case
    ppc0 = loadcase(casefile)
    del ppc0['dclinecost']
    ppc = ppc0
    ppc = toggle_dcline(ppc, 'on')
    ppc = toggle_dcline(ppc, 'off')
    ndc = ppc['dcline'].shape[0]

    ## run AC OPF w/o DC lines
    t = ''.join([t0, 'AC OPF (no DC lines) : '])
    r0 = runopf(ppc0, ppopt)
    success = r0['success']
    t_ok(success, [t, 'success'])
    r = runopf(ppc, ppopt)
    success = r['success']
    t_ok(success, [t, 'success'])
    t_is(r['f'], r0['f'], 8, [t, 'f'])
    t_is(   r['bus'][:,ib_data   ],    r0['bus'][:,ib_data   ], 10, [t, 'bus data'])
    t_is(   r['bus'][:,ib_voltage],    r0['bus'][:,ib_voltage],  3, [t, 'bus voltage'])
    t_is(   r['bus'][:,ib_lam    ],    r0['bus'][:,ib_lam    ],  3, [t, 'bus lambda'])
    t_is(   r['bus'][:,ib_mu     ],    r0['bus'][:,ib_mu     ],  2, [t, 'bus mu'])
    t_is(   r['gen'][:,ig_data   ],    r0['gen'][:,ig_data   ], 10, [t, 'gen data'])
    t_is(   r['gen'][:,ig_disp   ],    r0['gen'][:,ig_disp   ],  3, [t, 'gen dispatch'])
    t_is(   r['gen'][:,ig_mu     ],    r0['gen'][:,ig_mu     ],  3, [t, 'gen mu'])
    t_is(r['branch'][:,ibr_data  ], r0['branch'][:,ibr_data  ], 10, [t, 'branch data'])
    t_is(r['branch'][:,ibr_flow  ], r0['branch'][:,ibr_flow  ],  3, [t, 'branch flow'])
    t_is(r['branch'][:,ibr_mu    ], r0['branch'][:,ibr_mu    ],  2, [t, 'branch mu'])

    t = ''.join([t0, 'AC PF (no DC lines) : '])
    ppc1 = {'baseMVA': r['baseMVA'],
            'bus': r['bus'][:, :VMIN + 1].copy(),
            'gen': r['gen'][:, :APF + 1].copy(),
            'branch': r['branch'][:, :ANGMAX + 1].copy(),
            'gencost': r['gencost'].copy(),
            'dcline': r['dcline'][:, :c.LOSS1 + 1].copy()}
    ppc1['bus'][:, VM] = 1
    ppc1['bus'][:, VA] = 0
    rp = runpf(ppc1, ppopt)
    success = rp['success']
    t_ok(success, [t, 'success'])
    t_is(   rp['bus'][:,ib_voltage],    r['bus'][:,ib_voltage],  3, [t, 'bus voltage'])
    t_is(   rp['gen'][:,ig_disp   ],    r['gen'][:,ig_disp   ],  3, [t, 'gen dispatch'])
    t_is(rp['branch'][:,ibr_flow  ], r['branch'][:,ibr_flow  ],  3, [t, 'branch flow'])

    ## run with DC lines
    t = ''.join([t0, 'AC OPF (with DC lines) : '])
    ppc = toggle_dcline(ppc, 'on')
    r = runopf(ppc, ppopt)
    success = r['success']
    t_ok(success, [t, 'success'])
    expected = array([
        [10,     8.9,  -10,       10, 1.0674, 1.0935],
        [2.2776, 2.2776, 0,        0, 1.0818, 1.0665],
        [0,      0,      0,        0, 1.0000, 1.0000],
        [10,     9.5,    0.0563, -10, 1.0778, 1.0665]
    ])
    t_is(r['dcline'][:, c.PF:c.VT + 1], expected, 4, [t, 'P Q V'])
    expected = array([
        [0, 0.8490, 0.6165, 0,      0,      0.2938],
        [0, 0,      0,      0.4290, 0.0739, 0],
        [0, 0,      0,      0,      0,      0],
        [0, 7.2209, 0,      0,      0.0739, 0]
    ])
    t_is(r['dcline'][:, c.MU_PMIN:c.MU_QMAXT + 1], expected, 3, [t, 'mu'])

    t = ''.join([t0, 'AC PF (with DC lines) : '])
    ppc1 = {'baseMVA': r['baseMVA'],
            'bus': r['bus'][:, :VMIN + 1].copy(),
            'gen': r['gen'][:, :APF + 1].copy(),
            'branch': r['branch'][:, :ANGMAX + 1].copy(),
            'gencost': r['gencost'].copy(),
            'dcline': r['dcline'][:, :c.LOSS1 + 1].copy()}
    ppc1 = toggle_dcline(ppc1, 'on')
    ppc1['bus'][:, VM] = 1
    ppc1['bus'][:, VA] = 0
    rp = runpf(ppc1, ppopt)
    success = rp['success']
    t_ok(success, [t, 'success'])
    t_is(   rp['bus'][:,ib_voltage],    r['bus'][:,ib_voltage], 3, [t, 'bus voltage'])
    #t_is(   rp['gen'][:,ig_disp   ],    r['gen'][:,ig_disp   ], 3, [t, 'gen dispatch'])
    t_is(   rp['gen'][:2,ig_disp ],    r['gen'][:2,ig_disp ], 3, [t, 'gen dispatch'])
    t_is(   rp['gen'][2,PG        ],    r['gen'][2,PG        ], 3, [t, 'gen dispatch'])
    t_is(   rp['gen'][2,QG]+rp['dcline'][0,c.QF], r['gen'][2,QG]+r['dcline'][0,c.QF], 3, [t, 'gen dispatch'])
    t_is(rp['branch'][:,ibr_flow  ], r['branch'][:,ibr_flow  ], 3, [t, 'branch flow'])

    ## add appropriate P and Q injections and check angles and generation when running PF
    t = ''.join([t0, 'AC PF (with equivalent injections) : '])
    ppc1 = {'baseMVA': r['baseMVA'],
            'bus': r['bus'][:, :VMIN + 1].copy(),
            'gen': r['gen'][:, :APF + 1].copy(),
            'branch': r['branch'][:, :ANGMAX + 1].copy(),
            'gencost': r['gencost'].copy(),
            'dcline': r['dcline'][:, :c.LOSS1 + 1].copy()}
    ppc1['bus'][:, VM] = 1
    ppc1['bus'][:, VA] = 0
    for k in range(ndc):
        if ppc1['dcline'][k, c.BR_STATUS]:
            ff = find(ppc1['bus'][:, BUS_I] == ppc1['dcline'][k, c.F_BUS])
            tt = find(ppc1['bus'][:, BUS_I] == ppc1['dcline'][k, c.T_BUS])
            ppc1['bus'][ff, PD] = ppc1['bus'][ff, PD] + r['dcline'][k, c.PF]
            ppc1['bus'][ff, QD] = ppc1['bus'][ff, QD] - r['dcline'][k, c.QF]
            ppc1['bus'][tt, PD] = ppc1['bus'][tt, PD] - r['dcline'][k, c.PT]
            ppc1['bus'][tt, QD] = ppc1['bus'][tt, QD] - r['dcline'][k, c.QT]
            ppc1['bus'][ff, VM] = r['dcline'][k, c.VF]
            ppc1['bus'][tt, VM] = r['dcline'][k, c.VT]
            ppc1['bus'][ff, BUS_TYPE] = PV
            ppc1['bus'][tt, BUS_TYPE] = PV

    rp = runpf(ppc1, ppopt)
    success = rp['success']
    t_ok(success, [t, 'success'])
    t_is(   rp['bus'][:,ib_voltage],    r['bus'][:,ib_voltage],  3, [t, 'bus voltage'])
    t_is(   rp['gen'][:,ig_disp   ],    r['gen'][:,ig_disp   ],  3, [t, 'gen dispatch'])
    t_is(rp['branch'][:,ibr_flow  ], r['branch'][:,ibr_flow  ],  3, [t, 'branch flow'])

    ## test DC OPF
    t = ''.join([t0, 'DC OPF (with DC lines) : '])
    ppc = ppc0.copy()
    ppc['gen'][0, PMIN] = 10
    ppc['branch'][4, RATE_A] = 100
    ppc = toggle_dcline(ppc, 'on')
    r = rundcopf(ppc, ppopt)
    success = r['success']
    t_ok(success, [t, 'success'])
    expected = array([
        [10, 8.9, 0, 0, 1.01, 1],
        [2,  2,   0, 0, 1,    1],
        [0,  0,   0, 0, 1,    1],
        [10, 9.5, 0, 0, 1, 0.98]
    ])
    t_is(r['dcline'][:, c.PF:c.VT + 1], expected, 4, [t, 'P Q V'])
    expected = array([
        [0,      1.8602, 0, 0, 0, 0],
        [1.8507, 0,      0, 0, 0, 0],
        [0,      0,      0, 0, 0, 0],
        [0,      0.2681, 0, 0, 0, 0]
    ])
    t_is(r['dcline'][:, c.MU_PMIN:c.MU_QMAXT + 1], expected, 3, [t, 'mu'])

    t = ''.join([t0, 'DC PF (with DC lines) : '])
    ppc1 = {'baseMVA': r['baseMVA'],
            'bus': r['bus'][:, :VMIN + 1].copy(),
            'gen': r['gen'][:, :APF + 1].copy(),
            'branch': r['branch'][:, :ANGMAX + 1].copy(),
            'gencost': r['gencost'].copy(),
            'dcline': r['dcline'][:, :c.LOSS1 + 1].copy()}
    ppc1 = toggle_dcline(ppc1, 'on')
    ppc1['bus'][:, VA] = 0
    rp = rundcpf(ppc1, ppopt)
    success = rp['success']
    t_ok(success, [t, 'success'])
    t_is(   rp['bus'][:,ib_voltage],    r['bus'][:,ib_voltage], 3, [t, 'bus voltage'])
    t_is(   rp['gen'][:,ig_disp   ],    r['gen'][:,ig_disp   ], 3, [t, 'gen dispatch'])
    t_is(rp['branch'][:,ibr_flow  ], r['branch'][:,ibr_flow  ], 3, [t, 'branch flow'])

    ## add appropriate P injections and check angles and generation when running PF
    t = ''.join([t0, 'DC PF (with equivalent injections) : '])
    ppc1 = {'baseMVA': r['baseMVA'],
            'bus': r['bus'][:, :VMIN + 1].copy(),
            'gen': r['gen'][:, :APF + 1].copy(),
            'branch': r['branch'][:, :ANGMAX + 1].copy(),
            'gencost': r['gencost'].copy(),
            'dcline': r['dcline'][:, :c.LOSS1 + 1].copy()}
    ppc1['bus'][:, VA] = 0
    for k in range(ndc):
        if ppc1['dcline'][k, c.BR_STATUS]:
            ff = find(ppc1['bus'][:, BUS_I] == ppc1['dcline'][k, c.F_BUS])
            tt = find(ppc1['bus'][:, BUS_I] == ppc1['dcline'][k, c.T_BUS])
            ppc1['bus'][ff, PD] = ppc1['bus'][ff, PD] + r['dcline'][k, c.PF]
            ppc1['bus'][tt, PD] = ppc1['bus'][tt, PD] - r['dcline'][k, c.PT]
            ppc1['bus'][ff, BUS_TYPE] = PV
            ppc1['bus'][tt, BUS_TYPE] = PV

    rp = rundcpf(ppc1, ppopt)
    success = rp['success']
    t_ok(success, [t, 'success'])
    t_is(   rp['bus'][:,ib_voltage],    r['bus'][:,ib_voltage],  3, [t, 'bus voltage'])
    t_is(   rp['gen'][:,ig_disp   ],    r['gen'][:,ig_disp   ],  3, [t, 'gen dispatch'])
    t_is(rp['branch'][:,ibr_flow  ], r['branch'][:,ibr_flow  ],  3, [t, 'branch flow'])

    ## run with DC lines
    t = ''.join([t0, 'AC OPF (with DC lines + poly cost) : '])
    ppc = loadcase(casefile)
    ppc = toggle_dcline(ppc, 'on')
    r = runopf(ppc, ppopt)
    success = r['success']
    t_ok(success, [t, 'success'])
    expected1 = array([
        [10,     8.9,   -10,       10, 1.0663, 1.0936],
        [7.8429, 7.8429,  0,        0, 1.0809, 1.0667],
        [0,      0,       0,        0, 1.0000, 1.0000],
        [6.0549, 5.7522, -0.5897, -10, 1.0778, 1.0667]
    ])
    t_is(r['dcline'][:, c.PF:c.VT + 1], expected1, 4, [t, 'P Q V'])
    expected2 = array([
        [0, 0.7605, 0.6226, 0,      0,      0.2980],
        [0, 0,      0,      0.4275, 0.0792, 0],
        [0, 0,      0,      0,      0,      0],
        [0, 0,      0,      0,      0.0792, 0]
    ])
    t_is(r['dcline'][:, c.MU_PMIN:c.MU_QMAXT + 1], expected2, 3, [t, 'mu'])

    ppc['dclinecost'][3, :8] = array([2, 0, 0, 4, 0, 0, 7.3, 0])
    r = runopf(ppc, ppopt)
    success = r['success']
    t_ok(success, [t, 'success'])
    t_is(r['dcline'][:, c.PF:c.VT + 1], expected1, 4, [t, 'P Q V'])
    t_is(r['dcline'][:, c.MU_PMIN:c.MU_QMAXT + 1], expected2, 3, [t, 'mu'])

    t = ''.join([t0, 'AC OPF (with DC lines + pwl cost) : '])
    ppc['dclinecost'][3, :8] = array([1, 0, 0, 2, 0, 0, 10, 73])
    r = runopf(ppc, ppopt)
    success = r['success']
    t_ok(success, [t, 'success'])
    t_is(r['dcline'][:, c.PF:c.VT + 1], expected1, 4, [t, 'P Q V'])
    t_is(r['dcline'][:, c.MU_PMIN:c.MU_QMAXT + 1], expected2, 3, [t, 'mu'])

    t_end()


if __name__ == '__main__':
    t_dcline(quiet=False)
