from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *
from occupancies import *

import pandas as pd

class main(QWidget):
    #accept parent parameter (CTC_base)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.parent_window = parent #store reference

        main_layout = QHBoxLayout()

        #automatic dispatch side
        l_layout = QVBoxLayout()
        auto = QLabel('Automatic Dispatch')
        auto.setAlignment(Qt.AlignCenter)

        #upload button
        upload = QPushButton('Upload File')
        upload.clicked.connect(self.upload_file)

        l_layout.addWidget(auto)
        l_layout.addWidget(upload)

        #manual dispatch side
        r_layout = QVBoxLayout()
        man = QLabel('Manual Dispatch')
        man.setAlignment(Qt.AlignCenter)

        r_layout.addWidget(man)

        #checkboxes
        self.check_values = [False for i in range(7)]
        stations = [QCheckBox(f'Station {chr(i)}') for i in range (66, 68)]
        [station.stateChanged.connect(lambda state, i=i: self.station_checked(state, i)) for i, station, in enumerate(stations)]
        r_layout.addWidget(QLabel('Select Destination (Must begin in yard / station A):'))
        [r_layout.addWidget(i) for i in stations]

        #enter start time
        time_text = QLabel('Select Time of Dispatch: ')
        self.start_time = QTimeEdit()
        r_layout.addWidget(time_text)
        r_layout.addWidget(self.start_time)

        #submit manual dispatch
        man_button = QPushButton('Submit')
        man_button.clicked.connect(self.dispatch_manual)
        r_layout.addWidget(man_button)

        #bring layouts together
        main_layout.addLayout(l_layout)
        main_layout.addLayout(r_layout)
        self.setLayout(main_layout)

        print(self.parent())
    
    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Excel File', '', 'Excel Files (*.xlsx *.xls)')

        if file_path:  #when a file is selected
            df = pd.read_excel(file_path)

            #set row and column count
            self.parent_window.routes_maintenance_tab.table.setRowCount(df.shape[0])
            self.parent_window.routes_maintenance_tab.table.setColumnCount(df.shape[1])
            self.parent_window.routes_maintenance_tab.table.setHorizontalHeaderLabels(df.columns)

            #enter data from sheet
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    self.parent_window.routes_maintenance_tab.table.setItem(row, col, QTableWidgetItem(str(df.iat[row, col])))

    def station_checked(self, state, index):
        print(index+65)
        self.check_values[index] = not self.check_values[index]
        print(self.check_values[index])

    def dispatch_automatic():
        pass

    def dispatch_manual(self):
        chosen_destination = 0
        for i in range(len(self.check_values)):
            if self.check_values[i] == True:
                chosen_destination = chr(i+66)
        print(chosen_destination)
        chosen_time = self.start_time.time().toString('hh:mm:ss AP')
        print(chosen_time)

        #connect to routes tab to update trains table
        self.parent_window.routes_maintenance_tab.update_scheduled_trains(chosen_destination, chosen_time)