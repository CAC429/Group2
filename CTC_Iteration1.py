from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.resize(800, 600)

        #window title
        self.setWindowTitle('CTC')

        #create central widgets and set widget order
        central_widget = QWidget(self)
        layout = QVBoxLayout()
        layout.setSpacing(5) #isn't working properly but whatever come back to this

        #window label
        label = QLabel('Main Page')
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        #buttons
        button = QPushButton('Send for maintenance')
        button.clicked.connect(self.the_button_was_clicked)
        layout.addWidget(button)

        #check boxes
        checkboxes = [QCheckBox(f"Block {i+1}") for i in range(5)]
        print(checkboxes)
        #add checkboxes to the layout
        [cb.stateChanged.connect(self.checkbox_checked) for cb in checkboxes]
        [layout.addWidget(cb) for cb in checkboxes]

        #checkbox.stateChanged.connect(self.checkbox_checked)
        #layout.addWidget(checkbox)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def the_button_was_clicked(self):
        print('Clicked')

    def checkbox_checked(self, state):
        print('State changed', state)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()