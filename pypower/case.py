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

from collections import namedtuple

from numpy import ndarray, array

from pypower.idx_bus import \
    BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, VA, BASE_KV, ZONE, \
    VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN

class Case(object):

    def __init__(self, bus_data, gen_data, branch_data, areas_data=None,
                 gencost_data=None, baseMVA=100.0, version='2'):
        self.version = version
        self.baseMVA = baseMVA

        if isinstance(bus_data, ndarray):
            self.bus = BusData(bus_data)
        else:
            self.bus = bus_data

        if isinstance(gen_data, ndarray):
            self.gen = GenData(gen_data)
        else:
            self.gen = gen_data

        if isinstance(branch_data, ndarray):
            self.branch = BranchData(branch_data)
        else:
            self.branch = branch_data

        if isinstance(areas_data, ndarray):
            self.areas = AreasData(areas_data)
        else:
            self.areas = areas_data

        if isinstance(gencost_data, ndarray):
            self.gencost = GenCostData(gencost_data)
        else:
            self.gencost = gencost_data


class BusData(object):

    attrs = [('bus_i', int), ('bus_type', int), ('Pd', float), ('Qd', float),
                ('Gs', float), ('Bs', float), ('bus_area', int),
                ('Vm', float), ('Va', float), ('baseKV', float), ('zone', int),
                ('Vmax', float), ('Vmin', float),
                ('lam_P', float), ('lam_Q', float),
                ('mu_Vmax', float), ('mu_Vmin', float)]

    def __init__(self, bus_data):
        assert isinstance(bus_data, ndarray)

        # bus number (1 to 29997)
        self.bus_i = bus_data[:, BUS_I].astype(int)

        # bus type
        self.bus_type = bus_data[:, BUS_TYPE].astype(int)

        # Pd, real power demand (MW)
        self.Pd = bus_data[:, PD]

        # Qd, reactive power demand (MVAr)
        self.Qd = bus_data[:, QD]

        # Gs, shunt conductance (MW at V = 1.0 p.u.)
        self.Gs = bus_data[:, GS]

        # Bs, shunt susceptance (MVAr at V = 1.0 p.u.)
        self.Bs = bus_data[:, BS]

        # area number, 1-100
        self.bus_area = bus_data[:, BUS_AREA].astype(int)

        # Vm, voltage magnitude (p.u.)
        self.Vm = bus_data[:, VM]

        # Va, voltage angle (degrees)
        self.Va = bus_data[:, VA]

        # baseKV, base voltage (kV)
        self.baseKV = bus_data[:, BASE_KV]

        # zone, loss zone (1-999)
        self.zone = bus_data[:, ZONE].astype(int)

        # maxVm, maximum voltage magnitude (p.u.)
        self.Vmax = bus_data[:, VMAX]

        # minVm, minimum voltage magnitude (p.u.)
        self.Vmin = bus_data[:, VMIN]

        # included in opf solution, not necessarily in input
        # assume objective function has units, u
        ncol = bus_data.shape[1]

        # Lagrange multiplier on real power mismatch (u/MW)
        self.lam_P = bus_data[:, LAM_P] if ncol > LAM_P else None

        # Lagrange multiplier on reactive power mismatch (u/MVAr)
        self.lam_Q = bus_data[:, LAM_Q] if ncol > LAM_P else None

        # Kuhn-Tucker multiplier on upper voltage limit (u/p.u.)
        self.mu_Vmax = bus_data[:, MU_VMAX] if ncol > LAM_P else None

        # Kuhn-Tucker multiplier on lower voltage limit (u/p.u.)
        self.mu_Vmin = bus_data[:, MU_VMIN] if ncol > LAM_P else None


    def __getitem__(self, key):
        print "KEY:", key

        if isinstance(key, tuple):
            if isinstance(key[1], int):
                val = getattr(self, self.attrs[key[1]][0])
                if val is not None:
                    return val[key[0]]
                else:
                    raise IndexError, 'index out of bounds'
            else:
                attrs = self.attrs[key[1]]
                print "ATTRS:", attrs


    @property
    def size(self):
        """Returns the number of buses.
        """
        return 0 if self.bus_i is None else self.bus_i.shape[0]




class GenData(object):

    def __init__(self, gen_data):
        pass


class BranchData(object):

    def __init__(self, branch_data):
        pass


class AreasData(object):

    def __init__(self, areas_data):
        pass


class GenCostData(object):

    def __init__(self, gencost_data):
        pass


#bus_attr = [('bus_i', int), ('bus_type', int), ('Pd', float), ('Qd', float),
#            ('Gs', float), ('Bs', float), ('bus_area', int),
#            ('Vm', float), ('Va', float), ('baseKV', float), ('zone', int),
#            ('Vmax', float), ('Vmin', float),
#            ('lam_P', float), ('lam_Q', float),
#            ('mu_Vmax', float), ('mu_Vmin', float)]


#class BusData(namedtuple('bus_data'), [attr for attr, _ in bus_attr]):
#
#    __slots__ = ()
#
#    @property
#    def size(self):
#        """Returns the number of buses.
#        """
#        return 0 if self.bus_i is None else self.bus_i.shape[0]
#
#
#    def to_array(self):
#        """Returns the bus data as array of floats.
#        """
#        data = zeros((self.size, len(self)), float)
#        for i, attr in self:
#            data[:, i] = getattr(self, attr)
#
#
#    def from_array(self, data):
#        """Set the bus data from an array of floats.
#        """
#        for i, (attr, typ) in bus_attr:
#            setattr(self, attr, data[:, i].astype(typ))
#
#
#    def copy(self, idx=None):
#        """Returns a copy of the bus data.
#        @param idx: Indexes of the buses to be copied. All bus data is copied
#        if not specified.
#        """
#        return bus_data(*[copy(val[idx]) for val in self])
#
#
#    def update(self, other, idx=None):
#        """Updates the bus data given another BusData object.
#        @param idx: Indexes of the buses to be updated. All buses are
#        updated if not specified.
#        """
#        for i, val in enumerate(other):
#            self[i] = copy(val[idx])
#
#
#    def __getitem__(self, key):
#        print "KEY:", key
#
#        if not isinstance(key, int):
#            raise TypeError
#        if key > self.size():
#            raise IndexError

