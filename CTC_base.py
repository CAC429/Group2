from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *
from occupancies import *
from test_bench import *

import sys

class CTC_base(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle('CTC Interface')

        #set window size
        self.resize(800, 600)

        #create widget for main tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        #store all tabs for easier access between them
        self.main_tab = main(self)
        self.routes_maintenance_tab = routes_maintenance(self)
        self.speed_authority_tab = speed_authority(self)
        self.occupancies_tab = occupancies(self)

        #create all four main tabs
        self.tabs.addTab(self.main_tab, 'Home')
        self.tabs.addTab(self.routes_maintenance_tab, 'Routes and Maintenance')
        self.tabs.addTab(self.speed_authority_tab, 'Speed and Authority')
        self.tabs.addTab(self.occupancies_tab, 'Block Occupancies')

        #test bench window
        self.test_bench = test_bench()
        self.test_bench.occupancy_change.connect(self.occupancies_tab.update_occupancies)

        self.test_bench.show()
        self.test_bench.activateWindow()

app = QApplication(sys.argv)

window = CTC_base()
window.show()

app.exec_()