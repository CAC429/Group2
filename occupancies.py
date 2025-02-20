from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *
from occupancies import *

class occupancies(QWidget):
    #accept parent parameter (CTC_base)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.parent_window = parent #store reference

        layout = QVBoxLayout()
        
        #create table for speed/authority
        self.table = QTableWidget()
        self.table.setRowCount(15)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Block #', 'Occupied?'])
        self.table.setVerticalHeaderLabels(['', '', '', '', '', '', '','','','','','','','',''])

        #dummy data for now
        for row in range(15):
                self.table.setItem(row, 0, QTableWidgetItem(str(row+1)))
                self.table.setItem(row, 1, QTableWidgetItem('N'))

        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_occupancies(self, block):
        #change chosen block to occupied
        self.table.setItem(int(block[6])-1, 1, QTableWidgetItem('Y'))
        #change previous block to unoccupied
        self.table.setItem(int(block[6])-2, 1, QTableWidgetItem('N'))

    def check_occupancy(self, block):
        if self.table.item(int(block)-1, 1).text() == 'Y':
             return True
        else:
             return False