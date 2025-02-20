from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *
from occupancies import *

class routes_maintenance(QWidget):
    #accept parent parameter (CTC_base)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.parent_window = parent #store reference

        #initialize necessary lists/variables (can only be changed upon user interaction)
        #self. makes this accessible outside of __init__
        self.checkbox_states = [False for i in range(15)]

        #allows you to use layout to store order of widgets
        layout = QVBoxLayout()
        layout.setSpacing(5) #isn't working properly but whatever come back to this

        #CHECK BOXES
        checkboxes = [QCheckBox(f"Block {i+1}") for i in range(15)]
        #use a list to and anonymous function to send state and index of any checked box to checkbox_checked
        [cb.stateChanged.connect(lambda state, i=i+1: self.checkbox_checked(state, i)) for i, cb in enumerate(checkboxes)]
        #adds every checkbox to the layout
        [layout.addWidget(cb) for cb in checkboxes]

        #MAINTENANCE BUTTON 
        button = QPushButton('Send for maintenance')
        #send clicked signal along with current checked box
        #return i+1 for each iterable i if cb is checked
        button.clicked.connect(lambda: self.the_button_was_clicked(next((i+1 for i, cb in enumerate(checkboxes) if cb.isChecked()), -1)))
        layout.addWidget(button)

        #TRAIN LISTS
        #create table for trains
        self.table = QTableWidget()
        self.table.setRowCount(1)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Train #', 'Start Time', 'Start Station', 'End Station'])
        #self.table.setVerticalHeaderLabels(['', '', ''])

        #dummy data for presenting
        data = [
            ['0', '0:00 PM', 'X', 'Y']
        ]

        for col in range(4):
            self.table.setItem(0, col, QTableWidgetItem(data[0][col]))

        layout.addWidget(self.table)

        self.setLayout(layout)

    def the_button_was_clicked(self, index):
        pop_up = QMessageBox()
        #check to ensure block is not occupied
        if self.parent_window.occupancies_tab.check_occupancy(index):
            pop_up.setIcon(QMessageBox.Warning)
            pop_up.setWindowTitle('Failure')
            pop_up.setText(f'Block {index} currently occupied!\nCan not send maintenance now')
            pop_up.setStandardButtons(QMessageBox.Ok)
        #box pop up to confirm maintenance sent
        else:
            pop_up.setIcon(QMessageBox.Information)
            pop_up.setWindowTitle('Maintenance Sent')
            pop_up.setText(f'Maintenance Sent for Block {index}')
            pop_up.setStandardButtons(QMessageBox.Ok)
        pop_up.exec_()

    def checkbox_checked(self, state, index):
        if state == 2:
            self.checkbox_states[index] = True
        else:
            self.checkbox_states[index] = False

    def update_scheduled_trains(self, stops, time):
        print(stops, time)
        new_row_position = self.table.rowCount()
        self.table.insertRow(0)

        #data
        self.table.setItem(0, 0, QTableWidgetItem(str(new_row_position+1)))
        self.table.setItem(0, 1, QTableWidgetItem(time))
        self.table.setItem(0, 2, QTableWidgetItem('Yard / Station A'))
        self.table.setItem(0, 3, QTableWidgetItem(stops)) #should eventually include all stops, but that algorithm hasn't been written yet