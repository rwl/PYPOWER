# Copyright (c) 2025 Eudoxys Sciences LLC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Branch accessor

Branch Data
-----------

F_BUS (RO)       From bus number
T_BUS            To bus number
BR_R             Resistance (p.u.)
BR_X             Reactance (p.u.)
BR_B             Total line charging susceptance (p.u.)
RATE_A           MVA rating A (long term rating)
RATE_B           MVA rating B (short term rating)
RATE_C           MVA rating C (emergency rating)
TAP              Transformer off nominal turns ratio
SHIFT            Transformer phase shift angle (degrees)
BR_STATUS        Initial branch status, 1 - in service, 0 - out of service
ANGMIN           Minimum angle difference, angle(Vf) - angle(Vt) (degrees)
ANGMAX           Maximum angle difference, angle(Vf) - angle(Vt) (degrees)

Set after powerflow or OPF solution
-----------------------------------

PF (RO)          Real power injected at "from" bus end (MW)
QF (RO)          Reactive power injected at "from" bus end (MVAr)
PT (RO)          Real power injected at "to" bus end (MW)
QT (RO)          Reactive power injected at "to" bus end (MVAr)

Set after OPF solution
----------------------

MU_SF (RO)       Kuhn-Tucker multiplier on MVA limit at "from" bus (u/MVA)
MU_ST            Kuhn-Tucker multiplier on MVA limit at "to" bus (u/MVA)

Set after SCOPF solution
------------------------

MU_ANGMIN (RO)   Kuhn-Tucker multiplier lower angle difference limit
MU_ANGMAX (RO)   Kuhn-Tucker multiplier upper angle difference limit
"""

from typing import TypeVar
import pypower.idx_brch as branch
import numpy as np
from data import Data

class Branch(Data):
    """Branch data accessor"""
    datatype = "branch"
    readonly = ["F_BUS","T_BUS","MU_SF","MU_ANGMIN","MU_ANGMAX"]

    def __init__(self,
            case:TypeVar('Case'),
            ref:int|float|np.float64,
            ):
        """Branch data access constructor

        Parameters
        ----------

        * case: Case object for bus data
        * ref: Branch data index
        """
        super().__init__(case,ref,branch)


    # F_BUS
    @property
    def F_BUS(self):
        return int(self.get("F_BUS"))
    
    # T_BUS
    @property
    def T_BUS(self):
        return int(self.get("T_BUS"))
    
    # BR_R
    @property
    def BR_R(self):
        return self.get("BR_R")
    @BR_R.setter
    def BR_R(self,value:int|float|np.float64):
        self.set("BR_R",value,check=isinstance(value,(int,float,np.float64)))
    
    # BR_X
    @property
    def BR_X(self):
        return self.get("BR_X")
    @BR_X.setter
    def BR_X(self,value:int|float|np.float64):
        self.set("BR_X",value,check=isinstance(value,(int,float,np.float64)))
    
    # BR_B
    @property
    def BR_B(self):
        return self.get("BR_B")
    @BR_B.setter
    def BR_B(self,value:int|float|np.float64):
        self.set("BR_B",value,check=isinstance(value,(int,float,np.float64)))
    
    # RATE_A
    @property
    def RATE_A(self):
        return self.get("RATE_A")
    @RATE_A.setter
    def RATE_A(self,value:int|float|np.float64):
        self.set("RATE_A",value,check=isinstance(value,(int,float,np.float64)))
    
    # RATE_B
    @property
    def RATE_B(self):
        return self.get("RATE_B")
    @RATE_B.setter
    def RATE_B(self,value:int|float|np.float64):
        self.set("RATE_B",value,check=isinstance(value,(int,float,np.float64)))
    
    # RATE_C
    @property
    def RATE_C(self):
        return self.get("RATE_C")
    @RATE_C.setter
    def RATE_C(self,value:int|float|np.float64):
        self.set("RATE_C",value,check=isinstance(value,(int,float,np.float64)))
    
    # TAP
    @property
    def TAP(self):
        return self.get("TAP")
    @TAP.setter
    def TAP(self,value:int|float|np.float64):
        self.set("TAP",value,check=isinstance(value,(int,float,np.float64)))
    
    # SHIFT
    @property
    def SHIFT(self):
        return self.get("SHIFT")
    @SHIFT.setter
    def SHIFT(self,value:int|float|np.float64):
        self.set("SHIFT",value,check=isinstance(value,(int,float,np.float64)))
    
    # BR_STATUS
    @property
    def BR_STATUS(self):
        return int(self.get("BR_STATUS"))
    @BR_STATUS.setter
    def BR_STATUS(self,value:int|float|np.float64):
        self.set("BR_STATUS",value,check=isinstance(value,int) and value in [0,1])
    
    # ANGMIN
    @property
    def ANGMIN(self):
        return self.get("ANGMIN")
    @ANGMIN.setter
    def ANGMIN(self,value:int|float|np.float64):
        self.set("ANGMIN",value,check=isinstance(value,(int,float,np.float64)) and -360 < value < +360)
    
    # ANGMAX
    @property
    def ANGMAX(self):
        return self.get("ANGMAX")
    @ANGMAX.setter
    def ANGMAX(self,value:int|float|np.float64):
        self.set("ANGMAX",value,check=isinstance(value,(int,float,np.float64)) and -360 < value < +360)
    
    # PF
    @property
    def PF(self):
        return self.get("PF")
    
    # QF
    @property
    def QF(self):
        return self.get("QF")
    
    # PT
    @property
    def PT(self):
        return self.get("PT")
    
    # QT
    @property
    def QT(self):
        return self.get("QT")
    
    # MU_SF
    @property
    def MU_SF(self):
        return self.get("MU_SF")
    
    # MU_ST
    @property
    def MU_ST(self):
        return self.get("MU_ST")
    
    # MU_ANGMIN
    @property
    def MU_ANGMIN(self):
        return self.get("MU_ANGMIN")
    
    # MU_ANGMAX
    @property
    def MU_ANGMAX(self):
        return self.get("MU_ANGMAX")


