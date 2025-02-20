from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

class TestWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #set window size
        self.resize(800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.create_page('Home'), 'Home')

    def create_page(self, text):
        page = QWidget()
        layout = QVBoxLayout()
        label = QLabel(f'Welcome to the {text} page!', alignment=Qt.AlignCenter)
        layout.addWidget(label)
        page.setLayout(layout)
        return page

app = QApplication(sys.argv)

window = TestWindow()
window.show()

app.exec_()