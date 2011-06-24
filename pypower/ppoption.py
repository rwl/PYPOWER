# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2009-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

PF_OPTIONS = [
    ('pf_alg', 1, '''power flow algorithm:
1 - Newton's method,
2 - Fast-Decoupled (XB version),
3 - Fast-Decoupled (BX version),
4 - Gauss Seidel'''),

    ('pf_tol', 1e-8, 'termination tolerance on per unit P & Q mismatch'),

    ('pf_max_it', 10, 'maximum number of iterations for Newton\'s method'),

    ('pf_max_it_fd', 30, 'maximum number of iterations for fast '
     'decoupled method'),

    ('pf_max_it_gs', 1000, 'maximum number of iterations for '
     'Gauss-Seidel method'),

    ('enforce_q_lims', False, 'enforce gen reactive power limits, at '
     'expense of |V|'),

    ('pf_dc', False, '''use DC power flow formulation, for power flow and OPF:
False - use AC formulation & corresponding algorithm opts,
True  - use DC formulation, ignore AC algorithm options''')
]

OPF_OPTIONS = [
    ('opf_alg', 0, '''algorithm to use for OPF:
0 - choose best default solver available in the
    following order, 500, 540, 520 then 100/200
Otherwise the first digit specifies the problem
formulation and the second specifies the solver,
as follows, (see the User's Manual for more details)
500 - generalized formulation, MINOS,
540 - generalized formulation, MIPS
      primal/dual interior point method,
545 - generalized formulation (except CCV), SC-MIPS
      step-controlled primal/dual interior point method'''),

    ('opf_poly2pwl_pts', 10, 'number of evaluation points to use when '
     'converting from polynomial to piece-wise linear costs)'),

    ('opf_violation', 5e-6, 'constraint violation tolerance'),

    ('opf_flow_lim', 0, '''qty to limit for branch flow constraints:
0 - apparent power flow (limit in MVA),
1 - active power flow (limit in MW),
2 - current magnitude (limit in MVA at 1 p.u. voltage'''),

    ('opf_ignore_ang_lim', False, 'ignore angle difference limits for '
     'branches even if specified'),

    ('opf_alg_dc', 0, '''solver to use for DC OPF:
0 - choose default solver based on availability in the
    following order, 600, 500, 200.
200 - PIPS, Python Interior Point Solver
      primal/dual interior point method,
250 - PIPS-sc, step-controlled variant of PIPS
400 - IPOPT, requires pyipopt interface to IPOPT solver
      available from: https://projects.coin-or.org/Ipopt/
500 - CPLEX, requires Python interface to CPLEX solver
600 - MOSEK, requires Python interface to MOSEK solver
      available from: http://www.mosek.com/''')
]

OUTPUT_OPTIONS = [
    ('verbose', 1, '''amount of progress info printed:
0 - print no progress info,
1 - print a little progress info,
2 - print a lot of progress info,
3 - print all progress info'''),

    ('out_all', -1, '''controls printing of results:
-1 - individual flags control what prints,
0 - don't print anything
    (overrides individual flags, except OUT_RAW),
1 - print everything
    (overrides individual flags, except OUT_RAW)'''),

    ('out_sys_sum', True, 'print system summary'),

    ('out_area_sum', False, 'print area summaries'),

    ('out_bus', True, 'print bus detail'),

    ('out_branch', True, 'print branch detail'),

    ('out_gen', False, '''print generator detail
(OUT_BUS also includes gen info)'''),
    ('out_all_lim', -1, '''control constraint info output:
-1 - individual flags control what constraint info prints,
0 - no constraint info (overrides individual flags),
1 - binding constraint info (overrides individual flags),
2 - all constraint info (overrides individual flags)'''),

    ('out_v_lim', 1, '''control output of voltage limit info:
0 - don't print,
1 - print binding constraints only,
2 - print all constraints
(same options for OUT_LINE_LIM, OUT_PG_LIM, OUT_QG_LIM)'''),

    ('out_line_lim', 1, 'control output of line limit info'),

    ('out_pg_lim', 1, 'control output of gen P limit info'),

    ('out_qg_lim', 1, 'control output of gen Q limit info'),

    ('out_raw', False, 'print raw data'),

    ('return_raw_der', 0, '''return constraint and derivative info
in results['raw'] (in keys g, dg, df, d2f))''')
]

PDIPM_OPTIONS = [
    ('pdipm_feastol', 0, '''feasibility (equality) tolerance
for Primal-Dual Interior Points Methods, set
to value of OPF_VIOLATION by default'''),
    ('pdipm_gradtol', 1e-6, '''gradient tolerance for
Primal-Dual Interior Points Methods'''),
    ('pdipm_comptol', 1e-6, '''complementary condition (inequality)
tolerance for Primal-Dual Interior Points Methods'''),
    ('pdipm_costtol', 1e-6, '''optimality tolerance for
Primal-Dual Interior Points Methods'''),
    ('pdipm_max_it',  150, '''maximum number of iterations for
Primal-Dual Interior Points Methods'''),
    ('scpdipm_red_it', 20, '''maximum number of reductions per iteration
for Step-Control Primal-Dual Interior Points Methods''')
]

