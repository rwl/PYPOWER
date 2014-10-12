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
Main Function

"""

import os, sys, webbrowser
import numpy as np
from PyQt4 import QtCore, QtGui

from pypower.ppver import ppver
from pypower.runpf import runpf
from pypower.loadcase import loadcase
from pypower.printpf import printpf
from pypower.idx_bus import BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, \
    VM, VA, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN, REF

import gui_buses
import gui_gens
import gui_branches
import gui_log
import gui_pf_settings
import gui_utility
import gui_globals

import time

class Window(QtGui.QMainWindow):
    
    def __init__(self):
        super(Window, self).__init__()
        
        gui_globals.init()
        self.initUI()
        
    def initUI(self):
                
        self.resize(1700, 800)
        self.centre()
        self.setWindowTitle('PYPOWER | Editor')
        self.setWindowIcon(QtGui.QIcon('icons\sigma.png'))    
        
        """
        Tabs
        """
        tab_widget = QtGui.QTabWidget()
        tab1 = QtGui.QWidget()
        tab2 = QtGui.QWidget() 
        tab3 = QtGui.QWidget()
        tab4 = QtGui.QWidget()        
        self.tab_widget = tab_widget
               
        tab_widget.addTab(tab1, "Buses")
        tab_widget.addTab(tab2, "Generators")
        tab_widget.addTab(tab3, "Branches")
        tab_widget.addTab(tab4, "Message Log")        
        
        self.page1 = gui_buses.buses_ui(tab1)
        self.page2 = gui_gens.gens_ui(tab2)
        self.page3 = gui_branches.branches_ui(tab3)
        self.log = gui_log.log_ui(tab4)
        
        self.page1.setup(self)
        self.page2.setup(self)
        self.page3.setup(self)
        self.log.setup(self)
  
        self.setCentralWidget(tab_widget)
        
        """
        Actions
        """
        exitAction = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        
        refreshAction = QtGui.QAction(QtGui.QIcon('icons/refresh.ico'), '&Refresh', self)        
        refreshAction.setShortcut('F5')
        refreshAction.setStatusTip('Refresh')
        refreshAction.triggered.connect(self.page1.refresh_data)
        refreshAction.triggered.connect(self.page2.refresh_data)
        
        ldfAction = QtGui.QAction(QtGui.QIcon('icons/powerflow.png'), '&Power Flow', self)        
        #ldfAction.setShortcut('F5')
        ldfAction.setStatusTip('Calculate power flow')
        ldfAction.triggered.connect(self.calc_power_flow)
        
        resetAction = QtGui.QAction(QtGui.QIcon('icons/reset.png'), '&Reset Voltages', self)
        resetAction.setStatusTip('Reset bus voltages and angles')
        resetAction.triggered.connect(self.reset_voltages)        
        
        newAction = QtGui.QAction(QtGui.QIcon('icons/new.png'), '&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New grid')
        newAction.triggered.connect(self.new_fn) 
        
        ###########################
        # TO DO - Add Save button which will be greyed out if no changes from saved data
        #         Save button should bring up Save As if no open file
        ###########################
        
        saveAction = QtGui.QAction(QtGui.QIcon('icons/saveas.ico'), '&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save grid file')
        saveAction.triggered.connect(self.save_fn)
        
        saveAsAction = QtGui.QAction(QtGui.QIcon('icons/saveas.ico'), 'Save &As', self)
        saveAsAction.setShortcut('Ctrl+A')
        saveAsAction.setStatusTip('Save grid file as')
        saveAsAction.triggered.connect(self.save_as_fn)

        openAction = QtGui.QAction(QtGui.QIcon('icons/open.ico'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open grid file')
        openAction.triggered.connect(self.open_fn)
        
        aboutAction = QtGui.QAction('&About', self)
        aboutAction.setStatusTip('About')
        aboutAction.triggered.connect(self.about_dialog)
        
        helpAction = QtGui.QAction('&Documentation', self)
        helpAction.setShortcut('F1')
        helpAction.setStatusTip('User documentation')
        helpAction.triggered.connect(self.user_docs)   
        
        """
        Menubar
        """
        menu_bar = self.menuBar()
        fileMenu = menu_bar.addMenu('&File')
        fileMenu.addAction(newAction)        
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)
        helpMenu = menu_bar.addMenu('&Help')
        helpMenu.addAction(helpAction)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutAction)
               
        """
        Toolbar
        """
		
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar = self.addToolBar('Refresh')
        self.toolbar.addAction(refreshAction)
        self.toolbar = self.addToolBar('Power Flow')
        self.toolbar.addAction(ldfAction)
        self.toolbar = self.addToolBar('Reset Voltages')
        self.toolbar.addAction(resetAction)
          
        """
        Status bar and log messages
        """            
        self.statusBar()
        v = ppver('all')        
        self.log.write("PYPOWER v" + v["Version"] + ", " + v["Date"] + "\n")
        self.log.write("===========================\n")
        sys.stdout = self.log
        
    def centre(self):        
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def show_status_message(self, message, error = False, beep = False):
        """Display a status message on the status line.
           If error is True the status text will be coloured red.
           If beep is True then the application will beep.
        """
        if(error):
            self.statusBar().setStyleSheet('QStatusBar {color: red}')
        else:
            self.statusBar().setStyleSheet('')
        if beep:
            QtGui.QApplication.beep()
        self.statusBar().showMessage(message)
    
    def calc_power_flow(self):
        """ Calculate power flow """
        
        dialog = gui_pf_settings.Settings_ui(self)
        result = dialog.getSettings()
        
        if result: 
            # Run power flow
            self.refresh_data()
            results, success = runpf(gui_globals.ppc, gui_globals.ppopt)
            bus = results["bus"]       
            printpf(results, sys.stdout)
            
            if success:
                self.show_status_message("Power flow successfully converged...")
            else:
                self.show_status_message("Power flow did not converge...")
            
            gui_globals.ppc["bus"][:, VM] = np.round(bus[:, VM], 4)
            gui_globals.ppc["bus"][:, VA] = np.round(bus[:, VA], 4)
            self.refresh_data()
    
    def reset_voltages(self):
        """Function to reset all voltages to 1pu <0 deg (flat start)"""
        for i in range(0,len(gui_globals.ppc["bus"])):
            gui_globals.ppc["bus"][i,7] = 1.0
            gui_globals.ppc["bus"][i,8] = 0.0
        self.refresh_data()
        self.log.write("Bus voltages reset to 1.0pu and 0.0 radians...\n")
    
    def new_fn(self):
        """Function to create a new grid."""
        gui_globals.ppc["bus"] = np.array([[ 1, 3, 0.0, 0.0, 0.0, 0.0, 1, 1.0, 0.0, 132.0, 1, 1.1, 0.9],
                        [ 2, 2, 0.0, 0.0, 0.0, 0.0, 1, 1.0, 0.0, 132.0, 1, 1.1, 0.9]])
    
        gui_globals.ppc["branch"] = np.array([[1,   2,  0,      0.0576, 0,     250, 250, 250, 0, 0, 1, -360, 360]])
        gui_globals.ppc["gen"] = np.array([[1.0, 0,   0, 300, -300, 1, 100, 1, 250, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        gui_globals.ppc["areas"] = np.array([[1, 1]])
        gui_globals.ppc["gencost"] = np.array([[1, 1500, 0, 3, 0.11,   1,   150]])
        self.refresh_data()

    def save_as_fn(self):
        """Function for the Save As action."""
        fname = QtGui.QFileDialog.getSaveFileName(self, "Save Case File As", "", "Case files (*.py *.mat)")
        if fname:
            if gui_globals.write_ppc_file(fname):
                self.show_status_message("Save to Case File " + fname + " successful.")  
                self.log.write("Save to Case File " + fname + " successful.\n")
            else:
                self.show_status_message("Failed to save " + fname + ".", error = True, beep = True)
                self.log.write("Failed to save " + fname + ".\n")
        else:
            self.show_status_message("Save As cancelled.")                   
            ###########################
            # TO DO - Distinguish between cancel and failure
            #       - Put open filename in title bar
            ###########################
            
    def save_fn(self):    
        """Function for the Save action."""
        if gui_globals.filename != "":
            if gui_globals.write_ppc_file(gui_globals.filename):              
                self.show_status_message("Case File saved to " + gui_globals.filename + '.')    
                self.log.write("Case File saved to " + gui_globals.filename + '\n')
                return
            else:
                self.show_status_message("Failed to save to " + gui_globals.filename + ".", error = True, beep = True)
                self.log.write("Failed to save to " + gui_globals.filename + '\n')
        else:
            self.save_as_fn()
            
    def open_fn(self):
        """Function for the Open action."""
        ###########################
        # TO DO - Confirmation for opening file if data is unsaved
        #       - Put open filename in title bar
        ###########################
        fname = QtGui.QFileDialog.getOpenFileName(self, "Open Case File", "", "Case files (*.py *.mat)")
        if fname:
            try:
                gui_globals.ppc = loadcase(fname)
                self.refresh_data()
                gui_globals.filename = fname
                self.show_status_message("Case File " + fname + " successfully loaded.")
                self.log.write("Case File " + fname + " successfully loaded.\n")
            except:
                
                self.show_status_message("Failed to open " + fname + ".", error = True, beep = True)
                self.log.write("Failed to open " + fname + ".\n")

        else:
            self.show_status_message("Open Data File cancelled.")
    
    def user_docs(self):
        """Launch PYPOWER project page on GitHub"""
        webbrowser.open('https://github.com/rwl/PYPOWER')
    
    def about_dialog(self):
        """Show about dialog box"""
        v = ppver('all')
        QtGui.QMessageBox.about(self, "About PYPOWER",
                "<b>PYPOWER</b> is a power flow and optimal power flow solver. <p>Version " + v["Version"] + ", " + v["Date"])
	
    def refresh_data(self):
        """Refresh data in tabs"""
        self.page1.refresh_data()
        self.page2.refresh_data()
        self.page3.refresh_data()
        
def main():
    app = QtGui.QApplication(sys.argv)    
    w = Window()
    w.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()