# Copyright (C) 2006-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
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

from numpy import ones, zeros, eye, flatnonzero as find

from scipy.sparse import csr_matrix as sparse

from pypower.ppoption import ppoption
from pypower.rundcopf import rundcopf
from pypower.ext2int import ext2int
from pypower.makePTDF import makePTDF

from pypower.t.t_begin import t_begin
from pypower.t.t_is import t_is
from pypower.t.t_end import t_end

def t_makePTDF(quiet=False):
    """Tests for C{makePTDF}.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ntests = 24
    t_begin(ntests, quiet)

    casefile = 't_case9_opf'
    verbose = not quiet

    ## load case
    opt = ppoption()
    opt['VERBOSE'] = 0
    opt['OUT_ALL'] = 0
    baseMVA, bus, gen, _, branch, _, _, _ = rundcopf(casefile, opt)
    _, bus, gen, branch = ext2int(bus, gen, branch)
    nb  = bus.size()
    nbr = branch.size()
    ng  = gen.size()

    ## compute injections and flows
    Cg = sparse((ones(ng), (gen.gen_bus, range(ng))), (nb, ng))
    Pg = Cg * gen.Pg[:]
    Pd = bus.Pd[:]
    P  = Pg - Pd
    ig = find(P > 0)
    il = find(P <= 0)
    F  = branch.Pf[:]

    ## create corresponding slack distribution matrices
    e1 = zeros(nb)
    e1[0] = 1
    e4 = zeros(nb)
    e4[3] = 1
    D1  = eye((nb, nb)) - e1 * ones((1, nb))
    D4  = eye((nb, nb)) - e4 * ones((1, nb))
    Deq = eye((nb, nb)) - ones((nb, 1)) / nb * ones((1, nb))
    Dg  = eye(nb) - Pd / sum(Pd) * ones((1, nb))
    Dd  = eye(nb) - Pg / sum(Pg) * ones((1, nb))

    ## create some PTDF matrices
    H1  = makePTDF(baseMVA, bus, branch, 0)  # TODO Check zero based indexing
    H4  = makePTDF(baseMVA, bus, branch, 3)  # TODO Check zero based indexing
    Heq = makePTDF(baseMVA, bus, branch, ones(nb))
    Hg  = makePTDF(baseMVA, bus, branch, Pd)
    Hd  = makePTDF(baseMVA, bus, branch, Pg)

    ## matrices get properly transformed by slack dist matrices
    t_is(H1,  H1 * D1, 8,  'H1  == H1 * D1')
    t_is(H4,  H1 * D4, 8,  'H4  == H1 * D4')
    t_is(Heq, H1 * Deq, 8, 'Heq == H1 * Deq')
    t_is(Hg,  H1 * Dg, 8,  'Hg  == H1 * Dg')
    t_is(Hd,  H1 * Dd, 8,  'Hd  == H1 * Dd')
    t_is(H1,  Heq * D1, 8,  'H1  == Heq * D1')
    t_is(H4,  Heq * D4, 8,  'H4  == Heq * D4')
    t_is(Heq, Heq * Deq, 8, 'Heq == Heq * Deq')
    t_is(Hg,  Heq * Dg, 8,  'Hg  == Heq * Dg')
    t_is(Hd,  Heq * Dd, 8,  'Hd  == Heq * Dd')
    t_is(H1,  Hg * D1, 8,  'H1  == Hg * D1')
    t_is(H4,  Hg * D4, 8,  'H4  == Hg * D4')
    t_is(Heq, Hg * Deq, 8, 'Heq == Hg * Deq')
    t_is(Hg,  Hg * Dg, 8,  'Hg  == Hg * Dg')
    t_is(Hd,  Hg * Dd, 8,  'Hd  == Hg * Dd')

    ## PTDFs can reconstruct flows
    t_is(F,  H1 * P,  3,  'Flow == H1  * P')
    t_is(F,  H4 * P,  3,  'Flow == H4  * P')
    t_is(F,  Heq * P, 3,  'Flow == Heq * P')
    t_is(F,  Hg * P,  3,  'Flow == Hg  * P')
    t_is(F,  Hd * P,  3,  'Flow == Hd  * P')

    ## other
    t_is(F,  Hg * Pg,  3,  'Flow == Hg  * Pg')
    t_is(F,  Hd * (-Pd),  3,  'Flow == Hd  * (-Pd)')
    t_is(zeros(nbr,1),  Hg * (-Pd),  3,  'zeros == Hg  * (-Pd)')
    t_is(zeros(nbr,1),  Hd * Pg,  3,  'zeros == Hd  * Pg')

    t_end
