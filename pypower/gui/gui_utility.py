# Copyright (C) 1996-2011 Power System Engineering Research Center (PSERC)
# Copyright (C) 2011 Richard Lincoln
# Copyright (C) 2014 Julius Susanto, Tom Walker
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
Custom utility functions for PyQt tables

"""

from PyQt4 import QtCore, QtGui
import numpy as np
import csv
import gui_globals

def validate(input_value, lower_bound, upper_bound, l_inclusive = True, u_inclusive = True, convert_to_integer = False):
    """Check if value is within allowable range.
    
    :param input_value: Input value to validate
    :type input_value: String
    :param lower_bound: Lowest acceptable value.
    :type lower_bound: Float
    :param upper_bound: Highest acceptable value.
    :type upper_bound: Float
    :param l_inclusive: True if range includes lower bound.
    :type l_inclusive: Boolean
    :param u_inclusive: True if range includes upper bound.
    :type u_inclusive: Boolean
    :returns: Float of value if acceptable, False otherwise.
    :param conver_to_integer: Convert input_value to integer prior to check for validity.
    :type convert_to_integer: Boolean
    """    
    try:
        value = float(input_value)
        if convert_to_integer:
            value = int(value)
    except:
        value = False
    if ((u_inclusive and value <= upper_bound) or (not u_inclusive and value < upper_bound)) and ((l_inclusive and value >= lower_bound) or (not l_inclusive and value > lower_bound)):
        return value
    return False

def validate_from_list(input_value, valid_list, convert_to_numbers = False, convert_to_integer = False):
    """Check if a value is within list of valid numbers.

    :param input_value: Input value to validate
    :type input_value: String
    :param valid_list: List of acceptable values.
    :type valid_list: List
    :param convert_to_numbers: Convert input_value to number prior to checking for presence in list.
    :type convert_to_numbers: Boolean
    :param conver_to_integer: Convert input_value to integer prior to checking for presence in list.
    :type convert_to_integer: Boolean
    """
    try:
        if convert_to_numbers:
            value = float(input_value)        
            if convert_to_integer:
                value = int(value)
    except:
        value = False
    return value in valid_list

def create_validation_hook(gui, text_field, description, lower_bound = 0.0, upper_bound = 1.0, l_inclusive = True, u_inclusive = True, update_data = True, refresh_data = True, convert_to_integer = False, select_list = None, select_numeric = False, ):
    """Wrapper to create a function which will validate value input into a QLineEdit. For floating point numbers.

    :param gui: Reference to main window
    :type gui: Window
    :param text_field: Text field to validate input of
    :type text_field: QLineEdit
    :param description: Description of text field for display in status line.
    :type description: String
    :param select_list: Optional. Limits acceptable values to a list.
    :type select_list: List
    :param select_numeric: Optional. True if select list values should be converted to numbers before comparison to list.
    :type select_numeric: Boolean
    :param lower_bound: Optional. Lowest acceptable value.
    :type lower_bound: Float
    :param upper_bound: Optional. Highest acceptable value.
    :type upper_bound: Float
    :param l_inclusive: Optional. True if range includes lower bound.
    :type l_inclusive: Boolean
    :param u_inclusive: Optional. True if range includes upper bound.
    :type u_inclusive: Boolean
    :param convert_to_integer: Optional. True if value should be converted to integer.
    :type convert_to_integer: Boolean
    :param update_data: Optional. True if update_data function should be called on gui object.
    :type update_data: Boolean
    :param refresh_data: Optional. True if refresh_data function should be called on gui object.
    :type refresh_data: Boolean
    :returns: Reference to function which will perform validation calls.
    """        
    if select_list is None:
        test = lambda text: validate(text, lower_bound, upper_bound, l_inclusive, u_inclusive, convert_to_integer = convert_to_integer)
    else:
        test = lambda text: validate_from_list(text, select_list, select_numeric, convert_to_integer)
    def validation_hook():
        if test(text_field.text()) is False:
            gui.main_window.show_status_message(description + ": Input value '" + text_field.text() + "' out of bounds (" + str(lower_bound) + " to " + str(upper_bound) + "). Value not set.", error = True, beep = True)
            if refresh_data:
                gui.refresh_data()
        else:
            if update_data:
                gui.update_data()
            gui.main_window.show_status_message("", error = False, beep = False)
            if refresh_data:
                gui.refresh_data()            
    return validation_hook


def write_table_to_csv_file(file_name, edit_table):
    """Write the data from a table to a .csv file."""
    try:
        with open(file_name, mode='w') as fp:
            csv_writer = csv.writer(fp, dialect=csv.excel, lineterminator='\n')
            csv_writer.writerows(edit_table.get_headings_and_data_as_list())
        return True
    except:
        return False

def write_tables_to_csv_file(folder_name, variables, edit_tables):
    """Write the data from multiple table to a .csv file. Each widget is given a separate tab."""
    try:
        if len(variables) == len(edit_tables):
            for i in range(len(variables)):
                if not write_table_to_csv_file(folder_name + '\\' + variables[i] + ".csv", edit_tables[i]):                    
                    return False
        return True
    except:
        return False

class EditTable(QtGui.QTableWidget): 
    """Overloaded version of the QTableWidget which adds Copy/Paste functionality to the table."""

    def __init__(self, main_window, data = [], headings = [], allowCopy = True, allowPaste = True, readOnly = False, alternatingRowColors = False, allowShortcut = True):
        """Constructor which will set up Copy & Paste actions and populate table headings and data."""
        super(QtGui.QTableWidget, self).__init__()                
        self.setup(main_window, allowCopy, allowPaste, allowShortcut)
        if len(data) > 0:
            self.fill_table(data, readOnly)
        if len(headings) > 0:
            self.setColumnCount(len(headings))            
            self.setHorizontalHeaderLabels(headings)
        self.setAlternatingRowColors(alternatingRowColors)
        self.setSortingEnabled(True)
    
    def setup(self, main_window, allowCopy = True, allowPaste = True, allowShortcut = True):
        """Set up table."""
        self.main_window = main_window
		
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
            self.setSelectionMode(QAbstractItemView.ContiguousSelection)

    def copy_fn(self):
        """Function for the Copy action."""
        # get active element
        # find selected text in element
        # load into clipboard
        if len(self.selectedRanges()) > 1:
            self.main_window.show_status_message("Copy command cannot be used with multiple ranges selected.", error = True, beep = True)
            return
        rows = self.selectedRanges()[0].rowCount()
        columns = self.selectedRanges()[0].columnCount()
        # For some reason the selectedIndexes output is transposed, so we have to transpose it
        # Python 3.3 receives a str from .data(), 2.7 receives QVariant        
        data = np.array([ (str(index.data().toString()) if type(index.data()) == QtCore.QVariant else index.data()) for index in self.selectedIndexes() ])
        data.resize((columns, rows))
        data = np.transpose(data).flatten()        
        delimiters = ([ "\t" for c in range(columns - 1) ] + ["\n"]) * rows        
        # explicit string conversion required for Python 2.7
        copy = [char for pair in zip(data, delimiters) for char in pair]
        copy = ''.join(copy)
        QtGui.QApplication.clipboard().setText(copy)

    def paste_fn(self):
        """Function for the Paste action."""
        # There might be a more elegant way of doing this..
        try:
            # convert data to String if required
            data = str(QtGui.QApplication.clipboard().text())
            data = [ [ (np.complex(val) if val.find("j") > 0 else float(val)) for val in line.split('\t') if len(val) > 0 ] for line in data.split('\n') if len(line) > 0 ]        
            if len(self.selectedIndexes()) > 0 and len(data) > 0:
                data_rows = len(data)
                data_columns = len(data[0])
                table_rows = self.rowCount()
                table_columns = self.columnCount()
                active_row = self.selectedIndexes()[0].row()
                active_column = self.selectedIndexes()[0].column()
                selection = QtGui.QItemSelection(self.model().index(active_row, active_column), self.model().index(active_row + data_rows - 1, active_column + data_columns - 1))
                self.selectionModel().select(selection, QtGui.QItemSelectionModel.ClearAndSelect)
                if active_row + data_rows > table_rows or active_column + data_columns > (table_columns - 1):
                    self.main_window.show_status_message("Clipboard data too large.", error = True, beep = True)
                else:                    
                    for r in range(data_rows):
                        for c in range(data_columns):
                            self.item(r + active_row, c + active_column).setText(str(data[r][c]))                                
        except:
            self.main_window.show_status_message("Clipboard data invalid.", error = True, beep = True)    
        
    def fill_table(self, data, readOnly = False, convertComplexNumbers = False):
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
                        item = QTableWidgetItem()
                        item.setTextAlignment(Qt.AlignHCenter)
                        # Convert complex numbers from 0j to 0 and (1+1j) to 1+1j
                        if convertComplexNumbers and isinstance(data[r][c], np.complex):
                            re = data[r][c].real
                            im = data[r][c].imag
                            result = []
                            if re != 0:
                                result = result + [str(re)]
                            if im != 0:
                                result = result + [str(abs(im)) + "j"]
                            if len(result) == 0:
                                result = ["0"]
                            if im > 0:
                                result = "+".join(result)
                            else:
                                result = "-".join(result)
                            item.setText(result)
                        else:                             
                            item.setText(str(data[r][c]))
                        if readOnly:
                            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        self.setItem(r, c, item)                       
    
    def get_headings_and_data_as_list(self):
        """Return a 2D list including headings and data."""
        data = self.get_data_as_list()
        if self.horizontalHeaderItem(0) is None:
            return data
        headings = self.get_headings_as_list()        
        return [headings] + data
        
    def get_headings_as_list(self):
        """Return list of headings."""
        headings = [ self.horizontalHeaderItem(c).text() for c in range(self.columnCount()) ]
        return headings
    
    def get_data_as_list(self):
        """Return the data from the table as a 2D list."""
        data = [ [ self.item(r, c).text() for c in range(self.columnCount()) ] for r in range(self.rowCount()) ]
        return data