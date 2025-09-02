# Copyright (c) 2025 Eudoxys Sciences LLC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Bus accessor

Bus Data
--------

BUS_I (RO)     Bus number (1 to 29997)
BUS_TYPE       Bus type (see Bus Types below)
PD             Real power demand (MW)
QD             Reactive power demand (MVAr)
GS             Shunt conductance (MW at V = 1.0 p.u.)
BS             Shunt susceptance (MVAr at V = 1.0 p.u.)
BUS_AREA       Area number, 1-100
VM             Vm, voltage magnitude (p.u.)
VA             Va, voltage angle (degrees)
BASE_KV        Base voltage (kV)
ZONE           Zone, loss zone (1-999)
VMAX           MaxVm, maximum voltage magnitude (p.u.)
VMIN           MinVm, minimum voltage magnitude (p.u.)

Set after powerflow solution
----------------------------

LAM_P (RO)     Lagrange multiplier on real power mismatch (u/MW)
LAM_Q (RO)     Lagrange multiplier on reactive power mismatch (u/MVAr)
MU_VMAX (RO)   Kuhn-Tucker multiplier on upper voltage limit (u/p.u.)
MU_VMIN (RO)   Kuhn-Tucker multiplier on lower voltage limit (u/p.u.)

Bus Types
---------

PQ      PQ bus
PV      PV bus
REF     Reference bus
NONE    Isolated bus

"""

from typing import TypeVar
import pypower.idx_bus as bus
import numpy as np
from data import Data

class Bus(Data):
    """Bus data accessor"""
    datatype = "bus"
    readonly = ["BUS_I","LAM_P","LAM_Q","MU_VMAX","MU_VMIN"]

    def __init__(self,
            case:TypeVar('Case'),
            ref:int|float|np.float64,
            ):
        """Bus data access constructor

        Parameters
        ----------

        * case: Case object for bus data
        * ref: Bus data index
        """
        super().__init__(case,ref,bus)

    # BUS_I
    @property
    def BUS_I(self):
        return int(self.get("BUS_I"))

    # BUS_TYPE
    @property
    def BUS_TYPE(self):
        return int(self.get("BUS_TYPE"))
    @BUS_TYPE.setter
    def BUS_TYPE(self,value:int):
        self.set("BUS_TYPE",value,check=isinstance(value,int) and value in [bus.PQ,bus.PV,bus.REF,bus.NONE])

    # PD
    @property
    def PD(self):
        return self.get("PD")
    @PD.setter
    def PD(self,value:int|float|np.float64):
        self.set("PD",value,check=isinstance(value,(int,float,np.float64)))

    # QD
    @property
    def QD(self):
        return self.get("QD")
    @QD.setter
    def QD(self,value:int|float|np.float64):
        self.set("QD",value,check=isinstance(value,(int,float,np.float64)))

    # GS
    @property
    def GS(self):
        return self.get("GS")
    @GS.setter
    def GS(self,value:int|float|np.float64):
        self.set("GS",value,check=isinstance(value,(int,float,np.float64)))

    # BS
    @property
    def BS(self):
        return self.get("BS")
    @BS.setter
    def BS(self,value:int|float|np.float64):
        self.set("BS",value,check=isinstance(value,(int,float,np.float64)))

    # BUS_AREA
    @property
    def BUS_AREA(self):
        return int(self.get("BUS_AREA"))
    @BUS_AREA.setter
    def BUS_AREA(self,value:int):
        self.set("BUS_AREA",value,check=isinstance(value,int))

    # VM
    @property
    def VM(self):
        return self.get("VM")
    @VM.setter
    def VM(self,value:int|float|np.float64):
        self.set("VM",value,check=isinstance(value,(int,float,np.float64)))

    # VA
    @property
    def VA(self):
        return self.get("VA")
    @VA.setter
    def VA(self,value:int|float|np.float64):
        self.set("VA",value,check=isinstance(value,(int,float,np.float64)))

    # BASE_KV
    @property
    def BASE_KV(self):
        return self.get("BASE_KV")
    @BASE_KV.setter
    def BASE_KV(self,value:int|float|np.float64):
        self.set("BASE_KV",value,check=isinstance(value,(int,float,np.float64)))

    # ZONE
    @property
    def ZONE(self):
        return int(self.get("ZONE"))
    @ZONE.setter
    def ZONE(self,value:int):
        self.set("ZONE",value,check=isinstance(value,int))

    # VMAX
    @property
    def VMAX(self):
        return self.get("VMAX")
    @VMAX.setter
    def VMAX(self,value:int|float|np.float64):
        self.set("VMAX",value,check=isinstance(value,(int,float,np.float64)))

    # VMIN
    @property
    def VMIN(self):
        return self.get("VMIN")
    @VMIN.setter
    def VMIN(self,value:int|float|np.float64):
        self.set("VMIN",value,check=isinstance(value,(int,float,np.float64)))

    # LAM_P
    @property
    def LAM_P(self):
        return self.get("LAM_P")

    # LAM_Q
    @property
    def LAM_Q(self):
        return self.get("LAM_Q")

    # MU_VMAX
    @property
    def MU_VMAX(self):
        return self.get("MU_VMAX")

    # MU_VMIN
    @property
    def MU_VMIN(self):
        return self.get("MU_VMIN")
