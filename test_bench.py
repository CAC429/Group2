from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class test_bench(QWidget):
    occupancy_change = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle('CTC Test Bench')
        self.resize(400, 300)

        layout = QVBoxLayout()

        #text
        layout.addWidget(QLabel('Choose occupied block:'))
        #occupied block dropdown
        self.dropdown = QComboBox()
        self.dropdown.addItems([f'Block {i+1}' for i in range(15)])
        layout.addWidget(self.dropdown)

        #send button
        self.send = QPushButton('Send Test Data')
        self.send.clicked.connect(self.send_data)
        layout.addWidget(self.send)

        self.setLayout(layout)

    def send_data(self):
        block = self.dropdown.currentText()
        self.occupancy_change.emit(block)