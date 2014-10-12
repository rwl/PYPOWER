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
Branches tab user interface

"""

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import numpy as np
import gui_utility
import gui_globals

class branches_ui(QtGui.QVBoxLayout): 
    
    def setup(self, window):   
        """Setup for branches tab"""
        self.main_window = window        
        
        hbox = QtGui.QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)
        
        headings = ['Bus1', 'Bus2', 'R', 'X', 'B', 'Rate A', 'Rate B', 'Rate C', 'Ratio', 'Angle', 'Status', 'Ang min', 'Ang max']
        self.tableWidget = Branches_EditTable(window, headings = headings, alternatingRowColors = True)

        self.addLayout(hbox) 
        self.addWidget(self.tableWidget)

        self.tableWidget.itemChanged.connect(self.update_data_matrix)

        self.refresh_data()    
        
    def update_data_matrix(self, tableWidgetItem): 
        """ Update matrix whenever table data is changed """
        lower_bound = 0.0
        upper_bound = float("inf")
        value = 0.0
        if tableWidgetItem.column() == 0:
            element = "Bus1"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False, convert_to_integer = True)
        elif tableWidgetItem.column() == 1:
            element = "Bus2"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False, convert_to_integer = True)
        elif tableWidgetItem.column() == 2:
            element = "R (pu)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = False)
        elif tableWidgetItem.column() == 3:
            element = "X (pu)"
            lower_bound = -1.0 * float("inf")
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 4:
            element = "B (pu)"
            lower_bound = -1.0 * float("inf")
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = False, u_inclusive = False)
        elif tableWidgetItem.column() == 5:
            element = "Rate A (MVA)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = False)
        elif tableWidgetItem.column() == 6:
            element = "Rate B (MVA)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = False)
        elif tableWidgetItem.column() == 7:
            element = "Rate C (MVA)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = False)
        elif tableWidgetItem.column() == 8:
            element = "Ratio (pu)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = False)
        elif tableWidgetItem.column() == 9:
            element = "Angle (deg)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = False)
        elif tableWidgetItem.column() == 10:
            element = "Status"
            upper_bound = 1
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = True, convert_to_integer = True)
        elif tableWidgetItem.column() == 9:
            element = "Angle Min (deg)"
            lower_bound = -360.0
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = False)
        elif tableWidgetItem.column() == 10:
            element = "Angle Max (deg)"
            upper_bound = 360.0
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive = True, u_inclusive = False)
        if value is not False:   
            gui_globals.ppc["branch"][tableWidgetItem.row(), tableWidgetItem.column()] = value
        else:
            self.main_window.show_status_message("Branch row " + str(tableWidgetItem.row() + 1) + " " + element +  ": Input value '" + tableWidgetItem.text() + "' out of bounds. (" + str(lower_bound) + " to " + str(upper_bound) + "). Value not set.", error = True, beep = True)
            self.tableWidget.itemChanged.disconnect()
            self.refresh_data()          
            self.tableWidget.itemChanged.connect(self.update_data_matrix)            
        
    def refresh_data(self):
        """Update text fields to match global variables."""
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.fill_table(gui_globals.ppc["branch"])
        self.tableWidget.setSortingEnabled(True)
 
class Branches_EditTable(gui_utility.EditTable): 
    """Modified version of Edit Table specifically for the Buses tab."""
    
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
        new_row = np.array([ 1, 2, 0, 0.0576, 0, 250, 250, 250, 0, 0, 1, -360, 360])
        gui_globals.ppc["branch"] = np.vstack([gui_globals.ppc["branch"], new_row])
        self.fill_table(gui_globals.ppc["branch"])
        self.setSortingEnabled(True)
    
    def delrow_fn(self):
        """Function for the Delete Row action."""
        gui_globals.ppc["branch"] = np.delete(gui_globals.ppc["branch"],self.currentRow(),0)
        self.fill_table(gui_globals.ppc["branch"])
        
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
                        if c == 0 or c == 1:
                            item.setText(str(int(data[r][c])))
                        else:
                            item.setText(str(float(data[r][c])))
                        
                        if readOnly:
                            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        
                        self.setItem(r, c, item)
