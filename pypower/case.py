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

from numpy import ndarray, array, r_

from pypower.idx_bus import \
    BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, VA, BASE_KV, ZONE, \
    VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN

from pypower.idx_gen import \
    GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN, PC1, PC2, \
    QC1MIN, QC1MAX, QC2MIN, QC2MAX, RAMP_AGC, RAMP_10, RAMP_30, RAMP_Q, APF, \
    MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN

class case(object):

    def __init__(self):
        self.baseMVA = 100.0

        self.bus = None
        self.gen = None
        self.branch = None
#        self.areas = None
#        self.gencost = None


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


class _BaseData(object):

    def __getitem__(self, key):
        if isinstance(key, tuple):
            row, col = key
            attr = self._attrs[col]
            val = getattr(self, attr)
            if val is not None:
                return val[row]
            else:
                raise IndexError, 'index out of bounds'
#        elif isinstance(key, int):
#            a = array([])
#            for attr in self._attrs:
#                val = getattr(self, attr)
#                if val is not None:
#                    a = r_[a, val[key]]
#            return a
        else:
            raise TypeError, 'key is of an inappropriate type'


    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            row, col = key
            if isinstance(col, int):
                attr = self._attrs[col]
                val = getattr(self, attr)
                if val is not None:
                    val[row] = value
                else:
                    raise IndexError, 'index out of bounds'
            elif isinstance(col, slice):
                attrs = self._attrs[col]
                for i, attr in enumerate(attrs):
                    val = getattr(self, attr)
                    if val is not None:
                        val[row] = value[row, i]
                    else:
                        raise IndexError, 'index out of bounds'
            else:
                raise TypeError, 'key is of an inappropriate type'
        else:
            raise TypeError, 'key is of an inappropriate type'


class BusData(_BaseData):

#    attrs = [('bus_i', int), ('bus_type', int), ('Pd', float), ('Qd', float),
#                ('Gs', float), ('Bs', float), ('bus_area', int),
#                ('Vm', float), ('Va', float), ('baseKV', float), ('zone', int),
#                ('Vmax', float), ('Vmin', float),
#                ('lam_P', float), ('lam_Q', float),
#                ('mu_Vmax', float), ('mu_Vmin', float)]

    _attrs = ['bus_i', 'bus_type', 'Pd', 'Qd', 'Gs', 'Bs', 'bus_area',
             'Vm', 'Va', 'baseKV', 'zone', 'Vmax', 'Vmin',
             'lam_P', 'lam_Q', 'mu_Vmax', 'mu_Vmin']

    def __init__(self, bus_data):
        assert isinstance(bus_data, ndarray)

        # bus number (1 to 29997)
        self.bus_i = bus_data[:, BUS_I].astype(int)

        # bus type
        self.bus_type = bus_data[:, BUS_TYPE].astype(int)

        # Real power demand (MW)
        self.Pd = bus_data[:, PD]

        # Reactive power demand (MVAr)
        self.Qd = bus_data[:, QD]

        # Shunt conductance (MW at V = 1.0 p.u.)
        self.Gs = bus_data[:, GS]

        # Shunt susceptance (MVAr at V = 1.0 p.u.)
        self.Bs = bus_data[:, BS]

        # Area number, 1-100
        self.bus_area = bus_data[:, BUS_AREA].astype(int)

        # Voltage magnitude (p.u.)
        self.Vm = bus_data[:, VM]

        # Voltage angle (degrees)
        self.Va = bus_data[:, VA]

        # Base voltage (kV)
        self.baseKV = bus_data[:, BASE_KV]

        # Loss zone (1-999)
        self.zone = bus_data[:, ZONE].astype(int)

        # Maximum voltage magnitude (p.u.)
        self.Vmax = bus_data[:, VMAX]

        # Minimum voltage magnitude (p.u.)
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


    @property
    def size(self):
        """Returns the number of buses.
        """
        return 0 if self.bus_i is None else self.bus_i.shape[0]


