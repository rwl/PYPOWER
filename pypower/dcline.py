# Copyright (c) 2025 Eudoxys Sciences LLC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Dcline accessor

DC Line Data
------------

F_BUS            f, "from" bus number
T_BUS            t,  "to"  bus number
BR_STATUS        initial branch status, 1 - in service, 0 - out of service
PF               MW flow at "from" bus ("from" -> "to")
PT               MW flow at  "to"  bus ("from" -> "to")
QF               MVAr injection at "from" bus ("from" -> "to")
QT               MVAr injection at  "to"  bus ("from" -> "to")
VF               voltage setpoint at "from" bus (p.u.)
VT               voltage setpoint at  "to"  bus (p.u.)
PMIN             lower limit on PF (MW flow at "from" end)
PMAX            upper limit on PF (MW flow at "from" end)
QMINF           lower limit on MVAr injection at "from" bus
QMAXF           upper limit on MVAr injection at "from" bus
QMINT           lower limit on MVAr injection at  "to"  bus
QMAXT           upper limit on MVAr injection at  "to"  bus
LOSS0           constant term of linear loss function (MW)
LOSS1           linear term of linear loss function (MW)

Set after OPF solution
----------------------

MU_PMIN  (RO)   Kuhn-Tucker multiplier on lower flow lim at "from" bus (u/MW)
MU_PMAX  (RO)   Kuhn-Tucker multiplier on upper flow lim at "from" bus (u/MW)
MU_QMINF (RO)   Kuhn-Tucker multiplier on lower VAr lim at "from" bus (u/MVAr)
MU_QMAXF (RO)   Kuhn-Tucker multiplier on upper VAr lim at "from" bus (u/MVAr)
MU_QMINT (RO)   Kuhn-Tucker multiplier on lower VAr lim at  "to"  bus (u/MVAr)
MU_QMAXT (RO)   Kuhn-Tucker multiplier on upper VAr lim at  "to"  bus (u/MVAr)

"""

from typing import TypeVar
import pypower.idx_dcline as dcline
import numpy as np
from data import Data

class Dcline(Data):
    "DC line data accessor"
    datatype = "dcline"
    readonly = ["F_BUS","T_BUS","MU_SF","MU_ANGMIN","MU_ANGMAX"]

    def __init__(self,
            case:TypeVar('Case'),
            ref:int|float|np.float64,
            ):
        """DC line data access constructor

        Parameters:

        * case: Case object for DC line data
        * ref: DC line data index
        """
        super().__init__(case,ref,dcline)


    # F_BUS
    @property
    def F_BUS(self):
        return int(self.get("F_BUS"))
    
    # T_BUS
    @property
    def T_BUS(self):
        return int(self.get("T_BUS"))
    
    # BR_STATUS
    @property
    def BR_STATUS(self):
        return int(self.get("BR_STATUS"))
    @BR_STATUS.setter
    def BR_STATUS(self,value:int|float|np.float64):
        self.set("BR_STATUS",value,check=isinstance(value,int) and value in [0,1])
    
    # PF
    @property
    def PF(self):
        return self.get("PF")
    @PF.setter
    def PF(self,value:int|float|np.float64):
        self.set("PF",value,check=isinstance(value,(int,float,np.float64)))
    
    # PT
    @property
    def PT(self):
        return self.get("PT")
    @PT.setter
    def PT(self,value:int|float|np.float64):
        self.set("PT",value,check=isinstance(value,(int,float,np.float64)))
    
    # QF
    @property
    def QF(self):
        return self.get("QF")
    @QF.setter
    def QF(self,value:int|float|np.float64):
        self.set("QF",value,check=isinstance(value,(int,float,np.float64)))
    
    # VF
    @property
    def VF(self):
        return self.get("VF")
    @VF.setter
    def VF(self,value:int|float|np.float64):
        self.set("VF",value,check=isinstance(value,(int,float,np.float64)) and value > 0)
    
    # VT
    @property
    def VT(self):
        return self.get("VT")
    @VT.setter
    def VT(self,value:int|float|np.float64):
        self.set("VT",value,check=isinstance(value,(int,float,np.float64)) and value > 0)
    
    # QMINF
    @property
    def QMINF(self):
        return self.get("QMINF")
    @QMINF.setter
    def QMINF(self,value:int|float|np.float64):
        self.set("QMINF",value,check=isinstance(value,(int,float,np.float64)))
    
    # QMAXF
    @property
    def QMAXF(self):
        return self.get("QMAXF")
    @QMAXF.setter
    def QMAXF(self,value:int|float|np.float64):
        self.set("QMAXF",value,check=isinstance(value,(int,float,np.float64)))
    
    # QMINT
    @property
    def QMINT(self):
        return self.get("QMINT")
    @QMINT.setter
    def QMINT(self,value:int|float|np.float64):
        self.set("QMINT",value,check=isinstance(value,(int,float,np.float64)))
    
    # QMAXT
    @property
    def QMAXT(self):
        return self.get("QMAXT")
    @QMAXT.setter
    def QMAXT(self,value:int|float|np.float64):
        self.set("QMAXT",value,check=isinstance(value,(int,float,np.float64)) and -360 < value < +360)
    
    # LOSS0
    @property
    def LOSS0(self):
        return self.get("LOSS0")
    @LOSS0.setter
    def LOSS0(self,value:int|float|np.float64):
        self.set("LOSS0",value,check=isinstance(value,(int,float,np.float64)) and -360 < value < +360)
    
    # LOSS1
    @property
    def LOSS1(self):
        return self.get("LOSS1")
    @LOSS1.setter
    def LOSS1(self,value:int|float|np.float64):
        if not isinstance(value,(int,float,np.float64)):
            raise ValueError(f"{value=} is invalid")
        self.set("LOSS1",value)
    
    # MU_PMIN
    @property
    def MU_PMIN(self):
        return self.get("MU_PMIN")
    
    # MU_PMAX
    @property
    def MU_PMAX(self):
        return self.get("MU_PMAX")
    
    # MU_QMINF
    @property
    def MU_QMINF(self):
        return self.get("MU_QMINF")
    
    # MU_QMAXF
    @property
    def MU_QMAXF(self):
        return self.get("MU_QMAXF")
    
    # MU_QMINT
    @property
    def MU_QMINT(self):
        return self.get("MU_QMINT")
    
    # MU_QMAXT
    @property
    def MU_QMAXT(self):
        return self.get("MU_QMAXT")
    