def ppoption(ppopt=None, **kw_args):
    """PYPOWER options dictionary.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """

    default_ppopt = {
#        # power flow options
#        'PF_ALG':         1,      # 1  - PF_ALG
#        'PF_TOL':         1e-8,   # 2  - PF_TOL
#        'PF_MAX_IT':      10,     # 3  - PF_MAX_IT
#        'PF_MAX_IT_FD':   30,     # 4  - PF_MAX_IT_FD
#        'PF_MAX_IT_GS':   1000,   # 5  - PF_MAX_IT_GS
#        'ENFORCE_Q_LIMS': 0,      # 6  - ENFORCE_Q_LIMS
#        'RESERVED7':      0,      # 7  - RESERVED7
#        'RESERVED8':      0,      # 8  - RESERVED8
#        'RESERVED9':      0,      # 9  - RESERVED9
#        'PF_DC':          0,      # 10 - PF_DC
#
#        # OPF options
#        'OPF_ALG_POLY':  0,      # 11 - OPF_ALG_POLY
#        'OPF_ALG_POLY':  100,    # 12 - OPF_ALG_POLY
#        'OPF_ALG_PWL':   200,    # 13 - OPF_ALG_PWL
#        'OPF_POLY2PWL_PTS': 10,  # 14 - OPF_POLY2PWL_PTS
#        'OPF_NEQ':       0,      # 15 - OPF_NEQ
#        'OPF_VIOLATION': 5e-6,   # 16 - OPF_VIOLATION
#        'CONSTR_TOL_X':  1e-4,   # 17 - CONSTR_TOL_X
#        'CONSTR_TOL_F':  1e-4,   # 18 - CONSTR_TOL_F
#        'CONSTR_MAX_IT': 0,      # 19 - CONSTR_MAX_IT
#        'LPC_TOL_GRAD':  3e-3,   # 20 - LPC_TOL_GRAD
#        'LPC_TOL_X':     1e-4,   # 21 - LPC_TOL_X
#        'LPC_MAX_IT':    400,    # 22 - LPC_MAX_IT
#        'LPC_MAX_RESTART': 5,    # 23 - LPC_MAX_RESTART
#        'OPF_FLOW_LIM':  0,      # 24 - OPF_FLOW_LIM
#        'OPF_IGNORE_ANG_LIM': 0, # 25 - OPF_IGNORE_ANG_LIM
#        'RESERVED26': 0,         # 26 - RESERVED26
#        'RESERVED27': 0,         # 27 - RESERVED27
#        'RESERVED28': 0,         # 28 - RESERVED28
#        'RESERVED29': 0,         # 29 - RESERVED29
#        'RESERVED30': 0,         # 30 - RESERVED30
#
#        # output options
#        'VERBOSE':      1,      # 31 - VERBOSE
#        'OUT_ALL':      0,     # 32 - OUT_ALL
#        'OUT_SYS_SUM':  1,      # 33 - OUT_SYS_SUM
#        'OUT_AREA_SUM': 0,      # 34 - OUT_AREA_SUM
#        'OUT_BUS':      1,      # 35 - OUT_BUS
#        'OUT_BRANCH':   1,      # 36 - OUT_BRANCH
#        'OUT_GEN':      0,      # 37 - OUT_GEN
#        'OUT_ALL_LIM': -1,     # 38 - OUT_ALL_LIM
#        'OUT_V_LIM':    1,      # 39 - OUT_V_LIM
#        'OUT_LINE_LIM': 1,      # 40 - OUT_LINE_LIM
#        'OUT_PG_LIM':   1,      # 41 - OUT_PG_LIM
#        'OUT_QG_LIM':   1,      # 42 - OUT_QG_LIM
#        'OUT_RAW':      0,      # 43 - OUT_RAW
#        'RESERVED44':   0,      # 44 - RESERVED44
#        'RESERVED45':   0,      # 45 - RESERVED45
#        'RESERVED46':   0,      # 46 - RESERVED46
#        'RESERVED47':   0,      # 47 - RESERVED47
#        'RESERVED48':   0,      # 48 - RESERVED48
#        'RESERVED49':   0,      # 49 - RESERVED49
#        'RESERVED50':   0,      # 50 - RESERVED50
#
#        # PDIPM options
#        0      # 81 - PDIPM_FEASTOL
#        1e-6   # 82 - PDIPM_GRADTOL
#        1e-6   # 83 - PDIPM_COMPTOL
#        1e-6   # 84 - PDIPM_COSTTOL
#        150    # 85 - PDIPM_MAX_IT
#        20     # 86 - SCPDIPM_RED_IT
    }

    options = PF_OPTIONS + OPF_OPTIONS + OUTPUT_OPTIONS + PDIPM_OPTIONS

    for name, default, _ in options:
        default_ppopt[name.upper()] = default

    ppopt = default_ppopt if ppopt == None else ppopt.copy()

    ppopt.update(kw_args)

    return ppopt
