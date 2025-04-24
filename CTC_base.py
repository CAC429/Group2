from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *

import sys

#initalize general ui style
dark_mode = """"
QWidget{
    background-color: #121212;
    color: #e0e0e0;
}

class CTC_base(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('CTC Interface')

        #set window size
        self.resize(1200, 800)

        #create widget for main tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        #store all tabs for easier access between them
        self.main_tab = main(self)
        self.routes_maintenance_tab = routes_maintenance(self)
        self.speed_authority_tab = speed_authority(self)

        #create all four main tabs
        self.tabs.addTab(self.main_tab, 'Home')
        self.tabs.addTab(self.routes_maintenance_tab, 'Routes and Maintenance')
        self.tabs.addTab(self.speed_authority_tab, 'Speed and Authority')

app = QApplication(sys.argv)
app.setStyleSheet(dark_mode)

window = CTC_base()
window.show()

app.exec_()