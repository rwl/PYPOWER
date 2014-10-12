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
Dialog box for power flow settings

"""

from PyQt4 import QtCore, QtGui
import gui_globals

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
        
class PF_settings_dialog_ui(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(400, 300)
        Dialog.setWindowTitle(_fromUtf8("Power Flow Settings"))
        Dialog.setToolTip(_fromUtf8(""))
        Dialog.setStatusTip(_fromUtf8(""))
        Dialog.setWhatsThis(_fromUtf8(""))
        Dialog.setAccessibleName(_fromUtf8(""))
        Dialog.setAccessibleDescription(_fromUtf8(""))
        Dialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setToolTip(_fromUtf8(""))
        self.buttonBox.setStatusTip(_fromUtf8(""))
        self.buttonBox.setWhatsThis(_fromUtf8(""))
        self.buttonBox.setAccessibleName(_fromUtf8(""))
        self.buttonBox.setAccessibleDescription(_fromUtf8(""))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.checkBox = QtGui.QCheckBox(Dialog)
        self.checkBox.setGeometry(QtCore.QRect(50, 170, 271, 25))
        self.checkBox.setAcceptDrops(False)
        self.checkBox.setText(_fromUtf8("Consider reactive power limits"))
        self.checkBox.setToolTip(_fromUtf8("Consider reactive power limits"))
        self.checkBox.setStatusTip(_fromUtf8("Consider reactive power limits"))
        self.checkBox.setWhatsThis(_fromUtf8("Consider reactive power limits"))
        self.checkBox.setAccessibleName(_fromUtf8("Consider reactive power limits"))
        self.checkBox.setAccessibleDescription(_fromUtf8("Consider reactive power limits"))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.checkBox.setTristate(False)
        if gui_globals.ppopt["ENFORCE_Q_LIMS"] == True:
            self.checkBox.setChecked(True)        
        
        self.errTol = QtGui.QLineEdit(Dialog)
        self.errTol.setGeometry(QtCore.QRect(180, 50, 113, 27))
        self.errTol.setObjectName(_fromUtf8("errTol"))
        self.errTol.setText(str(gui_globals.ppopt["PF_TOL"]))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(40, 50, 131, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.label.setText(_fromUtf8("Error Tolerance:"))
        
        self.maxIter = QtGui.QLineEdit(Dialog)
        self.maxIter.setGeometry(QtCore.QRect(180, 110, 113, 27))
        self.maxIter.setObjectName(_fromUtf8("maxIter"))
        self.maxIter.setText(str(gui_globals.ppopt["PF_MAX_IT"]))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(40, 110, 131, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))        
        self.label_2.setText(_fromUtf8("Max. Iterations:"))
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

class Settings_ui(QtGui.QDialog, PF_settings_dialog_ui):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)
        
    def getSettings(self,parent=None):
        result = self.exec_()
        checkstate_ = self.checkBox.isChecked()
        gui_globals.ppopt["ENFORCE_Q_LIMS"] = checkstate_
        
        max_iter = int(self.maxIter.text())
        gui_globals.ppopt["PF_MAX_IT"] = max_iter
        
        err_tol = float(self.errTol.text())
        gui_globals.ppopt["PF_TOL"] = err_tol

        return (result == self.Accepted )
