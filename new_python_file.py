# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout

class TrackModelUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Track Model UI')
        self.setGeometry(500, 500, 800, 700) 

        # Input field
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText('Enter a value')

        # Display label
        self.display_label = QLabel('Entered value will be displayed here', self)

        # Submit button
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.display_value)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.display_label)
        
        self.setLayout(layout)

    def display_value(self):
        # Get the value from input field and set it to the display label
        value = self.input_field.text()
        self.display_label.setText(f'Entered Value: {value}')


def main():
    app = QApplication(sys.argv)
    window = TrackModelUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
