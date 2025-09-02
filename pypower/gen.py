# Copyright (c) 2025 Eudoxys Sciences LLC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Gen accessor

Generator Data
--------------

GEN_BUS        bus number
PG             Pg, real power output (MW)
QG             Qg, reactive power output (MVAr)
QMAX           Qmax, maximum reactive power output at Pmin (MVAr)
QMIN           Qmin, minimum reactive power output at Pmin (MVAr)
VG             Vg, voltage magnitude setpoint (p.u.)
MBASE          mBase, total MVA base of this machine, defaults to baseMVA
GEN_STATUS     status, 1 - machine in service, 0 - machine out of service
PMAX           Pmax, maximum real power output (MW)
PMIN           Pmin, minimum real power output (MW)
PC1            Pc1, lower real power output of PQ capability curve (MW)
PC2            Pc2, upper real power output of PQ capability curve (MW)
QC1MIN         Qc1min, minimum reactive power output at Pc1 (MVAr)
QC1MAX         Qc1max, maximum reactive power output at Pc1 (MVAr)
QC2MIN         Qc2min, minimum reactive power output at Pc2 (MVAr)
QC2MAX         Qc2max, maximum reactive power output at Pc2 (MVAr)
RAMP_AGC       ramp rate for load following/AGC (MW/min)
RAMP_10        ramp rate for 10 minute reserves (MW)
RAMP_30        ramp rate for 30 minute reserves (MW)
RAMP_Q         ramp rate for reactive power (2 sec timescale) (MVAr/min)
APF            area participation factor

Set after OPF solution
----------------------

MU_PMAX (RO)   Kuhn-Tucker multiplier on upper Pg limit (u/MW)
MU_PMIN (RO)   Kuhn-Tucker multiplier on lower Pg limit (u/MW)
MU_QMAX (RO)   Kuhn-Tucker multiplier on upper Qg limit (u/MVAr)
MU_QMIN (RO)   Kuhn-Tucker multiplier on lower Qg limit (u/MVAr)

