# Copyright (c) 2025 Eudoxys Sciences LLC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Case accessor class"""

import os
import sys
import datetime as dt
import importlib
import io
import numpy as np
import re
from typing import TypeVar, Any

from pypower.ppoption import (ppoption,
    PF_OPTIONS, CPF_OPTIONS, OPF_OPTIONS, 
    OUTPUT_OPTIONS, PDIPM_OPTIONS, GUROBI_OPTIONS)
import pypower.runpf as pf
import pypower.rundcopf as dcopf
import pypower.runduopf as duopf
import pypower.runopf as opf
import pypower.runuopf as uopf
import pypower.runcpf as cpf

import pypower.idx_bus as bus
import pypower.idx_brch as branch
import pypower.idx_gen as gen
import pypower.idx_dcline as dcline
import pypower.idx_cost as cost

from index import pp_index
from data import Data
from bus import Bus
from branch import Branch
from gen import Gen
from cost import Gencost, Dclinecost
from dcline import Dcline


DEBUG = True # enable raise on exceptions

def redirect_all(
        stdout:io.IOBase=sys.stdout,
        stderr:io.IOBase=sys.stderr,
        ):
    """Enables redirection of output from PP functions that import stdout and stderr from sys.
    """
    for name in ["add_userfcn","dcopf_solver","hasPQcap","main",
            "makeAvl","makeBdc","makePTDF","makeYbus",
            "opf_args","opf_execute","opf_model","opf_setup",
            "pqcost","printpf",
            "qps_cplex","qps_gurobi","qps_ipopt","qps_mosek",
            "runcpf","runopf","runpf","runuopf",
            "savecase","scale_load",
            "toggle_iflims","toggle_reserves","total_load",
            ]:
        module = importlib.import_module(name)
        setattr(module,"stdout",stdout)
        setattr(module,"stderr",stderr)
        sys.stdout = stdout
        sys.stderr = stderr

