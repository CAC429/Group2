# main.py
import sys
import csv
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QPushButton, QFileDialog
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
        self.upload_button.clicked.connect(self.Upload_Image)

        # Layout label
        self.layout_label = QLabel('Track Layout:')
        self.layout_label.setFixedSize(100, 20)
        
        # Table for CSV contents
        self.table = QTableWidget(self)
        self.table.setVisible(False)  # Hide until CSV is loaded

        # Timer for constant loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.Update_Voltage_Column)
        self.boolean_values = []
        self.voltages = []

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.layout_label)
        layout.addWidget(self.upload_button) 
        layout.addWidget(self.image_label)
        layout.addWidget(QLabel('Layout Block Occupancies:'))
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def Upload_Image(self, image_path=None):
        if not image_path:
            # If no image path is given, prompt the user
            file_dialog = QFileDialog()
            image_path, _ = file_dialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.bmp)')
        
        if image_path:
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(self.image_label.size())  # Scale to fit label
            self.image_label.setPixmap(pixmap)
            self.image_label.setText('')  # Clear default text
            
            # Load and display CSV after image upload
            self.load_and_display_csv('data.csv')
            self.table.setVisible(True)

            # Start the loop for the boolean column update
            self.timer.start(1000)  # Update every 1000 milliseconds (1 second)

    def Load_Display_CSV(self, file_path):
        # Load CSV file and populate table
        data = self.Load_CSV(file_path)
        self.Populate_Table(data)

        # Initialize the boolean values for the new column
        self.boolean_values = [False] * len(data)

    def Load_CSV(self, file_path):
        # Load CSV file and return the data as a list of lists
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                data = list(reader)
                return data
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
            return []

    def Populate_Table(self, data):
        # Set table dimensions with extra columns for booleans and voltages
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]) + 2)  # Extra columns for Active and Voltage

        # Set the header labels
        headers = data[0] + ["Active", "Voltage"]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Populate the table with CSV data
        for row_idx, row in enumerate(data):
            for col_idx, item in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(item))
            # Initialize the Active column with "False"
            self.table.setItem(row_idx, len(row), QTableWidgetItem("False"))
            # Initialize the Voltage column with "0V"
            self.table.setItem(row_idx, len(row)+1, QTableWidgetItem("0V"))

    def getTrack_Voltages(self):
        # Randomly choose between 0V and 10V for each of the 15 blocks
        return [random.choice([0, 10]) for _ in range(15)]

    def Update_Voltage_Column(self):
        # Get the latest voltage readings
        self.voltages = self.get_track_voltages()

        # Update the "Voltage" column and the "Active" column based on voltage
        for row_idx, voltage in enumerate(self.voltages):
            # Update the Voltage column
            self.table.setItem(row_idx, self.table.columnCount()-1, QTableWidgetItem(f"{voltage}V"))
            
            # Update the Active (boolean) column
            # True if 0V (Occupied), False if 10V (Unoccupied)
            self.boolean_values[row_idx] = (voltage == 0)
            boolean_text = "True" if self.boolean_values[row_idx] else "False"
            self.table.setItem(row_idx, self.table.columnCount()-2, QTableWidgetItem(boolean_text))

    def Switch_Function(self, state):
        # Control the timer based on the boolean state
        if state:
            print("Rails switched to 11 position")
        else:
            print("Rails switched to 6 position")

def main():
    app = QApplication(sys.argv)
    window = TrackModelUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
