#Philip Sherman
#Trains Group 2
#Train Controller SW UI
#2/19/2025

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

#################################################################################################################################################

class PeripheralControlsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Peripheral Controls")
        self.setGeometry(100, 100, 600, 400)

        self.main_window = main_window

        #Train states
        self.train_states = {
            "Train 1": {"int_lights": 0, "cab_lights": 0, "left_door": 0, "right_door": 0, "cabin_temp": 22},
            "Train 2": {"int_lights": 0, "cab_lights": 0, "left_door": 0, "right_door": 0, "cabin_temp": 22},
            "Train 3": {"int_lights": 0, "cab_lights": 0, "left_door": 0, "right_door": 0, "cabin_temp": 22},
        }
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        #Train Select
        self.train_select = QComboBox()
        self.train_select.addItems(["Train 1", "Train 2", "Train 3"])
        self.train_select.currentIndexChanged.connect(self.train_changed)
        layout.addWidget(self.train_select, alignment=Qt.AlignRight)

        #Light Toggle
        layout.addWidget(QLabel("Set Interior Lights"))
        interior_light_layout = QHBoxLayout()
        self.int_light_off = QPushButton("Off")
        self.int_light_on = QPushButton("On")
        interior_light_layout.addWidget(self.int_light_off)
        interior_light_layout.addWidget(self.int_light_on)
        layout.addLayout(interior_light_layout)
        self.int_light_off.clicked.connect(self.int_light_off_clicked)
        self.int_light_on.clicked.connect(self.int_light_on_clicked)

        #Cabin Light Toggle
        layout.addWidget(QLabel("Set Cabin Lights"))
        cabin_light_layout = QHBoxLayout()
        self.cab_light_off = QPushButton("Off")
        self.cab_light_on = QPushButton("On")
        cabin_light_layout.addWidget(self.cab_light_off)
        cabin_light_layout.addWidget(self.cab_light_on)
        layout.addLayout(cabin_light_layout)
        self.cab_light_off.clicked.connect(self.cab_light_off_clicked)
        self.cab_light_on.clicked.connect(self.cab_light_on_clicked)

        #Door Toggle
        layout.addWidget(QLabel("Door Status"))
        door_layout = QVBoxLayout()
        left_door_layout = QHBoxLayout()
        self.open_left = QPushButton("OPEN LEFT")
        self.close_left = QPushButton("CLOSE LEFT")
        left_door_layout.addWidget(self.open_left)
        left_door_layout.addWidget(self.close_left)
        self.open_left.clicked.connect(self.open_left_clicked)
        self.close_left.clicked.connect(self.close_left_clicked)

        right_door_layout = QHBoxLayout()
        self.open_right = QPushButton("OPEN RIGHT")
        self.close_right = QPushButton("CLOSE RIGHT")
        right_door_layout.addWidget(self.open_right)
        right_door_layout.addWidget(self.close_right)
        self.open_right.clicked.connect(self.open_right_clicked)
        self.close_right.clicked.connect(self.close_right_clicked)

        door_layout.addLayout(left_door_layout)
        door_layout.addLayout(right_door_layout)
        layout.addLayout(door_layout)
        
        #Set Cabin Temp
        layout.addWidget(QLabel("Set Cabin Temperature"))

        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(10)
        self.temp_slider.setMaximum(30)
        #self.temp_slider.setValue(22)
        self.temp_slider.setTickPosition(QSlider.TicksBelow)
        self.temp_slider.setTickInterval(1)
        layout.addWidget(self.temp_slider)

        self.temp_label = QLabel(f"Temperature: {self.temp_slider.value()} *C")
        layout.addWidget(self.temp_label)

        self.temp_slider.valueChanged.connect(self.update_temp_label)

        self.set_temp_btn = QPushButton("Set Cabin Temp")
        self.set_temp_btn.clicked.connect(self.set_temp_clicked)
        layout.addWidget(self.set_temp_btn, alignment=Qt.AlignCenter)
        

        #Home Button
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(self.return_home)
        layout.addWidget(self.home_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)

        self.train_changed()

    def get_selected_train(self):
        return self.train_select.currentText()

    def train_changed(self):
        train = self.get_selected_train()
        state = self.train_states[train]

        self.temp_slider.setValue(state["cabin_temp"])
        self.temp_label.setText(f"Temperature: {state['cabin_temp']} *C")

        print(f"Train changed to: {train}")

    def int_light_off_clicked(self, checked=False):
        train = self.get_selected_train()
        self.train_states[train]["int_lights"] = 0
        print(f"Interior Lights Off for {train}")

    def int_light_on_clicked(self, checked=False):
        print("Interior Lights On")

    def cab_light_off_clicked(self, checked=False):
        print("Cabin Lights Off")

    def cab_light_on_clicked(self, checked=False):
        print("Cabin Lights On")

    def open_left_clicked(self, checked=False):
        print("Opening Left Doors")

    def close_left_clicked(self, checked=False):
        print("Closing Left Doors")

    def open_right_clicked(self, checked=False):
        print("Opening Right Doors")

    def close_right_clicked(self, checked=False):
        print("Closing Right Doors")

    def update_temp_label(self):
        current_temp = self.temp_slider.value()
        self.temp_label.setText(f"Temperature: {current_temp} *C")
    
    def set_temp_clicked(self):
        current_temp = self.temp_slider.value()
        print(f"Setting Cabin Temp to {current_temp} *C")

    def return_home(self):
        self.close()
        self.main_window.show()

