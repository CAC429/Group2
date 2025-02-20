from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *
from occupancies import *

class speed_authority(QWidget):
    #accept parent parameter (CTC_base)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.parent_window = parent #store reference

        layout = QVBoxLayout()
        
        #create table for speed/authority
        self.table = QTableWidget()
        self.table.setRowCount(3)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Train #', 'Current Suggested\nSpeed (km/hr)', 'Current Suggest\nAuthority (km)', 'Last Reached Block'])
        self.table.setVerticalHeaderLabels(['', '', ''])

        #dummy data for now
        data = [
            ['1', '64', '8', 'E'],
            ['2', '72', '7', 'D'],
            ['3', '49', '9', 'B']
        ]

        for row in range(3):
            for col in range(4):
                self.table.setItem(row, col, QTableWidgetItem(data[row][col]))

        layout.addWidget(self.table)
        self.setLayout(layout)