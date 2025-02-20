import csv
import random
from PyQt5.QtWidgets import (
    QWidget, QLabel, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QPushButton, QFileDialog, QCheckBox, QHBoxLayout, QLineEdit
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import (QTimer, Qt)

class TrackModelUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Track Model UI')
        self.setGeometry(300, 20, 1600, 1000)

        # Image display
        self.image_label = QLabel(self)
        self.image_label.setText('No image uploaded')
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setFixedSize(800, 300)

        # Upload button
        self.upload_button = QPushButton('Upload Track Layout and CSV', self)
        self.upload_button.clicked.connect(self.Upload_Image)
        self.upload_button.setFixedSize(300,50)

        # Layout label
        self.layout_label = QLabel('Track Layout:')
        self.layout_label.setFixedSize(100, 20)
        
        self.block_label = QLabel('Layout Block Occupancies:')
        self.block_label.setFixedSize(300, 20)
        
        # Table for CSV contents
        self.table = QTableWidget(self)
        self.table.setVisible(False)  # Hide until CSV is loaded

        # Timer to continuously check block occupancies
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.Update_Active_Column)  # Every second, check active status

        # First layout (Image, Upload button, Table)
        layout = QVBoxLayout()
        layout.addWidget(self.layout_label)
        layout.addWidget(self.upload_button) 
        layout.addWidget(self.image_label)
        layout.addWidget(self.block_label)

        # Add table with size policy to allow resizing
        layout.addWidget(self.table)

        self.failure_button = QPushButton('Failure', self)
        self.failure_button.clicked.connect(self.Failure)
        self.failure_button.setFixedSize(300,50)

        self.Fail_Block = 0

        cross_layout = QHBoxLayout()
        check_layout = QHBoxLayout()
        # Second layout (Toggle switch)
        layout2 = QVBoxLayout()
        
        self.switch_toggle = QCheckBox("Toggle Switch Position (High = 11, Low = 6)", self)
        
        self.switch_toggle.stateChanged.connect(self.Update_Switch_Label)
        check_layout.addWidget(self.switch_toggle,  alignment=(Qt.AlignVCenter|Qt.AlignHCenter))

        self.switch_position_label = QLabel("Rails switched to station B", self)
        self.switch_position_label.setStyleSheet("QLabel { font-size: 20px; }")
        check_layout.addWidget(self.switch_position_label, alignment=(Qt.AlignVCenter|Qt.AlignHCenter))

        layout2.addWidget(self.failure_button, alignment=(Qt.AlignBottom|Qt.AlignHCenter))
        layout2.addLayout(check_layout)
        layout2.addLayout(cross_layout)
        self.crossbars_label = QLabel("Crossbars: ", self)
        cross_layout.addWidget(self.crossbars_label,  alignment=(Qt.AlignTop|Qt.AlignHCenter))
        
        self.crossbars_text = QLineEdit(self)
        self.crossbars_text.setReadOnly(True)  # Make the text box read-only
        self.crossbars_text.setVisible(False)
        cross_layout.addWidget(self.crossbars_text,  alignment=(Qt.AlignTop|Qt.AlignHCenter))

        # Add a label to display the current switch position
        

        # Main layout (Combining the two layouts side by side)
        main_layout = QHBoxLayout()
        main_layout.addLayout(layout)  # First layout
        main_layout.addLayout(layout2)  # Second layout
        
        self.setLayout(main_layout)  # Set the layout for the window

        # Set table size policy to allow expansion
        self.table.setSizePolicy(1, 1)  # Expanding both horizontally and vertically
        self.table.horizontalHeader().setStretchLastSection(True)  # Stretch the last column
        self.table.verticalHeader().setStretchLastSection(True)

    def Upload_Image(self):
        # Open a file dialog to select an image
        image_path, _ = QFileDialog.getOpenFileName(self, 'Upload Track Layout', '', 'Image Files (*.png *.jpg *.bmp)')

        if image_path:
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(self.image_label.size())  # Scale to fit label
            self.image_label.setPixmap(pixmap)
            self.image_label.setText('')  # Clear default text

    def Load_Display_CSV(self):
        # Open a file dialog to select a CSV file
        csv_file, _ = QFileDialog.getOpenFileName(self, 'Open CSV File', '', 'CSV Files (*.csv)')
        
        if csv_file:
            data = self.Load_CSV(csv_file)
            self.Populate_Table(data)
            self.table.setVisible(True)
            self.timer.start(1000)  # Start timer to update every second
            self.crossbars_text.setVisible(True)
        

    def Load_CSV(self, file_path):
        # Load CSV file and return the data as a list of lists
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                return list(reader)
            
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
            return []
       

    def Populate_Table(self, data):
        # Use the first row as headers and the rest as data
        headers = data[0] + ["Active"]
        self.table.setColumnCount(len(headers))  # Set the number of columns
        self.table.setHorizontalHeaderLabels(headers)  # Set header labels
        
        # Populate the table with the remaining rows
        self.table.setRowCount(len(data) - 1)  # Exclude the header row
        for row_idx, row in enumerate(data[1:]):  # Start from the second row
            for col_idx, item in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(item))
            # Initialize the Active column with "False"
            self.table.setItem(row_idx, len(row), QTableWidgetItem("False"))

    def Set_Train_Position(self, position1, position2):
        # Setter method to update train positions
        self.Block_No1, self.Block_No2 = self.Get_Train_Position(position1, position2)
        self.Check_Crossbar(position1,position2)

    def Get_Train_Position(self, position1, position2):
        # Calculate block positions based on input positions
        self.Block_No1 = position1 // 50
        self.Block_No2 = position2 // 50
        return self.Block_No1, self.Block_No2

    def Update_Active_Column(self):
        # Continuously check if Block_No1 or Block_No2 equals any Block Number in column 3
        for row in range(self.table.rowCount()):
            block_number_item = self.table.item(row, 2)  # Assuming Block Number is in column 3 (index 2)
            if block_number_item:
                try:
                    block_number = int(block_number_item.text())
                    # Check if either Block_No1 or Block_No2 matches the Block Number
                    if block_number == self.Block_No1 or block_number == self.Block_No2:
                        self.table.setItem(row, self.table.columnCount()-1, QTableWidgetItem("True"))
                    else:
                        self.table.setItem(row, self.table.columnCount()-1, QTableWidgetItem("False"))
                except ValueError:
                    print(f"Warning: Non-integer value '{block_number_item.text()}' in Block Number column.")
                    self.table.setItem(row, self.table.columnCount()-1, QTableWidgetItem("Error"))

    def Check_Crossbar(self, position1, position2):
        # If position1 or position2 is 100 or 200, update the crossbars text box
        if position1 == 100 or position2 == 100:
            self.crossbars_text.setText("Down")
        elif position1 == 200 or position2 == 200:
            self.crossbars_text.setText("Down")
        else:
            self.crossbars_text.setText("Up")  # Clear text if neither condition is met

    def Toggle_Switch(self, state):
        # When the toggle switch is clicked, update the rail position (11 or 6)
        self.switch_state = state == 2  # State 2 indicates 'checked' (High)
        self.Switch_Function(self.switch_state)
        return self.switch_state

    def Switch_Function(self, state):
        # Control the switch state
        switch_position = '11 position' if state else '6 position'
        print(f"Rails switched to {switch_position}")
        # Display the switch state in the UI label

    def Update_Switch_Label(self, state):
        # Update the label text based on the checkbox state
        if state == 2:  # Checked
            self.switch_position_label.setText("Rails switched to station C")
        else:  # Unchecked
            self.switch_position_label.setText("Rails switched to station B")

    def Pass_Count(self):
        # Randomly generate a number of passengers getting on/off the train
        passengers_change = random.randint(-222, 222)  # Passengers can increase by up to 20, decrease by up to 10
        
        # Update the current passenger count
        self.current_passenger_count += passengers_change
        
        # Ensure the passenger count stays between 0 and 222
        if self.current_passenger_count > 222:
            self.current_passenger_count = 222
        elif self.current_passenger_count < 0:
            self.current_passenger_count = 0
        
        # Print the updated passenger count (for debugging or visualization)
        print(f"Current passengers: {self.current_passenger_count}")
        return self.current_passenger_count
    
    def Failure(self):
        # Select a random block
        self.Fail_Block = random.randint(1, self.table.rowCount())  # Random block index

        # Check if the Fail status is 1
        if self.Get_Fail_Status() == 1:
            # If status is 1, set the random block's "Active" column to True
            block_item = self.table.item(self.Fail_Block - 1, self.table.columnCount() - 1)  # Active column is the last one
            if block_item and block_item.text() != "True":
                # Set "Active" to "True" for this block
                self.table.setItem(self.Fail_Block - 1, self.table.columnCount() - 1, QTableWidgetItem("True"))

    def Set_Fail_status(self, status):
        # Set the failure status (1 for True, 0 for False)
        self.f_status = status

    def Get_Fail_Status(self):
        # Get the current failure status
        return self.f_status
