from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *
from system_timer import system_timer

import global_variables
import pandas as pd
import os
import json

class main(QWidget):
    #accept parent parameter (CTC_base)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.parent_window = parent #store reference

        ###
        #SYSTEM TIMER
        ###
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_system_timer)
        self.timer.setInterval(global_variables.timer_interval)
        self.timer.start()

        #create layout pieces
        headers = QHBoxLayout()
        l_layout = QVBoxLayout()
        r_layout = QVBoxLayout()
        auto_and_man = QHBoxLayout()
        time_date = QHBoxLayout()
        full_layout = QVBoxLayout()

        ###
        #AUTOMATIC DISPATCH
        ###
        auto = QLabel('Automatic Dispatch')
        auto.setStyleSheet('font-weight: bold; background-color: green; color: white; font-size: 32px;')
        auto.setFixedSize(500, 100)
        #centers text in textbox
        auto.setAlignment(Qt.AlignCenter)

        #upload button
        upload = QPushButton('Upload File')
        upload.clicked.connect(self.upload_file)
        self.file_path = ''
        self.file_name = 'Current file: None'
        self.file_name_placeholder = QLabel(self.file_name)

        #submit automatic dispatch
        auto_button = QPushButton('Submit')
        auto_button.clicked.connect(self.dispatch_automatic)
        auto_button.setStyleSheet('background-color: green; color: white;')

        ###
        #MANUAL DISPATCH
        ###
        man = QLabel('Manual Dispatch')
        man.setStyleSheet('font-weight: bold; background-color: blue; color: white; font-size: 32px;')
        man.setFixedSize(500, 100)
        man.setAlignment(Qt.AlignCenter)

        #dropdown
        self.dropdown = QComboBox()
        self.dropdown.addItems([f'Station {chr(i)}' for i in range(65, 91)])

        #enter start time
        dispatch_time = QLabel('Select Time of Dispatch: ')
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat('HH:mm')

        #submit manual dispatch
        man_button = QPushButton('Submit')
        man_button.clicked.connect(self.dispatch_manual)
        man_button.setStyleSheet('background-color: blue; color: white;')

        ###
        #DATE, TIME, THROUGHPUT, SLIDER
        ###
        #date and time
        current_date = QLabel(f'Current date: {QDate.currentDate().toString("yyyy-MM-dd")}')
        self.time_txt = QLabel(f'Current time: {global_variables.current_time}')

        #throughput
        throughput = 0
        self.throughput_label = QLabel(f'Throughput: {throughput} tickets/hr')

        #set system speed
        #options: 1x, 5x, 10x, 20x
        sys_speed_txt = QLabel('Set speed of system (Options: 1x, 5x, 10x, 20x): ')
        self.sys_speed_slider = QSlider(Qt.Horizontal, self)
        self.sys_speed_slider.setMinimum(0)
        self.sys_speed_slider.setMaximum(3)
        self.sys_speed_slider.setValue(0)
        self.sys_speed_slider.setTickPosition(QSlider.TicksBelow)
        self.sys_speed_slider.setTickInterval(1)
        self.sys_speed_slider.valueChanged.connect(self.update_multiplier)

        #throughput
        #from greenlineoccup import GreenLineOccupancy

        ###
        #COMPILE WIDGETS
        ###
        #add headers together
        headers.addWidget(auto)
        headers.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        headers.addWidget(man)
        #compile left side (upload button, text, submit button)
        l_layout.addWidget(upload)
        l_layout.addWidget(self.file_name_placeholder)
        l_layout.addWidget(auto_button)
        #compile right side (time select, time display, submit button)
        r_layout.addWidget(dispatch_time)
        r_layout.addWidget(self.start_time)
        r_layout.addWidget(man_button)
        #compile date and time
        time_date.addWidget(current_date)
        time_date.addWidget(self.time_txt)
        #add every piece together
        full_layout.addLayout(headers)
        auto_and_man.addLayout(l_layout)
        auto_and_man.addLayout(r_layout)
        full_layout.addLayout(auto_and_man)
        full_layout.addLayout(time_date)
        #throw in throughput as well
        full_layout.addWidget(self.throughput_label)
        full_layout.addSpacerItem(QSpacerItem(0, 50, QSizePolicy.Minimum, QSizePolicy.Fixed))
        full_layout.addWidget(sys_speed_txt)
        full_layout.addWidget(self.sys_speed_slider)
        full_layout.addSpacerItem(QSpacerItem(0, 50, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.setLayout(full_layout)
    
    def upload_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, 'Open Excel File', '', 'Excel Files (*.xlsx *.xls)')
        self.file_name = 'Current file:'+str(os.path.basename(self.file_path))
        self.file_name_placeholder.setText(self.file_name)

    def station_checked(self, state, index):
        #change state of current index if box is detected to be checked
        self.check_values[index] = not self.check_values[index]

    def dispatch_automatic(self):
        if self.file_path:  #when a file is selected
            #choose based on line value (sheet value)
            df = pd.read_excel(self.file_path, sheet_name=global_variables.line)

            #enter data from sheet
            for i, content in enumerate(df.columns):
                if str(content).startswith("Train"):
                    self.parent_window.routes_maintenance_tab.update_scheduled_trains(str(df.iat[0, i]))

    def dispatch_manual(self):
        chosen_destination = chr(self.dropdown.currentIndex()+65)
        print(chosen_destination)
        chosen_time = self.start_time.time().toString('hh:mm:ss')
        print(chosen_time)

        #connect to routes tab to update trains table
        self.parent_window.routes_maintenance_tab.update_scheduled_trains(chosen_time)

    def update_multiplier(self):
        multipliers = [1, 5, 10, 20]
        index = int(self.sys_speed_slider.value())
        global_variables.system_multiplier = multipliers[index]
        global_variables.timer_interval = int(1000 / global_variables.system_multiplier)
        self.timer.setInterval(global_variables.timer_interval)
        #WRITE TO NEW JSON FILE
        try:
            with open('TIMER.json', 'w') as file:
                json.dump({"timer_interval": global_variables.timer_interval}, file)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to write PLC_INPUTS JSON: {e}")
            return
        self.parent_window.routes_maintenance_tab.timer.setInterval(global_variables.timer_interval)
        self.parent_window.speed_authority_tab.timer.setInterval(global_variables.timer_interval)

        current_time = global_variables.current_time
        self.time_txt.setText(str(current_time))

    def update_system_timer(self):
        self.time_txt.setText(f'Current time: {str(global_variables.current_time)[11:19]}')
        system_timer()

        ###
        #UPDATE THROUGHPUT EVERY SECOND
        ###
        try:
            with open('occupancy_data.json', 'r') as file:
                data = json.load(file)
                trains = data.get("trains", [])
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to read occupancy+data JSON: {e}")
            return

        all_sales = []
        tickets_hours = 0
        #grab all ticket sales
        for train in trains:
            all_sales.append(train.get("ticket_sales", []))
        #print(all_sales)

        #check time stamps that are within last hour
        for i in all_sales:
            for j in i:
                if int(str(j[1])[:2]+str(j[1])[3:]) <= int(str(global_variables.current_time)[11:13]+str(global_variables.current_time)[14:16]) and int(str(j[1])[:2]+str(j[1])[3:]) >= int(str(global_variables.current_time)[11:13]+str(global_variables.current_time)[14:16])-100:
                    tickets_hours += j[0]
        self.throughput_label.setText(f'{tickets_hours} tickets per hour')