#################################################################################################################################################

class StatsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Stats Page")
        self.setGeometry(100, 100, 600, 400)

        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        #Home Button
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(self.return_home)
        layout.addWidget(self.home_btn, alignment=Qt.AlignRight)

        self.train_select = QComboBox()
        self.train_select.addItems(["Train 1", "Train 2", "Train 3"])
        self.train_select.currentIndexChanged.connect(self.update_stats)
        layout.addWidget(QLabel("Select Train:"))
        layout.addWidget(self.train_select)

        self.dim_label = QLabel()
        self.mass_label = QLabel()
        self.power_label = QLabel()
        self.passenger_label = QLabel()
        self.crew_label = QLabel()
        self.weight_label = QLabel()

        layout.addWidget(self.dim_label)
        layout.addWidget(self.mass_label)
        layout.addWidget(self.power_label)
        layout.addWidget(self.passenger_label)
        layout.addWidget(self.crew_label)
        layout.addWidget(self.weight_label)

        self.setLayout(layout)

        self.train_data = {
            "Train 1": {"dimensions": "20m x 3m x 4m", "mass": "5000 kg", "power": "1500 kW", "passengers": 100, "crew": 5},
            "Train 2": {"dimensions": "25m x 3.5m x 4.2m", "mass": "6000 kg", "power": "1800 kW", "passengers": 120, "crew": 6},
            "Train 3": {"dimensions": "30m x 3.8m x 4.5m", "mass": "7500 kg", "power": "2000 kW", "passengers": 150, "crew": 8},
        }

        self.update_stats()

    def update_stats(self):
        select_train = self.train_select.currentText()
        train_info = self.train_data[select_train]

        total_weight = self.calc_tot_weight(train_info["passengers"], train_info["crew"])

        self.dim_label.setText(f"Total Dimensions: {train_info['dimensions']}")
        self.mass_label.setText(f"Total Mass: {train_info['mass']}")
        self.power_label.setText(f"Power: {train_info['power']}")
        self.passenger_label.setText(f"Passenger Count: {train_info['passengers']}")
        self.crew_label.setText(f"Crew Count: {train_info['crew']}")
        self.weight_label.setText(f"Total Weight of Train: {total_weight} kg")

    def calc_tot_weight(self, passengers, crew):
        avg_weight = 75 #75kg per person
        return (passengers + crew) * avg_weight

    def return_home(self):
        self.close()
        self.main_window.show()

##################################################################################################################################################

class SetConstantsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Set Constants Page")
        self.setGeometry(100, 100, 600, 400)

        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        #Home Button
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(self.return_home)
        layout.addWidget(self.home_btn, alignment=Qt.AlignRight)

        self.ki_label = QLabel("Enter Ki:")
        self.ki_input = QLineEdit()
        layout.addWidget(self.ki_label)
        layout.addWidget(self.ki_input)

        self.kp_label = QLabel("Enter Kp:")
        self.kp_input = QLineEdit()
        layout.addWidget(self.kp_label)
        layout.addWidget(self.kp_input)

        self.speed_label = QLabel("Enter Current Speed:")
        self.speed_input = QLineEdit()
        layout.addWidget(self.speed_label)
        layout.addWidget(self.speed_input)

        #Submit
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.calculate_and_send)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def calculate_and_send(self):
        try:
            ki = float(self.ki_input.text())
            kp = float(self.kp_input.text())
            s = float(self.speed_input.text())
            power = self.calculate_power(ki, kp, s)
            self.send_power(power)
        except ValueError:
            print("Please enter valid numerical values for Ki and Kp")

    def calculate_power(self, ki, kp, s):
        power = (ki/s) + kp
        return power

    def send_power(self, power):
        print(f"Power value {power} sent to the Train Model")

    
    def return_home(self):
        self.close()
        self.main_window.show()