class Case:
    """Case accessor class"""
    def __init__(self,
            case:dict|str=None,
            name:str="unnamed",
            **kwargs):
        """Case constructor"""
        self.args = dict(kwargs)

        self.name = name
        self.args["name"] = name

        self.version = "2"
        self.baseMVA = 100.0

        # initial empty case data
        for key,data in pp_index.items():
            setattr(self,key,np.zeros((0,len(data))))

        # load case data
        if not case is None:
            self.args["case"] = case
            self.read(case)

        self.index = {
            "bus" : [f"{x}" for x in self.bus[:,0]],
            "branch" : [f"{x}-{y}" for x,y in zip(self.branch[:,0],self.branch[:,1])],
            "gen" : [f"{x}" for x in self.gen[:,0]],
            "gencost" : [f"{x}" for x in self.gen[:,0]],
            "dcline" : [f"{x}-{y}" for x,y in zip(self.branch[:,0],self.dcline[:,1])] if hasattr(self,"dcline") else [],
            "dclinecost" : [f"{x}-{y}" for x,y in zip(self.branch[:,0],self.dcline[:,1])] if hasattr(self,"dcline") else [],
        }

        self.PF_OPTIONS = {x[0].upper():x[1] for x in PF_OPTIONS}
        self.CPF_OPTIONS = {x[0].upper():x[1] for x in CPF_OPTIONS}
        self.OPF_OPTIONS = {x[0].upper():x[1] for x in OPF_OPTIONS}
        self.OUTPUT_OPTIONS = {x[0].upper():x[1] for x in OUTPUT_OPTIONS}
        self.PDIPM_OPTIONS = {x[0].upper():x[1] for x in PDIPM_OPTIONS}
        self.GUROBI_OPTIONS = {x[0].upper():x[1] for x in GUROBI_OPTIONS}

        self.N = self.bus.shape[0] # number of busses
        self.L = self.branch.shape[0] # number of branches
        self.G = self.gen.shape[0] # number of generators
        self.D = self.dcline.shape[0] # number of dclines

        for key,arg in kwargs.items():

            if key in ["bus","branch","gen","gencost","dcline","dclinecost"]:

                setattr(self,key,np.array(arg))
                if key == "bus":
                    self.N = self.bus.shape[0]
                elif key == "branch":
                    self.L = self.branch.shape[0]
                elif key == "gen":
                    self.G = self.gen.shape[0]
                elif key == "dcline":
                    self.D = self.dcline.shape[0]

            else:
                self.set_options(**{key:arg})

        self._matrix = {}

    @property
    def case(self) -> dict:
        """Case property getter"""
        return {x:getattr(self,x) for x in ["version","baseMVA","bus","branch","gen",
                "gencost","dcline","dclinecost"] if hasattr(self,x) and not getattr(self,x) is None}
    @case.setter
    def case(self,case):
        """Case property setter"""
        for key,value in case.items():
            if not key in self.case:
                raise KeyError(f"{key=} is not a valid items in a case")
            dtype = type(self.case[key])
            if not isinstance(value,dtype):
                raise TypeError(f"{key=} dtype={type(value)} is invalid")
            self.case[key] = value
    
    @property
    def options(self) -> dict:
        """Options property getter"""
        return self.PF_OPTIONS | self.OPF_OPTIONS | self.CPF_OPTIONS \
            | self.OUTPUT_OPTIONS | self.PDIPM_OPTIONS | self.GUROBI_OPTIONS

    @options.setter
    def options(self,
            values:dict,
            ):
        """Options property setter"""
        for key,value in values.items():
            set_option(key,value)

    def __repr__(self):
        return f"{__class__.__name__}({repr(self.name)})"

    def set_options(self,
            **kwargs):
        for key,value in kwargs.items():
            found = False
            for options in [self.PF_OPTIONS,self.CPF_OPTIONS,self.OPF_OPTIONS,
                self.OUTPUT_OPTIONS,self.PDIPM_OPTIONS,self.GUROBI_OPTIONS]:
                if not key in options:
                    continue
                if not isinstance(value,type(options[key])):
                    raise TypeError(f"{key}={repr(value)} is invalid")
                options[key] = value
                found = True
                break
            if not found:
                raise ValueError(f"{key}={repr(value)} is invalid")

    def read(self,
            case:str|dict,
            ):
        """Read case from file or case data"""
        if isinstance(case,dict):
            for key,data in case.items():
                setattr(self,key,data)
        elif isinstance(case,str):
            sys.path.insert(0,os.path.dirname(case))
            self.name = os.path.splitext(os.path.basename(case))[0]
            module = importlib.import_module(self.name)
            call = getattr(module,self.name)
            for key,data in call().items():
                if key in pp_index and data.shape[1] < len(pp_index[key]):
                    # pad missing columns with zeros
                    data = np.concatenate([data,np.zeros((data.shape[0],len(pp_index[key])-data.shape[1]))],axis=1)
                setattr(self,key,data)
            sys.path = sys.path[1:]
        else:
            raise ValueError("case must be either case data or a case filename")

    def to_dict(self) -> dict:
        """Convert case to dict"""
        return self.case

    def write(self,
            file:str=None,
            ):
        """Write case to file"""
        file = file if file else self.name
        if not file.endswith(".py"):
            file += ".py"
        name = os.path.splitext(os.path.basename(file))[0]
        with open(file,"w") as fh:
            print(f"# Generated by '{repr(self)}.write({file=})' at {dt.datetime.now()}",file=fh)
            print(f"from numpy import array, float64",file=fh)
            print(f"def {name}():",file=fh)
            print(f"   return {{",file=fh)
            for tag,data in self.case.items():
                if hasattr(data,"tolist"):
                    data = data.tolist() # change np.array to list
                if isinstance(data,list):
                    print(f"""    "{tag}": array([""",file=fh)
                    if tag in pp_index:
                        print("      #",",".join([f"{x:>10.10s}" for x in pp_index[tag]]),file=fh)
                    for row in data:
                        print(f"""      [ {','.join([f'{x:10.5g}' for x in row])}],""",file=fh)
                    print("    ],dtype=float64),",file=fh)
                else:
                    print(f"""    "{tag}": {repr(data)},""",file=fh)
            print(f"}}",file=fh)

    def run(self,
            call:callable,
            *args,
            stdout=sys.stdout,
            stderr=sys.stderr,
            **kwargs) -> bool:
        """Run PP solver"""
        if isinstance(stdout,str):
            stdout = open(stdout,"w")
        if not isinstance(stdout,io.IOBase):
            raise TypeError("stdout is not an IO stream")
        if isinstance(stderr,str):
            stderr = open(stderr,"w")
        if not isinstance(stderr,io.IOBase):
            raise TypeError("stderr is not an IO stream")
        self.set_options(**kwargs)
        try:
            redirect_all(stdout,stderr)
            result = call(self.case,*args,ppopt=self.options)
            if isinstance(result,tuple):
                result,status = result
            else:
                status = result["success"]
            error = None
        except Exception as err:
            if DEBUG:
                raise
            result,status = None,0
            error = sys.exc_info()
        self.result = {
            "data" : result,
            "status" : status,
            "error" : error,
        }
        sys.stdout.flush()
        sys.stderr.flush()
        redirect_all()
        return status == 1

    def runpf(self,
            stdout:io.IOBase|str=sys.stdout,
            stderr:io.IOBase|str=sys.stderr,
            **kwargs,
            ) -> bool:
        """Run powerflow solver"""
        return self.run(pf.runpf,stdout=stdout,stderr=stderr)

    def rundcopf(self,
            stdout:io.IOBase|str=sys.stdout,
            stderr:io.IOBase|str=sys.stderr,
            **kwargs,
            ):
        """Run DC OPF solver"""
        return self.run(dcopf.rundcopf,stdout=stdout,stderr=stderr)

    def runduopf(self,
            stdout:io.IOBase|str=sys.stdout,
            stderr:io.IOBase|str=sys.stderr,
            **kwargs,
            ):
        """Run DC unit-commitment OPF solver"""
        return self.run(duopf.runduopf,stdout=stdout,stderr=stderr)

    def runopf(self,
            stdout:io.IOBase|str=sys.stdout,
            stderr:io.IOBase|str=sys.stderr,
            **kwargs,
            ):
        return self.run(opf.runopf,stdout=stdout,stderr=stderr)

    def runuopf(self,
            stdout:io.IOBase|str=sys.stdout,
            stderr:io.IOBase|str=sys.stderr,
            **kwargs,
            ):
        """Run unit-commitment OPF"""
        return self.run(uopf.runuopf,stdout=stdout,stderr=stderr)

    def runcpf(self,
            target:dict,
            stdout:io.IOBase|str=sys.stdout,
            stderr:io.IOBase|str=sys.stderr,
            **kwargs,
            ):
        """Run continuation powerflow"""
        return self.run(cpf.runcpf,target,stdout=stdout,stderr=stderr)

    def __getitem__(self,
            ref:str|tuple|list,
            ) -> int|float|np.float64:
        """Get an object data item"""
        if isinstance(ref,str):
            return getattr(self,ref)
        elif len(ref) == 1:
            return getattr(self,ref[0])
        elif len(ref) == 2:
            return getattr(self,ref[0])[ref[1]]
        elif len(ref) == 3:
            return getattr(self,ref[0])[ref[1],ref[2]]
        else:
            raise KeyError(f"{ref=} is not valid")

    def __setitem__(self,
            ref:tuple|list,
            value:int|float|np.float64,
            ):
        """Set an object data item"""
        dtype = getattr(self,ref[0]).dtype
        getattr(self,ref[0])[ref[1],ref[2]] = np.float64(value)
        self._matrix = {} # reset matrix results

    def Bus(self,name:int|str):
        """Get a bus object"""
        return Bus(self,name)

    def Branch(self,name:int|str):
        """Get a branch object"""
        return Branch(self,name)

    def Gen(self,name:int|str):
        """Get a generator object"""
        return Gen(self,name)

    def Gencost(self,name:int|str):
        """Get a generator cost object"""
        return Gencost(self,name)

    def Dcline(self,name:int|str):
        """Get a DC line object"""
        return Dcline(self,name)

    def Dclinecost(self,name:int|str):
        """Get a DC line cost object"""
        return Dclinecost(self,name)

    def add(self,ref:str,values:list|TypeVar('np.array')=None,**kwargs):
        """Add an object to the case"""
        if ref not in pp_index:
            raise ValueError(f"{ref=} is not a valid object type")

        data = getattr(self,ref)
        row = np.zeros(shape=(1,data.shape[1]))
        n = data.shape[0]
        if not values is None:
            row[0,0:len(values)] = values
        ndx = {x:n for n,x in enumerate(pp_index[ref])}
        for key,value in kwargs.items():
            if not key in ndx:
                raise KeyError(f"{key}={value} is not a valid property of {ref} objects")
            row[0,ndx[key]] = value
        setattr(self,ref,np.vstack([data,row]))

        self.N = self.bus.shape[0] # number of busses
        self.L = self.branch.shape[0] # number of branches
        self.G = self.gen.shape[0] # number of generators
        self.D = self.dcline.shape[0] # number of dclines

        return n

    def delete(self,name:str,ref:str|int):
        """Delete an object from the case"""
        if name not in pp_index:
            raise f"{name=} is not valid"

        self.N = self.bus.shape[0] # number of busses
        self.L = self.branch.shape[0] # number of branches
        self.G = self.gen.shape[0] # number of generators
        self.D = self.dcline.shape[0] # number of dclines

        setattr(self,name,np.delete(getattr(self,name),ref,axis=0))

    def items(self,
            name:str,
            as_array:bool=False,
            ) -> tuple[int,TypeVar('np.array')|TypeVar('Data')]:
        """Iterate through items in a case"""
        if not name in pp_index:
            raise KeyError(f"'{name=}' is not valid")
        for n,x in enumerate(getattr(self,name)):
            yield n,x if as_array else getattr(self,name.title())(n)

    def matrix(self,
            name:str,
            sparse:bool=None,
            weighted:bool|str|None=None,
            dtype:Any=None,
            **kwargs) -> TypeVar('np.array'):
        """Get a graph analysis matrix"""
        cache = str(f"{name}-{sparse}-{weighted}-{dtype}")
        if cache in self._matrix: # cached result

            return self._matrix[cache]

        # A used is multiple places, almost always needed
        A_cache = "-".join(["A"]+cache.split("-")[1:])
        if A_cache in self._matrix:
            A = self._matrix[A_cache]
        else:
            A = np.zeros((self.N,self.N),dtype=complex if weighted=="complex" else float)
            for n,x in [(n,x) for n,x in self.items("branch",as_array=True) if x[branch.BR_STATUS] == 1]:
                i,j = int(x[branch.F_BUS])-1,int(x[branch.T_BUS])-1
                if weighted in [None,False]:
                    Y = 1
                elif weighted in ["abs",True]:
                    Z = complex(x[branch.BR_R],x[branch.BR_X])
                    Y = abs(1/Z) if abs(Z)>0 else 0.0
                elif weighted in ["real"]:
                    Z = x[branch.BR_R]
                    Y = 1/Z if abs(Z)>0 else 0.0
                elif weighted in ["imag"]:
                    Z = x[branch.BR_X]
                    Y = 1/Z if abs(Z)>0 else 0.0
                elif weighted == "complex":
                    Z = complex(x[branch.BR_R],x[branch.BR_X])
                    Y = 1/Z if abs(Z)>0 else 0.0
                else:
                    raise ValueError(f"{weighted=} is invalid")
                A[i,j] += Y
            self._matrix[A_cache] = A

        # D used is multiple places, almost always needed
        D_cache = "-".join(["D"]+cache.split("-")[1:])
        if D_cache in self._matrix:
            D = self._matrix[D_cache]
        else:
            D = np.zeros((self.N,self.N),dtype=complex if weighted=="complex" else float)
            for n,x in [(n,x) for n,x in self.items("branch",as_array=True) if x[branch.BR_STATUS] == 1]:
                i,j = int(x[branch.F_BUS])-1,int(x[branch.T_BUS])-1
                if weighted in [None,False]:
                    Y = 1
                elif weighted in ["abs",True]:
                    Z = complex(x[branch.BR_R],x[branch.BR_X])
                    Y = abs(1/Z) if abs(Z)>0 else 0.0
                elif weighted in ["real"]:
                    Z = x[branch.BR_R]
                    Y = 1/Z if abs(Z)>0 else 0.0
                elif weighted in ["imag"]:
                    Z = x[branch.BR_X]
                    Y = 1/Z if abs(Z)>0 else 0.0
                elif weighted == "complex":
                    Z = complex(x[branch.BR_R],x[branch.BR_X])
                    Y = 1/Z if abs(Z)>0 else 0.0
                else:
                    raise ValueError(f"{weighted=} is invalid")
                D[i,i] += Y
                D[j,j] += Y
            self._matrix[D_cache] = D

        E_cache = "-".join(["E"]+cache.split("-")[1:])
        V_cache = "-".join(["V"]+cache.split("-")[1:])

        if name == "A": # adjacency

            result = self._matrix[A_cache]

        elif name == "B": # incidence

            B = np.zeros(shape=(self.N,self.L),dtype=complex if weighted=="complex" else float)
            for n,x in [(n,x) for n,x in self.items("branch",as_array=True) if x[branch.BR_STATUS] == 1]:
                i,j = int(x[branch.F_BUS])-1,int(x[branch.T_BUS])-1
                if weighted in [None,False]:
                    B[i,n] = -1
                    B[j,n] = 1
                elif weighted == True:
                    B[i,n] += -1
                    B[j,n] += 1
                elif weighted == "real":
                    Z = x[branch.BR_R]
                    Y = 1/Z if abs(Z) > 0 else 0.0
                    B[i,n] += -Y
                    B[j,n] += Y
                elif weighted == "imag":
                    Z = x[branch.BR_X]
                    Y = 1/Z if abs(Z) > 0 else 0.0
                    B[i,n] += -Y
                    B[j,n] += Y
                elif weighted == "complex":
                    Z = complex(x[branch.BR_R],x[branch.BR_X])
                    Y = 1/Z if abs(Z) > 0 else 0.0
                    B[i,n] += -Y
                    B[j,n] += Y
                elif weighted == "abs":
                    Z = complex(x[branch.BR_R],x[branch.BR_X])
                    Y = 1/Z if abs(Z) > 0 else 0.0
                    B[i,n] += -abs(Y)
                    B[j,n] += abs(Y)
                else:
                    raise ValueError(f"{weighted=} is invalid")

            result = B

        elif name == "D": # degree

            result = self._matrix[D_cache]

        elif name == "E": # eigenvalues of L

            if E_cache in self._matrix:
                result = self._matrix[E_cache]
            e,v = np.linalg.eig(self.matrix("L",weighted=weighted))
            n = [n for x,n in sorted([(x,n) for n,x in enumerate(np.abs(e) if e.dtype == complex else e)])]
            result = e[n],v[n]
            self._matrix[E_cache],self._matrix[V_cache] = result
            result = self._matrix[E_cache]

        elif name == "G": # generation

            G = np.zeros(shape=(self.N),dtype=dtype)
            for n,x in self.items("gen",as_array=True):
                g = complex(x[gen.PG],x[gen.QG]) if x[gen.GEN_STATUS] == 1 else 0
                G[n] += g if dtype == complex else np.abs(g)
            result = G

        elif name == "Gmin": # generation min

            G = np.zeros(shape=(self.N),dtype=dtype)
            for n,x in self.items("gen",as_array=True):
                g = complex(x[gen.PMIN],x[gen.QMIN]) if x[gen.GEN_STATUS] == 1 else 0
                G[n] += g if dtype == complex else np.abs(g)
            result = G

        elif name == "Gmax": # generation max

            G = np.zeros(shape=(self.N),dtype=dtype)
            for n,x in self.items("gen",as_array=True):
                g = complex(x[gen.PMAX],x[gen.QMAX]) if x[gen.GEN_STATUS] == 1 else 0
                G[n] += g if dtype == complex else np.abs(g)
            result = G

        elif name == "L": # Laplacian

            result = self._matrix[D_cache] - self._matrix[A_cache]

        elif name == "S": # demand

            S = np.zeros(shape=(self.N),dtype=dtype)
            for n,x in self.items("bus",as_array=True):
                s = complex(x[bus.PD],x[bus.QD])
                S[n] += s if dtype == complex else np.abs(s)
            result = S

        elif name == "V": # eigenvectors of L

            if V_cache in self._matrix:
                result = self._matrix[V_cache]
            e,v = np.linalg.eig(self.matrix("L",weighted=weighted))
            n = [n for x,n in sorted([(x,n) for n,x in enumerate(np.abs(e) if e.dtype == complex else e)])]
            result = e[n],v[n]
            self._matrix[E_cache],self._matrix[V_cache] = result
            result = self._matrix[V_cache]

        elif name == "Y": # admittance

            Y = np.zeros(shape=(self.N,self.N),dtype=complex)
            for n,x in [(n,x) for n,x in self.items("branch",as_array=True) if x[branch.BR_STATUS] == 1]:
                i,j = int(x[branch.F_BUS])-1,int(x[branch.T_BUS])-1
                Z = complex(x[branch.BR_R],x[branch.BR_X])
                Y[i,j] += 1/Z if abs(Z) > 0 else 0.0
                Y[j,i] += 1/Z if abs(Z) > 0 else 0.0
                f,t = self["bus",i],self["bus",j]
                Y[i,i] += complex(f[bus.GS],f[bus.BS])
                Y[j,j] += complex(t[bus.GS],t[bus.BS])
            result = Y

        elif name == "Z": # impedance

            # TODO: need a better way to compute Z that doesn't warn 1/0
            result = np.nan_to_num(1/self.matrix("Y"),nan=0.0,posinf=0.0,neginf=0.0)

        else:

            raise KeyError(f"matrix '{name=}' is invalid")

        self._matrix[cache] = result
        return result

    def validate(self) -> bool:
        """Validate a case"""

        result = {
            # severity levels
            0 : [], # unusual condition, failure unlikely
            1 : [], # unreasonable condition, failure possible
            2 : [], # improbable condition, failure likely
            3 : [], # invalid condition, failure certain
        }

        # check bus values
        for n,x in self.items("bus"):
            if x.BUS_I <= 0 or x.BUS_I > self.N:
                result[3].append(f"bus {n} has invalid BUS_I={x.BUS_I}")
            TODO
        return result

