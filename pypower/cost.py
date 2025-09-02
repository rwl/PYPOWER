# Copyright (c) 2025 Eudoxys Sciences LLC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Cost accessor

Cost Data
---------

MODEL       Model type (see Model Types below)
STARTUP     Startup cost
SHUTDOWN    Shutdown cost
NCOST       Number of cost coefficients or data points
COST        Cost parameters

Model Types
-----------

PW_LINEAR   Piecewise linear cost function (2N parameters)
POLYNOMIAL  Polynomial cost function (N parameters)
"""

from typing import TypeVar
import pypower.idx_cost as cost
import numpy as np
from data import Data

class Cost(Data):
    """Cost data accessor"""
    readonly = []

    def __init__(self,
            case:TypeVar('Case'),
            ref:int|float|np.float64,
            ):
        """Cost data access constructor

        Parameters:

        * case: Case object for cost data
        * ref: Cost data index
        """
        super().__init__(case,ref,cost)

    # MODEL
    @property
    def MODEL(self):
        return int(self.get("MODEL"))
    @MODEL.setter
    def MODEL(self,value:int|float|np.float64):
        self.set("MODEL",value,isinstance(value,int) and value in [1,2])

    # STARTUP
    @property
    def STARTUP(self):
        return self.get("STARTUP")
    @STARTUP.setter
    def STARTUP(self,value:int|float|np.float64):
        self.set("QG",value,isinstance(value,(int,float,np.float64)))

    # SHUTDOWN
    @property
    def SHUTDOWN(self):
        return self.get("SHUTDOWN")
    @SHUTDOWN.setter
    def SHUTDOWN(self,value:int|float|np.float64):
        self.set("SHUTDOWN",value,isinstance(value,(int,float,np.float64)))

    # NCOST
    @property
    def NCOST(self):
        return int(self.get("NCOST"))
    @NCOST.setter
    def NCOST(self,value:int|float|np.float64):
        self.set("NCOST",value,isinstance(value,int) and value > 0)

    # COST
    @property
    def COST(self):
        return self.get("COST",0,None)
    @COST.setter
    def COST(self,value:list|TypeVar(np.array)):
        for n,x in enumerate(value):
            self.set("COST",x,offset=n,check=isinstance(x,(int,float,np.float64)) and x >= 0)
        self.set("NCOST",len(value),check=len(value) > 0)

class Gencost(Cost):
    """Generator cost data accessor"""
    datatype = "gencost"

class Dclinecost(Cost):
    """DC line cost data accessor"""
    datatype = "dclinecost"
