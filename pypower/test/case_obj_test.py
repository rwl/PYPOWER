# Copyright (C) 2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

import unittest

from numpy import array, ones

from pypower.case import Case, BusData

from pypower.idx_bus import BUS_I, LAM_P, PD, QD, VMIN


class CaseObjTest(unittest.TestCase):

    def test_case_init(self):
        self.assertRaises(TypeError, Case)
        self.assertRaises(TypeError, Case, self.bus_array)
        self.assertRaises(TypeError, Case, self.bus_array, self.gen_array)


    def test_case_pf(self):
        c = Case(self.bus_array, self.gen_array_v2, self.branch_array_v2)

        self.assertEqual(c.baseMVA, 100.0)
        self.assertEqual(c.version, "2")
        self.assertNotEqual(c.bus, None)
        self.assertNotEqual(c.gen, None)
        self.assertNotEqual(c.branch, None)
        self.assertEqual(c.areas, None)
        self.assertEqual(c.gencost, None)


    def test_case_opf(self):
        c = Case(self.bus_array, self.gen_array_v2, self.branch_array_v2,
                 self.areas_array, self.gencost_array)

        self.assertEqual(c.baseMVA, 100.0)
        self.assertEqual(c.version, "2")
        self.assertNotEqual(c.bus, None)
        self.assertNotEqual(c.gen, None)
        self.assertNotEqual(c.branch, None)
        self.assertNotEqual(c.areas, None)
        self.assertNotEqual(c.gencost, None)


    def test_case_pf_v1(self):
        c = Case(self.bus_array, self.gen_array, self.branch_array,
                 baseMVA=10.0, version='1')

        self.assertEqual(c.baseMVA, 10.0)
        self.assertEqual(c.version, "1")
        self.assertNotEqual(c.bus, None)
        self.assertNotEqual(c.gen, None)
        self.assertNotEqual(c.branch, None)
        self.assertEqual(c.areas, None)
        self.assertEqual(c.gencost, None)


    def test_case_opf_v1(self):
        c = Case(self.bus_array, self.gen_array, self.branch_array,
                 self.areas_array, self.gencost_array, 10.0, '1')

        self.assertEqual(c.baseMVA, 10.0)
        self.assertEqual(c.version, "1")
        self.assertNotEqual(c.bus, None)
        self.assertNotEqual(c.gen, None)
        self.assertNotEqual(c.branch, None)
        self.assertNotEqual(c.areas, None)
        self.assertNotEqual(c.gencost, None)


    def test_bus_data_init(self):
        self.assertRaises(TypeError, BusData)


    def test_bus_data_size(self):
        bus = BusData(self.bus_array)
        self.assertEqual(bus.size, self.bus_array_size)


    def test_bus_data_type(self):
        bus = BusData(self.bus_array)

        self.assertTrue(isinstance(bus.bus_i[0], int))
        self.assertTrue(isinstance(bus.bus_type[0], int))
        self.assertTrue(isinstance(bus.Pd[0], float))
        self.assertTrue(isinstance(bus.bus_area[0], int))


#    def test_bus_data_getitem_index_int(self):
#        """Test indexing bus data with single integer.
#        """
#        bus = BusData(self.bus_array)
#
#        bus0 = bus[0]
#
#        self.assertTrue(isinstance(bus0[0], float))
#        self.assertEqual(bus0.shape, (self.bus_array.shape[1], ))
#        self.assertEqual(bus0[VMIN], self.bus_array[0, VMIN])
#
#        try:
#            bus[self.bus_array_size + 10]
#        except IndexError:
#            pass
#        except Exception, e:
#            self.fail(e.message)




    def test_bus_data_getitem_index_col(self):
        bus = BusData(self.bus_array)

        bus_i = bus[:, BUS_I]

        self.assertTrue(isinstance(bus_i[0], int))
        self.assertEqual(bus_i.shape, (self.bus_array_size, ))
        self.assertEqual(bus_i[2], self.bus_array[2, BUS_I])


    def test_bus_data_getitem_list_index_col(self):
        bus = BusData(self.bus_array)

        idx = [4, 6, 8]
        Pd = bus[idx, PD]
        self.assertTrue(isinstance(Pd[0], float))
        self.assertEqual(Pd.shape, (len(idx), ))
        for i, ix in enumerate(idx):
            self.assertEqual(Pd[i], self.bus_array[ix, PD])


    def test_bus_data_getitem_index_error(self):
        bus = BusData(self.bus_array)

        try:
            bus[:, LAM_P]
        except IndexError:
            pass
        except Exception, e:
            self.fail(e.message)


    def test_bus_data_setitem_element(self):
        """Test setting the value of a single bus data element.
        """
        bus = BusData(self.bus_array)

        idx = 4
        new_val = 110.0
        bus[idx, PD] = new_val

        self.assertTrue(isinstance(bus.Pd[idx], float))
        self.assertEqual(bus.Pd.shape, (self.bus_array_size, ))
        self.assertEqual(bus.Pd[idx], new_val)


    def test_bus_data_setitem_col(self):
        """Test setting the value of a bus data column.
        """
        bus = BusData(self.bus_array)

        new_col = -1 * ones(self.bus_array_size, int)  # check type conversion
        bus[:, QD] = new_col

        test_idx = 0
        self.assertTrue(isinstance(bus.Qd[test_idx], float))
        self.assertEqual(bus.Qd.shape, (self.bus_array_size, ))
        self.assertEqual(bus.Qd[test_idx], -1)


    def test_bus_data_setitem_list_index_col(self):
        """Test setting values of bus data column elements.
        """
        bus = BusData(self.bus_array)

        idx = [4, 6]
        new_val = -1 * ones(len(idx))
        bus[idx, PD] = new_val

        self.assertTrue(isinstance(bus.Pd[0], float))
        self.assertEqual(bus.Pd.shape, (self.bus_array_size, ))
        for i in idx:
            self.assertEqual(bus.Pd[i], -1)
        self.assertEqual(bus.Pd[8], 125)


    def test_bus_data_setitem_col_slice(self):
        """Test setting multiple columns of bus data.
        """
        bus = BusData(self.bus_array)

        new_val = -1 * ones((self.bus_array_size, 2), int)

        bus[:, PD:QD + 1] = new_val

        test_idx = 0
        self.assertTrue(isinstance(bus.Pd[test_idx], float))
        self.assertTrue(isinstance(bus.Qd[test_idx], float))
        self.assertEqual(bus.Pd.shape, (self.bus_array_size, ))
        self.assertEqual(bus.Qd.shape, (self.bus_array_size, ))
        self.assertEqual(bus.Pd[test_idx], -1)
        self.assertEqual(bus.Qd[test_idx], -1)


