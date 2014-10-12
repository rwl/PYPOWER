# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
# Copyright (C) 2014 Julius Susanto
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

"""
GUI for PYPOWER
Global Objects and Variables

"""

import numpy as np
import sys
import csv
import os

from pypower.ppoption import ppoption

def init():
    global ppc
    global ppopt
    
    ppc = {"version": '2'}
    
    ppc["baseMVA"] = 100.0
    
    ppc["bus"] = np.array([
        [1, 3, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [2, 2, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [3, 2, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [4, 1, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [5, 1, 90,  30, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [6, 1, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [7, 1, 100, 35, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [8, 1, 0,    0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [9, 1, 125, 50, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9]
    ])
     
    ppc["branch"] = np.array([
        [1, 4, 0,      0.0576, 0,     250, 250, 250, 0, 0, 1, -360, 360],
        [4, 5, 0.017,  0.092,  0.158, 250, 250, 250, 0, 0, 1, -360, 360],
        [5, 6, 0.039,  0.17,   0.358, 150, 150, 150, 0, 0, 1, -360, 360],
        [3, 6, 0,      0.0586, 0,     300, 300, 300, 0, 0, 1, -360, 360],
        [6, 7, 0.0119, 0.1008, 0.209, 150, 150, 150, 0, 0, 1, -360, 360],
        [7, 8, 0.0085, 0.072,  0.149, 250, 250, 250, 0, 0, 1, -360, 360],
        [8, 2, 0,      0.0625, 0,     250, 250, 250, 0, 0, 1, -360, 360],
        [8, 9, 0.032,  0.161,  0.306, 250, 250, 250, 0, 0, 1, -360, 360],
        [9, 4, 0.01,   0.085,  0.176, 250, 250, 250, 0, 0, 1, -360, 360]
    ])
    
    ppc["gen"] = np.array([
        [1, 0,   0, 300, -300, 1.0, 100, 1, 250, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 163, 0, 300, -300, 1.0, 100, 1, 300, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 85,  0, 300, -300, 1.0, 100, 1, 270, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])
    
    # OPF functions not yet implemented in GUI
    """
    ppc["areas"] = np.array([
        [1, 5]
    ])
    
    ppc["gencost"] = np.array([
        [2, 1500, 0, 3, 0.11,   5,   150],
        [2, 2000, 0, 3, 0.085,  1.2, 600],
        [2, 3000, 0, 3, 0.1225, 1,   335]
    ])
    """
    
    ppopt = ppoption()
    
    
    global filename   
    filename = ""    
    
    # Power flow settings
    global pf_settings
    pf_settings = {"Qlim": False, "max_iter": 25, "err_tol": 0.00001}
    
def write_ppc_file(fname):
    """Save PYPOWER file. 
    """
    
    filename = fname
        
    base = os.path.basename(fname)
    casename = os.path.splitext(base)[0]
    
    outfile = open(fname, 'w', newline='')
    
    outfile.write('from numpy import array\n\n')
    
    outfile.write('def ' + casename + '():\n') 
    outfile.write('\tppc = {"version": ''2''}\n')
    outfile.write('\tppc["baseMVA"] = 100.0\n')
   
    outfile.write('\tppc["bus"] = ')
    outfile.write(np.array_repr(ppc["bus"]))
    outfile.write('\n\n')
     
    outfile.write('\tppc["gen"] = ')
    outfile.write(np.array_repr(ppc["gen"]))
    outfile.write('\n\n')
    
    outfile.write('\tppc["branch"] = ')
    outfile.write(np.array_repr(ppc["branch"]))
    outfile.write('\n\n')
    
    outfile.write('\treturn ppc')
    outfile.close()
    
    return True