if __name__ == "__main__":

    test = Case("case9")
    # validation = test.validate()
    # print(validation)
    # quit()

    assert test.N == 9, "incorrect number of busses"
    assert test.L == 9, "incorrect number of branches"
    assert test.G == 3, "incorrect number of generators"
    assert test.D == 0, "incorrect number of dclines"

    # test direct __getitem__ and __setitem__
    bustypes = test["bus",np.s_[0:9],bus.BUS_TYPE].tolist()
    test["bus",np.s_[0:9],bus.BUS_TYPE] = 1
    assert (test["bus",np.s_[0:9],bus.BUS_TYPE] == np.ones((9,1))).all(), "__setitem__() failed"
    test["bus",np.s_[0:9],bus.BUS_TYPE] = bustypes
    assert (test["bus",np.s_[0:9],bus.BUS_TYPE] == np.array(bustypes)).all(), "__setitem() failed"

    # test Data accessor
    for n in range(1,test.N+1):
        assert test.Bus(str(n)).BUS_I == n, "invalid bus index"
    try:
        test.Bus("1").BUS_I = 2
    except AttributeError as err:
        assert str(err) == "can't set attribute 'BUS_I'", "unexpected exception"
    assert test.Bus("1").BUS_I == 1, "bus index changed unexpectedly"

    assert test.Bus(0).BUS_TYPE == 3, "invalid bus type"
    test.Bus(0).BUS_TYPE = 2
    assert test.Bus(0).BUS_TYPE == 2, "bustype change failed"
    test.Bus(0).BUS_TYPE = 3
    assert test.Bus(0).BUS_TYPE == 3, "bustype reset failed"

    # test Bus accessor objects
    assert str(test.Bus(0)) == """{"BUS_I": 1.0, "BUS_TYPE": 3.0, "PD": 0.0, "QD": 0.0, "GS": 0.0, "BS": 0.0, "BUS_AREA": 1.0, "VM": 1.0, "VA": 0.0, "BASE_KV": 345.0, "ZONE": 1.0, "VMAX": 1.1, "VMIN": 0.9, "LAM_P": 0.0, "LAM_Q": 0.0, "MU_VMAX": 0.0, "MU_VMIN": 0.0}""", "Bus.str() failed"
    assert repr(test.Bus(0)) == "Bus(case=Case('case9'),ref=0)", "Bus.repr() failed"

    # test Branch accessor
    assert test.Branch(0).F_BUS == 1, "branch F_BUS get failed"
    assert test.Branch(0).T_BUS == 4, "branch T_BUS get failed"

    # test Gen accessor
    assert test.Gen(0).GEN_BUS == 1, "gen GEN_BUS get failed"
    assert test.Gen("2").PG == 163.0, "gen PG get failed"
    assert test.Gen(2).APF == 0.0, "gen APF get failed"

    # test Gencost access
    assert test.Gencost(0).MODEL == 2, "gencost MODEL get failed"
    assert test.Gencost(0).NCOST == 3, "gencost N get failed"
    assert (test.Gencost(0).COST == np.array([0.11,5,150])).all(), "gencost COST get failed"
    test.Gencost(0).COST[1] = 200
    assert test.Gencost(0).COST[1] == 200, "gencost COST set failed"
    test.Gencost(0).COST = [0.11,5,150]
    assert (test.Gencost(0).COST == np.array([0.11,5,150])).all(), "gencost COST reset failed"

    # test iterators
    for name in pp_index:
        for n,x in test.items(name,as_array=True):
            assert (getattr(test,name)[n] == x).all(), f"'{name}' iterator as array failed"
    assert str(list(test.items("bus"))[0]) == "(0, Bus(case=Case('case9'),ref=0))", "bus iterator failed"

    # test matrices
    assert (test.matrix("A") == test.matrix("A",weighted=False)).all(), "A matrix unweighted failed"
    A = test.matrix("A",weighted="complex")
    assert (A.sum(axis=1).round(2)==[-17.36j,0,-17.06j,1.94-10.51j,1.28-5.59j,1.16-9.78j,1.62-13.7j,1.19-21.98j,1.37-11.6j ]).all(), "A matrix get complex failed"
    assert (np.abs(A).round(2)<=test.matrix("A",weighted="abs").round(2)).all(), "A matrix get abs failed"
    assert (test.matrix("A",weighted="real").sum(axis=1).round(2) == [0,0,0,58.82,25.64,84.03,117.65,31.25,100]).all(), "A matrix get real failed"
    assert (test.matrix("A",weighted="imag").sum(axis=1).round(2) == [17.36,0,17.06,10.87,5.88,9.92,13.89,22.21,11.76]).all(), "A matrix get imag failed"

    assert (test.matrix("D") == test.matrix("D",weighted=False)).all(), "D matrix unweighted failed"
    D = test.matrix("D",weighted="complex")
    assert (D.sum(axis=1).round(2)==[-17.36j,-16.j,-17.06j,3.31-39.48j,3.22-16.1j,2.44-32.44j,2.77-23.48j,2.8-35.67j,2.55-17.58j]).all(), "D matrix get complex failed"
    assert (np.abs(D).round(2)<=test.matrix("D",weighted="abs").round(2)).all(), "D matrix get abs failed"
    assert (test.matrix("D",weighted="real").sum(axis=1).round(2) == [0,0,0,158.82,84.46,109.67,201.68,148.9,131.25]).all(), "D matrix get real failed"
    assert (test.matrix("D",weighted="imag").sum(axis=1).round(2) == [17.36,16,17.06,40,16.75,32.87,23.81,36.1,17.98]).all(), "D matrix get imag failed"

    for weight in [None,False,True,"real","complex","abs","imag"]:
        assert ( test.matrix("L",weighted=weight) == test.matrix("D",weighted=weight) - test.matrix("A",weighted=weight) ).all(), f"L matrix get {weight} failed"

    assert (test.matrix("E",weighted="real").round(1)==[  0.  +0.j ,   0.  +0.j ,   0.  +0.j ,  67.3 +0.j , 104.1+42.6j,
       104.1-42.6j, 172.8+41.7j, 172.8-41.7j, 213.6 +0.j ]).all(), "E matrix get real failed"

    assert (test.matrix("V",weighted="complex")[0].round(2) == [ 0,1,0.51+0.16j,0.57,0.79,-0.51+0.24j,-0.52-0.04j,-0.23+0.03j,0.82]).all(), "V matrix failed"

    assert (test.matrix("G") == [0,163,85,0,0,0,0,0,0]).all(), "G matrix get failed"
    assert (test.matrix("S").round(1) == [0,0,0,0,94.9,0,105.9,0,134.6]).all(), "S matrix get failed"
    assert (test.matrix("G") - test.matrix("S")).sum().round(1) == -87.4, "G - S matrix calculation failed"

    for weight in [None,False,True,"real","complex","abs","imag"]:
        assert test.matrix('B',weighted=weight).sum().round(2) == 0.0, "B matrix get/sum failed"

    assert test.matrix("Y").sum().round(2) == (17.1-215.17j), "Y matrix sum failed"
    assert test.matrix("Z").sum().round(2) == (0.24+1.72j), "Z matrix sum failed"

    b = test["bus",-1]
    test.delete("bus",8)
    test.add("bus",[9, 1, 125, 50, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9])
    assert (b == test["bus",-1]).all(), "add/delete index failed"

    b = test.Bus("9").to_dict()
    test.delete("bus",8)
    n = test.add("bus",**b)
    b = test.Bus("9").to_array()
    assert (b == test["bus",n]).all(), "add/delete ref failed"

    # test solvers
    for file in os.listdir("."):
        if re.match("case[0-9]+.py",file):
            test = Case(file,
                VERBOSE=0,
                OUT_ALL=0,
                OUT_SYS_SUM=False,
                OUT_AREA_SUM=False,
                OUT_BUS=False,
                OUT_GEN=False,
                OUT_ALL_LIM=0,
                OUT_V_LIM=0,
                OUT_LINE_LIM=0,
                OUT_PG_LIM=0,
                OUT_QG_LIM=0,
                )
            print(f"Testing {test.name}...",end="",flush=True,file=sys.stderr)
            assert test.runpf(os.devnull,os.devnull), f"{file} runpf failed"
            assert test.rundcopf(os.devnull,os.devnull), f"{file} rundcopf failed"
            assert test.runduopf(os.devnull,os.devnull), f"{file} runduopf failed"
            assert test.runopf(os.devnull,os.devnull), f"{file} runopf failed"
            assert test.runuopf(os.devnull,os.devnull), f"{file} runuopf failed"
            sys.stdout.flush()
            print("ok",file=sys.stderr,flush=True)

    print("All dev tests ok",file=sys.stderr)