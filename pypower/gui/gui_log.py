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
Message log tab user interface

"""

import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import numpy as np

class log_ui(QtGui.QVBoxLayout): 
    
    def setup(self, window):   
        """Setup for message log tab"""
        font = QtGui.QFont("Courier New",10)
        
        self.main_window = window        
        
        hbox = QtGui.QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)
        
        self.textBox = QtGui.QTextEdit()
        self.textBox.setReadOnly(True)
        self.textBox.setFont(font)

        self.addLayout(hbox) 
        self.addWidget(self.textBox)
        
        # Clear log
        self.textBox.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textBox.customContextMenuRequested.connect(self.textbox_menu)

    def textbox_menu(self, point):
        """ Custom context menu for text box """
        menu = self.textBox.createStandardContextMenu(point)
        
        # Include clear log action
        clearLog = QtGui.QAction('Clear message log', self)
        clearLog.setStatusTip('Clear message log')
        clearLog.triggered.connect(self.clear_fn)
        
        menu.addAction(clearLog)
        menu.exec_(self.textBox.viewport().mapToGlobal(point))
    
    def write(self, msg):
        """ Function to write messages into log """
        self.textBox.insertPlainText(str(msg))
    
    def clear_fn(self):
        """ Function to clear message log """
        self.textBox.clear()
        