#    def test_bus_data_setitem_col_slice(self):
#        bus = BusData(self.bus_array)
#
#        Sd = bus[:, PD:QD + 1]
#
#        self.assertTrue(isinstance(Sd[0, 0], float))
#        self.assertEqual(Sd.shape, (self.bus_array_size, 2))
#        self.assertEqual(Sd[4, 0], self.bus_array[4, PD])


    def setUp(self):
        self.bus_array = array([
            [1,  3, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [2,  2, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [30, 2, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [4,  1, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [5,  1, 90,  30, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [6,  1, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [7,  1, 100, 35, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [8,  1, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [9,  1, 125, 50, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9]
        ])

        self.bus_array_size = self.bus_array.shape[0]

        self.gen_array = array([
            [1,  0,   0, 300, -300, 1, 100, 1, 250, 90],
            [2,  163, 0, 300, -300, 1, 100, 1, 300, 10],
            [30, 85,  0, 300, -300, 1, 100, 1, 270, 10]
        ], float)

        self.gen_array_v2 = array([
            [1,  0,   0, 300, -300, 1, 100, 1, 250, 90, 0, 0,    0,  0,   0,  0,  0, 0, 0, 0, 0],
            [2,  163, 0, 300, -300, 1, 100, 1, 300, 10, 0, 200, -20, 20, -10, 10, 0, 0, 0, 0, 0],
            [30, 85,  0, 300, -300, 1, 100, 1, 270, 10, 0, 200, -30, 30, -15, 15, 0, 0, 0, 0, 0]
        ])

        self.branch_array = array([
            [1,  4, 0,      0.0576, 0,       0, 250, 250, 0, 0, 1],
            [4,  5, 0.017,  0.092,  0.158,   0, 250, 250, 0, 0, 1],
            [5,  6, 0.039,  0.17,   0.358, 150, 150, 150, 0, 0, 1],
            [30, 6, 0,      0.0586, 0,       0, 300, 300, 0, 0, 1],
            [6,  7, 0.0119, 0.1008, 0.209,  40, 150, 150, 0, 0, 1],
            [7,  8, 0.0085, 0.072,  0.149, 250, 250, 250, 0, 0, 1],
            [8,  2, 0,      0.0625, 0,     250, 250, 250, 0, 0, 1],
            [8,  9, 0.032,  0.161,  0.306, 250, 250, 250, 0, 0, 1],
            [9,  4, 0.01,   0.085,  0.176, 250, 250, 250, 0, 0, 1]
        ])

        self.branch_array_v2 = array([
            [1,  4, 0,      0.0576, 0,       0, 250, 250, 0, 0, 1, -360, 2.48],
            [4,  5, 0.017,  0.092,  0.158,   0, 250, 250, 0, 0, 1, -360, 360],
            [5,  6, 0.039,  0.17,   0.358, 150, 150, 150, 0, 0, 1, -360, 360],
            [30, 6, 0,      0.0586, 0,       0, 300, 300, 0, 0, 1, -360, 360],
            [6,  7, 0.0119, 0.1008, 0.209,  40, 150, 150, 0, 0, 1, -360, 360],
            [7,  8, 0.0085, 0.072,  0.149, 250, 250, 250, 0, 0, 1, -360, 360],
            [8,  2, 0,      0.0625, 0,     250, 250, 250, 0, 0, 1, -360, 360],
            [8,  9, 0.032,  0.161,  0.306, 250, 250, 250, 0, 0, 1, -360, 360],
            [9,  4, 0.01,   0.085,  0.176, 250, 250, 250, 0, 0, 1, -2,   360]
        ])

        self.areas_array = array([
            [1, 5]
        ])

        self.gencost_array = array([
            [1, 0, 0, 4,  0,        0,   100, 2500, 200, 5500, 250, 7250],
            [2, 0, 0, 2, 24.035, -403.5,   0,    0,   0,    0,   0,    0],
            [1, 0, 0, 3,  0,        0,   200, 3000, 300, 5000,   0,    0]
        ])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()