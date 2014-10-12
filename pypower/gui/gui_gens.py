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
Generators tab user interface

"""

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import numpy as np
import gui_utility
import gui_globals

class gens_ui(QtGui.QVBoxLayout): 
    
    def setup(self, window):   
        """Setup for generators tab"""
        self.main_window = window        
        
        hbox = QtGui.QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)
        
        headings = ['Bus ID', 'Pg', 'Qg', 'Qmax', 'Qmin', 'Vg', 'mBase', 'Status', 'Pmax', 'Pmin', 'Pc1', 'Pc2', 'Qc1min', 'Q1max', 'Qc2min', 'Qc2max', 'ramp_agc', 'ramp_10', 'ramp_30', 'ramp_q', 'apf']
        self.tableWidget = Gens_EditTable(window, headings = headings, alternatingRowColors = True)

        self.addLayout(hbox) 
        self.addWidget(self.tableWidget)

        self.tableWidget.itemChanged.connect(self.update_data_matrix)

        self.refresh_data()
        #self.tableWidget.sortItems(0)
        
    def update_data_matrix(self, tableWidgetItem): 
        """ Update matrix whenever table data is changed """
        lower_bound = 0.0
        upper_bound = float("inf")
        value = 0.0
        if tableWidgetItem.column() == 0:
            element = "Bus ID"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False, convert_to_integer = True)
        elif tableWidgetItem.column() == 1:
            element = "Pg (MW)"
            lower_bound = -1.0 * float("inf")
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 2:
            lower_bound = -1.0 * float("inf")
            element = "Qg (Mvar)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 3:
            lower_bound = -1.0 * float("inf")
            element = "Qmax (Mvar)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 4:
            lower_bound = -1.0 * float("inf")
            element = "Qmin (Mvar)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 5:
            element = "Vg (pu)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 6:
            element = "mBase (MVA)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 7:
            element = "Status"
            upper_bound = 1
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = True, convert_to_integer = True)
        elif tableWidgetItem.column() == 8:
            element = "Pmax (MW)"
            lower_bound = -1.0 * float("inf")
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 9:
            element = "Pmin (MW)"
            lower_bound = -1.0 * float("inf")
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 10:
            lower_bound = -1.0 * float("inf")
            element = "Pc1"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 11:
            lower_bound = -1.0 * float("inf")
            element = "Pc2"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 12:
            lower_bound = -1.0 * float("inf")
            element = "Qc1min"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 13:
            lower_bound = -1.0 * float("inf")
            element = "Qc1max"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 14:
            lower_bound = -1.0 * float("inf")
            element = "Qc2min"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 15:
            lower_bound = -1.0 * float("inf")
            element = "Qc2max"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 16:
            lower_bound = -1.0 * float("inf")
            element = "ramp_agc"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 17:
            lower_bound = -1.0 * float("inf")
            element = "ramp_10"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 18:
            lower_bound = -1.0 * float("inf")
            element = "ramp_30"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 19:
            lower_bound = -1.0 * float("inf")
            element = "ramp_q"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 20:
            lower_bound = -1.0 * float("inf")
            element = "apf"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        if value is not False:   
            gui_globals.ppc["gen"][tableWidgetItem.row(), tableWidgetItem.column()] = value
        else:
            self.main_window.show_status_message("Gen row " + str(tableWidgetItem.row() + 1) + " " + element +  ": Input value '" + tableWidgetItem.text() + "' out of bounds. (" + str(lower_bound) + " to " + str(upper_bound) + "). Value not set.", error = True, beep = True)
            self.tableWidget.itemChanged.disconnect()
            self.refresh_data()          
            self.tableWidget.itemChanged.connect(self.update_data_matrix)            
        
    def refresh_data(self):
        """Update text fields to match global variables."""
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.fill_table(gui_globals.ppc["gen"])
        self.tableWidget.setSortingEnabled(True)
 
class Gens_EditTable(gui_utility.EditTable): 
    """Modified version of Edit Table specifically for the Gens tab."""
    
    def setup(self, main_window, allowCopy = True, allowPaste = True, allowShortcut = True):
        """Set up table."""
        self.main_window = main_window
        
        # Add row
        addRow = QtGui.QAction('&Add Row', self)
        addRow.setStatusTip('Add Row')
        if allowShortcut:
            addRow.setShortcut('Ctrl+R')
        addRow.triggered.connect(self.addrow_fn)
        self.addAction(addRow)
		
        # Delete row
        delRow = QtGui.QAction('&Delete Row', self)
        delRow.setStatusTip('Delete Row')
        #if allowShortcut:
        #    delRow.setShortcut('Delete')
        delRow.triggered.connect(self.delrow_fn)
        self.addAction(delRow)
        
        if allowCopy:
            copyAction = QtGui.QAction('&Copy', self)
            if allowShortcut:
                copyAction.setShortcut('Ctrl+C')
            copyAction.setStatusTip('Copy')
            copyAction.triggered.connect(self.copy_fn)        
            self.addAction(copyAction)            

        if allowPaste:                
            pasteAction = QtGui.QAction('&Paste', self)
            if allowShortcut:
                pasteAction.setShortcut('Ctrl+V')
            pasteAction.setStatusTip('Paste')
            pasteAction.triggered.connect(self.paste_fn)       
            self.addAction(pasteAction)

        if allowCopy or allowPaste:                
            self.setContextMenuPolicy(Qt.ActionsContextMenu)
            self.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
	
    def addrow_fn(self):
        """Function for the Add Row action."""
        self.setSortingEnabled(False)
        vbus_no = np.array(gui_globals.ppc["gen"][:,0], dtype=int)
        
        bus_no = max(vbus_no) + 1
        self.main_window.show_status_message("Adding row: " + str(bus_no))
        
        new_row = np.array([1, 0,   0, 300, -300, 1, 100, 1, 250, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        gui_globals.ppc["gen"] = np.vstack([gui_globals.ppc["gen"], new_row])
        self.fill_table(gui_globals.ppc["gen"])
        self.setSortingEnabled(True)
    
    def delrow_fn(self):
        """Function for the Delete Row action."""
        gui_globals.ppc["gen"] = np.delete(gui_globals.ppc["gen"],self.currentRow(),0)
        self.fill_table(gui_globals.ppc["gen"])
    
    def fill_table(self, data, readOnly = False):
        """Fill table from 2D list or numpy array."""
        if len(data) > 0:
            if isinstance(data, np.ndarray):
                data = data.tolist()
            data_rows = len(data)
            data_columns = len(data[0])
            if data_columns > 0:
                self.setRowCount(data_rows)
                self.setColumnCount(data_columns)
                for r in range(0, data_rows):
                    for c in range(0, data_columns):
                        item = QtGui.QTableWidgetItem()
                        item.setTextAlignment(Qt.AlignHCenter)
                        if c == 0:
                            item.setText(str(int(data[r][c])))
                        else:
                            item.setText(str(float(data[r][c])))
                        if readOnly:
                            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                                            
                        self.setItem(r, c, item)