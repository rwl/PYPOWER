"""Fix ppc case bus to start from 0 rather than 1 to avoid mismatch
""" 
from pypower.idx_bus import BUS_I
from pypower.idx_brch import F_BUS, T_BUS
from pypower.idx_gen import GEN_BUS

def to_ppc0(ppc):
    """Make bus number start from 0 if bus number is not start from 0."""
    bus=ppc['bus']
    if bus[0][0]==0:
        return ppc
    
    numberOfBus=len(bus)
    bus[:,BUS_I]=range(numberOfBus)
    
    branch=ppc['branch']
    branch[:,F_BUS]=branch[:,F_BUS]-1
    branch[:,T_BUS]=branch[:,T_BUS]-1
    
    gen=ppc['gen']
    gen[:,GEN_BUS]=gen[:,GEN_BUS]-1
    
    ppc['bus']=bus
    ppc['branch']=branch
    ppc['gen']=gen
    return ppc