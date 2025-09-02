# Copyright (c) 2025 Eudoxys Sciences LLC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Data accessor

The data accessor is the base class for all PP API object accessors.

To implement an object XYZ accessor use the following template

    from typing import TypeVar
    import pypower.idx_XYZ as XYZ
    import numpy as np
    from data import Data

    class XYZ(Data):
        "XYZ data accessor"
        datatype = "XYZ"
        readonly = ["XYZ_0"]

        def __init__(self,
                case:TypeVar('Case'),
                ref:int|float|np.float64,
                ):
            super().__init__(case,ref,XYZ)

        # XYZ_0 (read-only)
        @property
        def XYZ_0(self):
            return int(self.get("XYZ_0"))

        # XYZ_1 (read-write)
        @property
        def XYZ_1(self):
            return int(self.get("XYZ_1"))
        @XYZ_1.setter
        def XYZ_1(self,value:int|float|np.float64):
            self.set("XYZ_1",value,check=isinstance(value,(int,float,np.float64)))

        # define getter/setter for each field of XYZ listing in pypower.idx_XYZ...
"""

import json
from typing import TypeVar
import numpy as np
from index import pp_index

class Data:
    """PP object data base class"""
    def __init__(self,
            case:TypeVar('Case'),
            ref:int|float|np.float64, # index to row in data array
            pp_module:list[int], # PP module for subclass field index (e.g., idx_bus)
            ):
        self.case = case
        self.fields = pp_index[self.datatype] # list of field names
        self.pp_module = pp_module
        if isinstance(ref,(int,float,np.float64)):
            if not ( 0 <= int(ref) < case.N ):
                raise KeyError(f"{ref=} is out of range")
            self.index = ref
        elif isinstance(ref,str):
            try:
                found = [n for n,x in enumerate(case[self.datatype]) if x[0] == int(ref)]
                if not found:
                    raise KeyError(f"{self.datatype} {repr(ref)} not found")
                if len(found) > 1:
                    raise Runtime(f"{self.datatype} {repr(ref)} has more than one instance ({found=})")
                self.index = found[0]
            except ValueError:
                self.index = None
            if self.index is None:
                self.index = case.index[self.datatype][ref]

    def __str__(self) -> str:
        return json.dumps(self.to_dict())

    def __repr__(self) -> str:
        return f"{self.datatype.title()}(case={repr(self.case)},ref={repr(self.index)})"

    def get(self,
            name:str, 
            start:int|None=None, 
            stop:int|None=None, 
            ) -> np.float64|TypeVar('np.array'):
        """Get data

        Parameters
        ----------

        name: Name of field to get
        start: Array start index (default None to include first item)
        stop: Array stop index (default None to include last item)

        If both start and stop are None, only a single is returned

        Returns
        -------

        np.float64: singleton (start==None and stop==None)
        np.array: array data (start!=None or stop!=None)
        """

        # lookup attribute index from PP module
        ndx = getattr(self.pp_module,name)

        # singleton get
        if start is None and stop is None:
            return self.case[self.datatype,self.index,ndx]

        # array get
        return self.case[self.datatype,self.index,np.s_[ndx:]][start:stop]

    def set(self,
            name:str, # attribute name
            value:int|float|np.float64, # attribute value
            offset:int=0, # index offset
            check:bool=True, # check test
            override:bool=False, # override RO protection
            ):
        # TODO: allow array set
        """Set data

        Parameters
        ----------

        name: Attribute name
        value: Attribute value
        offset: Index offset (default 0)
        check: Check test (default True)
        override: Override RO protection (default False)
        """
        if not override and name in self.readonly:
            raise RuntimeError(f"{name} is read-only")
        if not check:
            raise ValueError(f"{value=} is invalid")
        self.case[self.datatype,self.index,getattr(self.pp_module,name)+offset] = float(value)

    def to_dict(self) -> dict:
        """Convert object to dict

        Returns
        -------

        dict: field names and values
        """
        return {x:self.get(x) for x in self.fields}

    def to_array(self) -> TypeVar('np.array'):
        """Convert objectd data to array

        Returns
        -------

        np.array: object values in field order
        """
        return np.array([self.get(x) for x in self.fields],dtype=np.float64)
