# main.py
import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QHBoxLayout, QFileDialog, QPushButton
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

class TrackModelUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Track Model UI')
        self.setGeometry(500, 200, 1300, 1200) 

        # Image display
        self.image_label = QLabel(self)
        self.image_label.setText('No image uploaded')
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setFixedSize(1000, 400)

        # Upload button
        self.upload_button = QPushButton('Upload Image', self)
        self.upload_button.clicked.connect(self.upload_image)

        # Layout label
        self.layout_label = QLabel('Track Layout:')
        self.layout_label.setFixedSize(100, 20)
        
        # Table for CSV contents
        self.table = QTableWidget(self)
        self.table.setVisible(False)  # Hide until CSV is loaded

        # Timer for constant loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_boolean_column)
        self.boolean_values = []

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.layout_label)
        layout.addWidget(self.upload_button) 
        layout.addWidget(self.image_label)
        layout.addWidget(QLabel('Layout Block Occupancies:'))
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def upload_image(self):
        # Open file dialog to select image
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.bmp)')
        
        if image_path:
            # Display the selected image
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(self.image_label.size())  # Scale to fit label
            self.image_label.setPixmap(pixmap)
            self.image_label.setText('')  # Clear default text
            
            # Load and display CSV after image upload
            self.load_and_display_csv('data.csv')
            self.table.setVisible(True)

            # Start the loop for the boolean column update
            self.timer.start(1000)  # Update every 1000 milliseconds (1 second)

    def load_and_display_csv(self, file_path):
        # Load CSV file and populate table
        data = self.load_csv(file_path)
        self.populate_table(data)

        # Initialize the boolean values for the new column
        self.boolean_values = [False] * len(data)

    def load_csv(self, file_path):
        # Load CSV file and return the data as a list of lists
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                data = list(reader)
                return data
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
            return []

    def populate_table(self, data):
        # Set table dimensions with an extra column for the boolean values
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]) + 1)  # Extra column for boolean

        # Set the header labels
        headers = data[0] + ["Active"]  # Add header for the new column
        self.table.setHorizontalHeaderLabels(headers)
        
        # Populate the table with CSV data
        for row_idx, row in enumerate(data):
            for col_idx, item in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(item))
            # Initialize the fourth column with "False"
            self.table.setItem(row_idx, len(row), QTableWidgetItem("False"))

    def update_boolean_column(self):
        # Toggle boolean values and update the fourth column
        for row_idx in range(len(self.boolean_values)):
            self.boolean_values[row_idx] = not self.boolean_values[row_idx]
            value = "True" if self.boolean_values[row_idx] else "False"
            self.table.setItem(row_idx, self.table.columnCount()-1, QTableWidgetItem(value))

def main():
    app = QApplication(sys.argv)
    window = TrackModelUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
