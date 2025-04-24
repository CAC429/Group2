from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *

import sys

#initalize general ui style
dark_mode = """
QWidget{
    background-color: #1e1e1e;
    color: #dcdcdc;
    font-family: Segoe UI, sans-serif;
}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QListView, QSpinBox, QDoubleSpinBox{
    background-color: #2b2b2b;
    color: #f0f0f0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 4px;
}

QTabWidget::pane{
    border: 1px solid #333;
    background-color: #1e1e1e;
}

QTabBar::tab{
    background: #2a2a2a;
    color: #ffffff;
    padding: 10px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    min-width: 366px;
}

QTabBar::tab:selected{
    background: #3a3a3a;
    color: #ffffff;
    font-weight: bold;
}

QTabBar::tab:hover{
    background: #444444
}

QPushButton{
    background-color: #6a6a6a;
    color: #ffffff;
    border: 1px solid #7a7a7a;
    border-radius: 6px;
    padding: 6px 12px;
}
"""
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