# Copyright (C) 2009-2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

import unittest

from os.path import join, dirname

from scipy.io.mmio import mmread

from numpy import allclose, pi

from pypower import \
    idx_bus, idx_gen, idx_brch, loadcase, ext2int, bustypes, makeBdc, \
    makeSbus, dcpf, int2ext, ppoption, rundcpf

DATA_DIR = join(dirname(__file__), "data")

class _BaseTestCase(unittest.TestCase):
    """Abstract PYPOWER test case.
    """

    def __init__(self, methodName='runTest'):
        super(_BaseTestCase, self).__init__(methodName)

        #: Name of the PYPOWER case and the folder in which the MatrixMarket
        #  data exists. Subclasses should set this value.
        self.case_name = ""

        #: Relative tolerance for equality (see allclose notes).
        self.rtol = 1e-05

        #: Absolute tolerance for equality (see allclose notes).
        self.atol = 1e-08

        #: Number of decimal places to round to for float equality.
        self.places = 7

        self.case = None
        self.opf = None

        self.path = ""


    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case_path = join(dirname(loadcase.__file__), self.case_name)


    def test_loadcase(self):
        """Test loading a case.
        """
        ppc = loadcase.loadcase(self.case_path)

        self.compare_case(ppc, "loadcase")


    def test_ext2int(self):
        """Test conversion from external to internal indexing.
        """
        ppc = loadcase.loadcase(self.case_path)
        ppc = ext2int.ext2int(ppc)

        self.compare_case(ppc, "ext2int")


    def test_bustypes(self):
        """Test bus index lists.
        """
        ppc = loadcase.loadcase(self.case_path)
        ppc = ext2int.ext2int(ppc)
        ref, pv, pq = bustypes.bustypes(ppc["bus"], ppc["gen"])

        path = join(DATA_DIR, self.case_name, "bustypes")
        ref_mp = mmread(join(path, "ref.mtx"))
        pv_mp = mmread(join(path, "pv.mtx"))
        pq_mp = mmread(join(path, "pq.mtx"))

        # Adjust for MATLAB 1 (one) based indexing.
        ref += 1
        pv += 1
        pq += 1

        self.assertTrue(self.equal(ref, ref_mp.T))
        self.assertTrue(self.equal(pv, pv_mp.T))
        self.assertTrue(self.equal(pq, pq_mp.T))


    def test_makeBdc(self):
        """Test B matrices and phase shift injections.
        """
        ppc = loadcase.loadcase(self.case_path)
        ppc = ext2int.ext2int(ppc)

        Bbus, Bf, Pbusinj, Pfinj = makeBdc.makeBdc(ppc["baseMVA"], ppc["bus"],
                                                   ppc["branch"])

        path = join(DATA_DIR, self.case_name, "makeBdc")

        Bbus_mp = mmread(join(path, "Bbus.mtx"))
        self.assertTrue(self.equal(Bbus.todense(), Bbus_mp.todense()))

        Bf_mp = mmread(join(path, "Bf.mtx"))
        self.assertTrue(self.equal(Bf.todense(), Bf_mp.todense()))

        Pbusinj_mp = mmread(join(path, "Pbusinj.mtx"))
        self.assertTrue(self.equal(Pbusinj, Pbusinj_mp))

        Pfinj_mp = mmread(join(path, "Pfinj.mtx"))
        self.assertTrue(self.equal(Pfinj, Pfinj_mp))


    def test_makeSbus(self):
        """Test vector of complex bus power injections.
        """
        ppc = loadcase.loadcase(self.case_path)
        ppc = ext2int.ext2int(ppc)

        Sbus = makeSbus.makeSbus(ppc["baseMVA"], ppc["bus"], ppc["gen"])

        path = join(DATA_DIR, self.case_name, "makeSbus")

        Sbus_mp = mmread(join(path, "Sbus.mtx"))
        self.assertTrue(self.equal(Sbus, Sbus_mp.T))


    def test_dcpf(self):
        """Test DC power flow.
        """
        ppc = loadcase.loadcase(self.case_path)
        ppc = ext2int.ext2int(ppc)
        ref, pv, pq = bustypes.bustypes(ppc["bus"], ppc["gen"])

        Bbus, _, _, _ = makeBdc.makeBdc(ppc["baseMVA"], ppc["bus"],
                                        ppc["branch"])

        Sbus = makeSbus.makeSbus(ppc["baseMVA"], ppc["bus"], ppc["gen"])

        Va0 = ppc["bus"][:, idx_bus.VA] * (pi / 180)
        Va = dcpf.dcpf(Bbus, Sbus.real, Va0, ref, pv, pq)

        path = join(DATA_DIR, self.case_name, "dcpf")

        Va_mp = mmread(join(path, "Va.mtx"))
        self.assertTrue(self.equal(Va, Va_mp.T))


    def test_int2ext(self):
        """Test conversion from internal to external indexing.
        """
        ppc = loadcase.loadcase(self.case_path)
        ppc = ext2int.ext2int(ppc)
        ppc = int2ext.int2ext(ppc)

        self.compare_case(ppc, "int2ext")


    def test_rundcpf(self):
        """ Test running a DC power flow.
        """
        ppopt = ppoption.ppoption
        ppopt['OUT_ALL'] = ppopt['VERBOSE'] = 0

        results, _ = rundcpf.rundcpf(self.case_path, ppopt)

        self.compare_case(results, "rundcpf")


    def compare_case(self, ppc, dir):
        """Compares the given case against MATPOWER data in the given directory.
        """
        # Adjust for MATLAB 1 (one) based indexing.
        ppc["bus"][:, idx_bus.BUS_I] += 1
        ppc["gen"][:, idx_gen.GEN_BUS] += 1
        ppc["branch"][:, idx_brch.F_BUS] += 1
        ppc["branch"][:, idx_brch.T_BUS] += 1

        path = join(DATA_DIR, self.case_name, dir)

        baseMVA_mp = mmread(join(path, "baseMVA.mtx"))
        self.assertAlmostEqual(ppc["baseMVA"], baseMVA_mp[0][0], self.places)

        if "version" in ppc:
            version_mp = mmread(join(path, "version.mtx"))
            self.assertEqual(ppc["version"], str(int(version_mp[0][0])))

        bus_mp = mmread(join(path, "bus.mtx"))
        self.assertTrue(self.equal(ppc["bus"], bus_mp), dir)

        gen_mp = mmread(join(path, "gen.mtx"))
        self.assertTrue(self.equal(ppc["gen"], gen_mp), dir)

        branch_mp = mmread(join(path, "branch.mtx"))
        self.assertTrue(self.equal(ppc["branch"], branch_mp), dir)

        if "areas" in ppc:
            areas_mp = mmread(join(path, "gencost.mtx"))
            self.assertTrue(self.equal(ppc["areas"], areas_mp), dir)

        if "gencost" in ppc:
            gencost_mp = mmread(join(path, "gencost.mtx"))
            self.assertTrue(self.equal(ppc["gencost"], gencost_mp), dir)


    def equal(self, a, b):
        """Returns True if two arrays are element-wise equal.
        """
        # If the following equation is element-wise True, then allclose returns
        # True.
        #
        # absolute(`a` - `b`) <= (`atol` + `rtol` * absolute(`b`))
        #
        # The above equation is not symmetric in `a` and `b`, so that
        # `allclose(a, b)` might be different from `allclose(b, a)` in
        # some rare cases.
        return allclose(a, b, self.rtol, self.atol)
