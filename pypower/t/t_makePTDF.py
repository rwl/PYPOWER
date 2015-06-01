# Copyright (c) 1996-2015 PSERC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Tests for C{makePTDF}.
"""

from os.path import dirname, join

from numpy import ones, zeros, eye, arange, dot, matrix, flatnonzero as find

from scipy.sparse import csr_matrix as sparse

from pypower.ppoption import ppoption
from pypower.rundcopf import rundcopf
from pypower.ext2int import ext2int1
from pypower.makePTDF import makePTDF
from pypower.idx_gen import GEN_BUS, PG
from pypower.idx_bus import PD
from pypower.idx_brch import PF

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end


def t_makePTDF(quiet=False):
    """Tests for C{makePTDF}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    ntests = 24
    t_begin(ntests, quiet)

    tdir = dirname(__file__)
    casefile = join(tdir, 't_case9_opf')
    verbose = 0#not quiet

    ## load case
    ppopt = ppoption(VERBOSE=verbose, OUT_ALL=0)
    r = rundcopf(casefile, ppopt)
    baseMVA, bus, gen, branch = r['baseMVA'], r['bus'], r['gen'], r['branch']
    _, bus, gen, branch = ext2int1(bus, gen, branch)
    nb  = bus.shape[0]
    nbr = branch.shape[0]
    ng  = gen.shape[0]

    ## compute injections and flows
    Cg = sparse((ones(ng), (gen[:, GEN_BUS], arange(ng))), (nb, ng))
    Pg = Cg * gen[:, PG]
    Pd = bus[:, PD]
    P  = Pg - Pd
    ig = find(P > 0)
    il = find(P <= 0)
    F  = branch[:, PF]

    ## create corresponding slack distribution matrices
    e1 = zeros((nb, 1));  e1[0] = 1
    e4 = zeros((nb, 1));  e4[3] = 1
    D1  = eye(nb, nb) - dot(e1, ones((1, nb)))
    D4  = eye(nb, nb) - dot(e4, ones((1, nb)))
    Deq = eye(nb, nb) - ones((nb, 1)) / nb * ones((1, nb))
    Dg  = eye(nb) - matrix( Pd / sum(Pd) ).T * ones(nb)
    Dd  = eye(nb) - matrix( Pg / sum(Pg) ).T * ones(nb)

    ## create some PTDF matrices
    H1  = makePTDF(baseMVA, bus, branch, 0)
    H4  = makePTDF(baseMVA, bus, branch, 3)
    Heq = makePTDF(baseMVA, bus, branch, ones(nb))
    Hg  = makePTDF(baseMVA, bus, branch, Pd)
    Hd  = makePTDF(baseMVA, bus, branch, Pg)

    ## matrices get properly transformed by slack dist matrices
    t_is(H1,  dot(H1, D1), 8,  'H1  == H1 * D1')
    t_is(H4,  dot(H1, D4), 8,  'H4  == H1 * D4')
    t_is(Heq, dot(H1, Deq), 8, 'Heq == H1 * Deq')
    t_is(Hg,  dot(H1, Dg), 8,  'Hg  == H1 * Dg')
    t_is(Hd,  dot(H1, Dd), 8,  'Hd  == H1 * Dd')
    t_is(H1,  dot(Heq, D1), 8,  'H1  == Heq * D1')
    t_is(H4,  dot(Heq, D4), 8,  'H4  == Heq * D4')
    t_is(Heq, dot(Heq, Deq), 8, 'Heq == Heq * Deq')
    t_is(Hg,  dot(Heq, Dg), 8,  'Hg  == Heq * Dg')
    t_is(Hd,  dot(Heq, Dd), 8,  'Hd  == Heq * Dd')
    t_is(H1,  dot(Hg, D1), 8,  'H1  == Hg * D1')
    t_is(H4,  dot(Hg, D4), 8,  'H4  == Hg * D4')
    t_is(Heq, dot(Hg, Deq), 8, 'Heq == Hg * Deq')
    t_is(Hg,  dot(Hg, Dg), 8,  'Hg  == Hg * Dg')
    t_is(Hd,  dot(Hg, Dd), 8,  'Hd  == Hg * Dd')

    ## PTDFs can reconstruct flows
    t_is(F,  dot(H1, P),  3,  'Flow == H1  * P')
    t_is(F,  dot(H4, P),  3,  'Flow == H4  * P')
    t_is(F,  dot(Heq, P), 3,  'Flow == Heq * P')
    t_is(F,  dot(Hg, P),  3,  'Flow == Hg  * P')
    t_is(F,  dot(Hd, P),  3,  'Flow == Hd  * P')

    ## other
    t_is(F,  dot(Hg, Pg),  3,  'Flow == Hg  * Pg')
    t_is(F,  dot(Hd, (-Pd)),  3,  'Flow == Hd  * (-Pd)')
    t_is(zeros(nbr),  dot(Hg, (-Pd)),  3,  'zeros == Hg  * (-Pd)')
    t_is(zeros(nbr),  dot(Hd, Pg),  3,  'zeros == Hd  * Pg')

    t_end()


if __name__ == '__main__':
    t_makePTDF(quiet=False)