##################################################################################################################################################

class MainWindow(QWidget):
    def __init__(self):

        eb_status = 0
        sb_status = 0

        super().__init__()
        self.setGeometry(100, 100, 580, 450)
        self.setWindowTitle("B Team Train Control")

        self.peripheral_window = None
        self.stats_window = None
        self.constants_window = None

        layout = QVBoxLayout()

        title_label = QLabel("B Team Train Control")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; background-color: blue; color: white; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        content_layout = QHBoxLayout()
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignTop)
        button_style = "font-size: 14px; padding: 10px; min-width: 150px; min-height: 40px;"

        self.peripheral_btn = QPushButton("Peripheral Controls")
        self.peripheral_btn.setStyleSheet(button_style)
        self.peripheral_btn.clicked.connect(self.open_peripheral_controls)

        self.stats_btn = QPushButton("Stats")
        self.stats_btn.setStyleSheet(button_style)
        self.stats_btn.clicked.connect(self.open_stats_page)

        self.constants_btn = QPushButton("Set Constants")
        self.constants_btn.setStyleSheet(button_style)
        self.constants_btn.clicked.connect(self.open_set_constants_page)

        self.auto_checkbox = QCheckBox("Automatic Mode")
        self.auto_checkbox.setFont(QFont("Arial", 12))

        def auto_clicked():
            if self.auto_checkbox.isChecked():
                print("Automatic Mode Enabled!")
            else:
                print("Automatic Mode Disabled")

        self.auto_checkbox.clicked.connect(auto_clicked)

        button_layout.addWidget(self.peripheral_btn)
        button_layout.addWidget(self.stats_btn)
        button_layout.addWidget(self.constants_btn)
        button_layout.addWidget(self.auto_checkbox)

        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        button_container.setMaximumWidth(200)

        content_layout.addWidget(button_container)

        #train picture layout
        train_image = QLabel()
        pixmap = QPixmap("PGHtrainpic.jpg")
        pixmap = pixmap.scaled(420, 380, Qt.KeepAspectRatio)
        train_image.setPixmap(pixmap)
        train_image.setAlignment(Qt.AlignRight)
        content_layout.addWidget(train_image)

        layout.addLayout(content_layout)

        #brake buttons
        brake_layout = QHBoxLayout()
        brake_layout.setAlignment(Qt.AlignLeft)
        sb_button = QPushButton("Service Brake")
        sb_button.setStyleSheet("background-color: orange; font-size: 14px; font-weight: bold; padding: 10px;")
        sb_button.setFixedWidth(220)
        eb_button = QPushButton("Emergency Brake")
        eb_button.setStyleSheet("background-color: red; color: white; font-size: 14px; font-weight: bold; padding: 10px;")
        eb_button.setFixedWidth(220)
        sb_button.clicked.connect(self.sb_clicked)
        eb_button.clicked.connect(self.eb_clicked)

        brake_layout.addWidget(sb_button)
        brake_layout.addSpacing(10)
        brake_layout.addWidget(eb_button)
        layout.addLayout(brake_layout)

        self.setLayout(layout)

    def open_peripheral_controls(self):
        if self.peripheral_window is None or not self.peripheral_window.isVisible():
            self.peripheral_window = PeripheralControlsPage(self)
            self.peripheral_window.show()
            self.hide()

    def open_stats_page(self):
        if self.stats_window is None or not self.stats_window.isVisible():
            self.stats_window = StatsPage(self)
            self.stats_window.show()
            self.hide()

    def open_set_constants_page(self):
        if self.constants_window is None or not self.constants_window.isVisible():
            self.constants_window = SetConstantsPage(self)
            self.constants_window.show()
            self.hide()

    def sb_clicked(self, checked=False):
        sb_status = 1
        print("Service Brake Activated")

    def eb_clicked(self, checked=False):
        eb_status = 1
        print("Emergency Brake Activated!")

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
