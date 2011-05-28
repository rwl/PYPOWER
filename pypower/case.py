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

from numpy import zeros, copy

class case(object):

    def __init__(self, version=2, baseMVA=100.0):
        self.version = version
        self.baseMVA = baseMVA
        self.bus = None
        self.gen = None
        self.branch = None
        self.gencost = None


bus_attr = [('bus_i', int), ('bus_type', int), ('Pd', float), ('Qd', float),
            ('Gs', float), ('Bs', float), ('bus_area', int),
            ('Vm', float), ('Va', float), ('baseKV', float), ('zone', int),
            ('Vmax', float), ('Vmin', float),
            ('lam_P', float), ('lam_Q', float),
            ('mu_Vmax', float), ('mu_Vmin', float)]


class bus_data(namedtuple('bus_data'), [attr for attr, _ in bus_attr]):

    __slots__ = ()

    @property
    def size(self):
        """Returns the number of buses.
        """
        return 0 if self.bus_i is None else self.bus_i.shape[0]


    def to_array(self):
        """Returns the bus data as array of floats.
        """
        data = zeros((self.size, len(self)), float)
        for i, attr in self:
            data[:, i] = getattr(self, attr)


    def from_array(self, data):
        """Set the bus data from an array of floats.
        """
        for i, (attr, typ) in bus_attr:
            setattr(self, attr, data[:, i].astype(typ))


    def copy(self, idx=None):
        """Returns a copy of the bus data.
        @param idx: Indexes of the buses to be copied. All bus data is copied
        if not specified.
        """
        return bus_data(*[copy(val[idx]) for val in self])


    def update(self, other, idx=None):
        """Updates the bus data given another BusData object.
        @param idx: Indexes of the buses to be updated. All buses are
        updated if not specified.
        """
        for i, val in enumerate(other):
            self[i] = copy(val[idx])


    def __getitem__(self, key):
        print "KEY:", key

        if not isinstance(key, int):
            raise TypeError
        if key > self.size():
            raise IndexError


#class BusData(object):
#
#    attr = ['bus_i', 'bus_type', 'Pd', 'Qd', 'Gs', 'Bs', 'bus_area',
#            'Vm', 'Va', 'baseKV', 'zone', 'Vmax', 'Vmin',
#            'lam_P', 'lam_Q', 'mu_Vmax', 'mu_Vmin']
#
#    def __init__(self):
#
#        for a in self.__class__.attr:
#            setattr(self, a, array([]))
#
#        # bus number (1 to 29997)
#        self.bus_i = array([])
#
#        # bus type
#        self.bus_type = array([])
#
#        # Pd, real power demand (MW)
#        self.Pd = array([])
#
#        # Qd, reactive power demand (MVAr)
#        self.Qd = array([])
#
#        # Gs, shunt conductance (MW at V = 1.0 p.u.)
#        self.Qd = array([])
#
#        # Bs, shunt susceptance (MVAr at V = 1.0 p.u.)
#        self.Bs = array([])
#
#        # area number, 1-100
#        self.bus_area = array([])
#
#        # Vm, voltage magnitude (p.u.)
#        self.Vm = array([])
#
#        # Va, voltage angle (degrees)
#        self.Va = array([])
#
#        # baseKV, base voltage (kV)
#        self.baseKV = array([])
#
#        # zone, loss zone (1-999)
#        self.zone = array([])
#
#        # maxVm, maximum voltage magnitude (p.u.)
#        self.Vmax = array([])
#
#        # minVm, minimum voltage magnitude (p.u.)
#        self.Vmin = array([])
#
#        # included in opf solution, not necessarily in input
#        # assume objective function has units, u
#
#        # Lagrange multiplier on real power mismatch (u/MW)
#        self.lamP = array([])
#
#        # Lagrange multiplier on reactive power mismatch (u/MVAr)
#        self.lamQ = array([])
#
#        # Kuhn-Tucker multiplier on upper voltage limit (u/p.u.)
#        self.mu_Vmax = array([])
#
#        # Kuhn-Tucker multiplier on lower voltage limit (u/p.u.)
#        self.mu_Vmin = array([])