class GenData(_BaseData):

    attrs = ['bus', 'Pg', 'Qg', 'Qmax', 'Qmin', 'Vg', 'mBase', 'status',
        'Pmax', 'Pmin', 'Pc1', 'Pc2', 'Qc1min', 'Qc1max', 'Qc2min', 'Qc2max',
        'ramp_acg', 'ramp_10', 'ramp_30', 'ramp_q', 'apf', 'mu_Pmax', 'mu_Pmin',
        'mu_Qmax', 'mu_Qmin']

    def __init__(self, gen_data):

        # Bus number
        self.bus = gen_data[:, GEN_BUS].astype(int)

        # Real power output (MW)
        self.Pg = gen_data[:, PG]

        # Reactive power output (MVAr)
        self.Qg = gen_data[:, QG]

        # Maximum reactive power output at Pmin (MVAr)
        self.Qmax = gen_data[:, QMAX]

        # Minimum reactive power output at Pmin (MVAr)
        self.Qmin = gen_data[:, QMIN]

        # Voltage magnitude setpoint (p.u.)
        self.Vg = gen_data[:, VG]

        # Total MVA base of this machine, defaults to baseMVA
        self.mBase = gen_data[:, MBASE]

        # 1 - machine in service, 0 - machine out of service
        self.status = gen_data[:, GEN_STATUS].astype(int)

        # Maximum real power output (MW)
        self.Pmax = gen_data[:, PMAX]

        # Minimum real power output (MW)
        self.Pmin = gen_data[:, PMIN]

        ncol = gen_data.shape[1]

        # Lower real power output of PQ capability curve (MW)
        self.Pc1 = None if ncol > PC1 else gen_data[:, PC1]

        # Upper real power output of PQ capability curve (MW)
        self.Pc2 = None if ncol > PC1 else gen_data[:, PC2]

        # Minimum reactive power output at Pc1 (MVAr)
        self.Qc1min = None if ncol > PC1 else gen_data[:, QC1MIN]

        # Maximum reactive power output at Pc1 (MVAr)
        self.Qc1max = None if ncol > PC1 else gen_data[:, QC1MAX]

        # Minimum reactive power output at Pc2 (MVAr)
        self.Qc2min = None if ncol > PC1 else gen_data[:, QC2MIN]

        # Maximum reactive power output at Pc2 (MVAr)
        self.Qc2max = None if ncol > PC1 else gen_data[:, QC2MAX]

        # Ramp rate for load following/AGC (MW/min)
        self.ramp_acg = None if ncol > PC1 else gen_data[:, RAMP_AGC]

        # Ramp rate for 10 minute reserves (MW)
        self.ramp_10 = None if ncol > PC1 else gen_data[:, RAMP_10]

        # Ramp rate for 30 minute reserves (MW)
        self.ramp_30 = None if ncol > PC1 else gen_data[:, RAMP_30]

        # Ramp rate for reactive power (2 sec timescale) (MVAr/min)
        self.ramp_q = None if ncol > PC1 else gen_data[:, RAMP_Q]

        # Area participation factor
        self.apf = None if ncol > PC1 else gen_data[:, APF]

        # Included in opf solution, not necessarily in input
        # assume objective function has units, u

        # Kuhn-Tucker multiplier on upper Pg limit (u/MW)
        self.mu_Pmax = None if ncol > MU_PMAX else gen_data[:, MU_PMAX]

        # Kuhn-Tucker multiplier on lower Pg limit (u/MW)
        self.mu_Pmin = None if ncol > MU_PMAX else gen_data[:, MU_PMIN]

        # Kuhn-Tucker multiplier on upper Qg limit (u/MVAr)
        self.mu_Qmax = None if ncol > MU_PMAX else gen_data[:, MU_QMAX]

        # Kuhn-Tucker multiplier on lower Qg limit (u/MVAr)
        self.mu_Qmin = None if ncol > MU_PMAX else gen_data[:, MU_QMIN]


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