"""

from typing import TypeVar
import pypower.idx_gen as gen
import numpy as np
from data import Data

class Gen(Data):
    "Generation data accessor"
    datatype = "gen"
    readonly = ["LAM_P","LAM_Q","MU_VMAX","MU_VMIN"]

    def __init__(self,
            case:TypeVar('Case'),
            ref:int|float|np.float64,
            ):
        """Generator data access constructor

        Parameters:

        * case: Case object for Generator data
        * ref: Generator data index
        """
        super().__init__(case,ref,gen)

    # GEN_BUS
    @property
    def GEN_BUS(self):
        return int(self.get("GEN_BUS"))
    @GEN_BUS.setter
    def GEN_BUS(self,value:int|float|np.float64):
        self.set("GEN_BUS",value,check=isinstance(value,(int,float,np.float64)))

    # PG
    @property
    def PG(self):
        return self.get("PG")
    @PG.setter
    def PG(self,value:int|float|np.float64):
        self.set("PG",value,check=isinstance(value,(int,float,np.float64)))

    # QG
    @property
    def QG(self):
        return self.get("QG")
    @QG.setter
    def QG(self,value:int|float|np.float64):
        self.set("QG",value,check=isinstance(value,(int,float,np.float64)))

    # QMAX
    @property
    def QMAX(self):
        return self.get("QMAX")
    @QMAX.setter
    def QMAX(self,value:int|float|np.float64):
        self.set("QMAX",value,check=isinstance(value,(int,float,np.float64)))

    # QMIN
    @property
    def QMIN(self):
        return self.get("QMIN")
    @QMIN.setter
    def QMIN(self,value:int|float|np.float64):
        self.set("QMIN",value,check=isinstance(value,(int,float,np.float64)))

    # VG
    @property
    def VG(self):
        return self.get("VG")
    @VG.setter
    def VG(self,value:int|float|np.float64):
        self.set("VG",value,check=isinstance(value,(int,float,np.float64)))

    # MBASE
    @property
    def MBASE(self):
        return self.get("MBASE")
    @MBASE.setter
    def MBASE(self,value:int|float|np.float64):
        self.set("MBASE",value,check=isinstance(value,(int,float,np.float64)))

    # GEN_STATUS
    @property
    def GEN_STATUS(self):
        return self.get("GEN_STATUS")
    @GEN_STATUS.setter
    def GEN_STATUS(self,value:int|float|np.float64):
        self.set("GEN_STATUS",value,check=isinstance(value,int) and value in [0,1])

    # PMAX
    @property
    def PMAX(self):
        return self.get("PMAX")
    @PMAX.setter
    def PMAX(self,value:int|float|np.float64):
        self.set("PMAX",value,check=isinstance(value,(int,float,np.float64)))

    # PMIN
    @property
    def PMIN(self):
        return self.get("PMIN")
    @PMIN.setter
    def PMIN(self,value:int|float|np.float64):
        self.set("PMIN",value,check=isinstance(value,(int,float,np.float64)))

    # PC1
    @property
    def PC1(self):
        return self.get("PC1")
    @PC1.setter
    def PC1(self,value:int|float|np.float64):
        self.set("PC1",value,check=isinstance(value,(int,float,np.float64)))

    # PC2
    @property
    def PC2(self):
        return self.get("PC2")
    @PC2.setter
    def PC2(self,value:int|float|np.float64):
        self.set("PC2",value,check=isinstance(value,(int,float,np.float64)))

    # QC1MIN
    @property
    def QC1MIN(self):
        return self.get("QC1MIN")
    @QC1MIN.setter
    def QC1MIN(self,value:int|float|np.float64):
        self.set("QC1MIN",value,check=isinstance(value,(int,float,np.float64)))

    # QC1MAX
    @property
    def QC1MAX(self):
        return self.get("QC1MAX")
    @QC1MAX.setter
    def QC1MAX(self,value:int|float|np.float64):
        self.set("QC1MAX",value,check=isinstance(value,(int,float,np.float64)))

    # QC2MIN
    @property
    def QC2MIN(self):
        return self.get("QC2MIN")
    @QC2MIN.setter
    def QC2MIN(self,value:int|float|np.float64):
        self.set("QC2MIN",value,check=isinstance(value,(int,float,np.float64)))

    # QC2MAX
    @property
    def QC2MAX(self):
        return self.get("QC2MAX")
    @QC2MAX.setter
    def QC2MAX(self,value:int|float|np.float64):
        self.set("QC2MAX",value)

    # RAMP_AGC
    @property
    def RAMP_AGC(self):
        return self.get("RAMP_AGC")
    @RAMP_AGC.setter
    def RAMP_AGC(self,value:int|float|np.float64):
        self.set("RAMP_AGC",value,check=isinstance(value,(int,float,np.float64)))

    # RAMP_10
    @property
    def RAMP_10(self):
        return self.get("RAMP_10")
    @RAMP_10.setter
    def RAMP_10(self,value:int|float|np.float64):
        self.set("RAMP_10",value,check=isinstance(value,(int,float,np.float64)))

    # RAMP_30
    @property
    def RAMP_30(self):
        return self.get("RAMP_30")
    @RAMP_30.setter
    def RAMP_30(self,value:int|float|np.float64):
        self.set("RAMP_30",value,check=isinstance(value,(int,float,np.float64)))

    # RAMP_Q
    @property
    def RAMP_Q(self):
        return self.get("RAMP_Q")
    @RAMP_Q.setter
    def RAMP_Q(self,value:int|float|np.float64):
        self.set("RAMP_Q",value,check=isinstance(value,(int,float,np.float64)))

    # APF
    @property
    def APF(self):
        return self.get("APF")
    @APF.setter
    def APF(self,value:int|float|np.float64):
        self.set("APF",value,check=isinstance(value,(int,float,np.float64)))

    # MU_PMAX
    @property
    def MU_PMAX(self):
        return self.get("MU_PMAX")

    # MU_PMIN
    @property
    def MU_PMIN(self):
        return self.get("MU_PMIN")

    # MU_QMAX
    @property
    def MU_QMAX(self):
        return self.get("MU_QMAX")
    @MU_QMAX.setter

    # MU_QMIN
    @property
    def MU_QMIN(self):
        return self.get("MU_QMIN")
