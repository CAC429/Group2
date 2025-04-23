from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *

from send_train import send_train
import global_variables

class routes_maintenance(QWidget):
    #accept parent parameter (CTC_base)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.parent_window = parent #store reference

        #allows you to use layout to store order of widgets
        layout = QVBoxLayout()

        ###
        #SENT TRAINS TIMER
        ###
        self.train_list = []
        self.train_queue = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.train_check)
        self.timer.setInterval(global_variables.timer_interval)
        self.timer.start()

        ###
        #DROPDOWN
        ###
        self.dropdown = QComboBox()
        self.current_choice = QLabel('Selected: None')
        if global_variables.line == 0:
            self.dropdown.addItems([f'Block {i+1}' for i in range(150)])
        elif global_variables.line == 1:
            self.dropdown.addItems([f'Block {i+1}' for i in range(76)])
        #connect to function (passes a reference since there are NO parentheses;
        #otherwise immediate execution would occur)
        self.dropdown.currentIndexChanged.connect(self.update_block)

        layout.addWidget(self.dropdown)
        layout.addWidget(self.current_choice)

        ###
        #MAINTENANCE BUTTON 
        ###
        button = QPushButton('Send for maintenance')
        button.setFixedWidth(250)
        button.setStyleSheet('background-color: red; color: white;')
        #store maintenance_pressed reference in lambda, so that it is not immediately
        #called and returned faulty value, then when button is pressed lambda is called
        button.pressed.connect(lambda: self.maintenance_pressed(self.dropdown.currentIndex()))
        layout.addWidget(button)

        ###
        #DEFAULT SWITCH POSITION
        ###
        self.switch_txt = QLabel('Current default switch position: UP')
        self.switch_button = QPushButton('Change to DOWN')
        self.switch_button.clicked.connect(self.switch_default_position)
        self.switch_position = 0
        layout.addWidget(self.switch_txt)
        layout.addWidget(self.switch_button)

        ###
        #TRAIN LISTS
        ###
        #create table for trains
        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Train #', 'Start Time', 'Status'])

        layout.addWidget(self.table)

        self.setLayout(layout)

    def maintenance_pressed(self, index):
        pop_up = QMessageBox()
        #check to ensure block is not occupied
        if global_variables.block_occupancies[index]:
            pop_up.setIcon(QMessageBox.Warning)
            pop_up.setWindowTitle('Failure')
            pop_up.setText(f'Block {index+1} currently occupied!\nCan not send maintenance now')
            pop_up.setStandardButtons(QMessageBox.Ok)
            pop_up.exec_()
        #box pop up to confirm maintenance sent
        else:
            pop_up.setIcon(QMessageBox.Information)
            pop_up.setWindowTitle('Maintenance Sent')
            pop_up.setText(f'Maintenance Sent for Block {index+1}')
            pop_up.setStandardButtons(QMessageBox.Ok)
            pop_up.exec_()
            #update custom CTC occupancies to lower authority/speed surrounding maintenance
            global_variables.current_maintenance.append(index)
        #send_maintenance_update(index+1)

    def update_block(self):
        self.current_choice.setText(f'Selected: {self.dropdown.currentText()}')

    def update_scheduled_trains(self, time):
        #print(stops, time)
        new_train_number = self.table.rowCount()+1
        self.table.insertRow(0)
        self.table.setVerticalHeaderLabels(['' for i in range (new_train_number)])
        data = [str(new_train_number), str(time), 'WAITING']
        #train number, time to send, 0 to flag it has not been sent
        self.train_list.insert(0, [str(time), 0])
        for col in range(3):
            self.table.setItem(0, col, QTableWidgetItem(data[col]))
    
    def switch_default_position(self):
        if self.switch_position == 0:
            self.switch_txt.setText('Current default switch position: DOWN')
            self.switch_button.setText('Change to UP')
            self.switch_position = 1
        else:
            self.switch_txt.setText('Current default switch position: UP')
            self.switch_button.setText('Change to DOWN')
            self.switch_position = 0

    def train_check(self):
        #testing
        for i, train in enumerate(self.train_list):
            #make sure times match up and train has never been sent
            if str(train[0][:8]) == str(str(global_variables.current_time)[11:19]) and train[1] == 0:
                #send train into dispatch queue
                self.train_queue.insert(0, 0)
                train[1] = 1
        for i, train in enumerate(self.train_queue):
            if global_variables.line == 0:
                self.train_queue[i] = 1
                self.table.setItem(i, 2, QTableWidgetItem('SENT'))
                send_train(1)
                return
            elif global_variables.line == 1 and train == 0 and all(x == 0 for x in global_variables.block_occupancies[:9]) and all(x == 0 for x in global_variables.block_occupancies[15:27]):
                self.train_queue[i] = 1
                self.table.setItem(i, 2, QTableWidgetItem('SENT'))
                send_train(1)
                return
        send_train(0)