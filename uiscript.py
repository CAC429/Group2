#Philip Sherman
#Trains Group 2
#Train Controller SW UI
#2/19/2025

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
import csv

#################################################################################################################################################

class PeripheralControlsPage(QWidget):
    def __init__(self, main_window, train_states2):
        super().__init__()
        self.setWindowTitle("Peripheral Controls")
        self.setGeometry(100, 100, 600, 400)

        self.main_window = main_window
        self.train_states = train_states2
        
        self.temp_timer = QTimer()
        self.temp_timer.timeout.connect(self.update_temp)

        self.target_temp = None

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        #Train Select
        self.train_select = QComboBox()
        self.train_select.addItems(self.train_states.keys())
        self.train_select.currentIndexChanged.connect(self.train_changed)
        layout.addWidget(QLabel("Select Train:"))
        layout.addWidget(self.train_select, alignment=Qt.AlignRight)

        #Light Toggle
        layout.addWidget(QLabel("Set Exterior Lights"))
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
        temp_layout = QVBoxLayout()
        temp_layout.addWidget(QLabel("Set Cabin Temperature"))

        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(40)
        self.temp_slider.setMaximum(80)
        self.temp_slider.setTickPosition(QSlider.TicksBelow)
        self.temp_slider.setTickInterval(1)
        temp_layout.addWidget(self.temp_slider)

        self.current_temp_label = QLabel("Current Temp: -- *F")
        self.target_temp_label = QLabel(f"Temperature: {self.temp_slider.value()} *F")
        temp_layout.addWidget(self.current_temp_label, alignment=Qt.AlignCenter)
        temp_layout.addWidget(self.target_temp_label, alignment=Qt.AlignCenter)

        self.temp_slider.valueChanged.connect(self.update_temp_label)

        self.set_temp_btn = QPushButton("Set Cabin Temp")
        self.set_temp_btn.clicked.connect(self.set_temp_clicked)
        temp_layout.addWidget(self.set_temp_btn, alignment=Qt.AlignCenter)

        layout.addLayout(temp_layout)
        
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
        self.target_temp_label.setText(f"Target Temp: {self.temp_slider.value()} *F")
        self.current_temp_label.setText(f"Current Temp: {state['cabin_temp']} *F")

        self.int_light_on.setEnabled(state["int_lights"] == False)
        self.int_light_off.setEnabled(state["int_lights"] == True)
    
        self.cab_light_on.setEnabled(state["cab_lights"] == False)
        self.cab_light_off.setEnabled(state["cab_lights"] == True)

        self.open_left.setEnabled(state["left_door"] == False)
        self.close_left.setEnabled(state["left_door"] == True)

        self.open_right.setEnabled(state["right_door"] == False)
        self.close_right.setEnabled(state["right_door"] == True)

        print(f"Train changed to: {train}")

    def int_light_off_clicked(self):
        train = self.get_selected_train()
        self.train_states[train]["int_lights"] = False
        print(f"Interior Lights Off for {train}")
        self.train_changed()

    def int_light_on_clicked(self):
        train = self.get_selected_train()
        self.train_states[train]["int_lights"] = True
        print(f"Interior Lights On for {train}")
        self.train_changed()

    def cab_light_off_clicked(self):
        train = self.get_selected_train()
        self.train_states[train]["cab_lights"] = False
        print(f"Cabin Lights Off for {train}")
        self.train_changed()

    def cab_light_on_clicked(self):
        train = self.get_selected_train()
        self.train_states[train]["cab_lights"] = True
        print(f"Cabin Lights On for {train}")
        self.train_changed()

    def open_left_clicked(self):
        train = self.get_selected_train()
        self.train_states[train]["left_door"] = True
        print(f"Opening Left Doors for {train}")
        self.train_changed()

    def close_left_clicked(self):
        train = self.get_selected_train()
        self.train_states[train]["left_door"] = False
        print(f"Closing Left Doors for {train}")
        self.train_changed()

    def open_right_clicked(self):
        train = self.get_selected_train()
        self.train_states[train]["right_door"] = True
        print(f"Opening Right Doors for {train}")
        self.train_changed()

    def close_right_clicked(self):
        train = self.get_selected_train()
        self.train_states[train]["right_door"] = False
        print(f"Closing Right Doors for {train}")
        self.train_changed()

    def update_temp_label(self):
        #current_temp = self.temp_slider.value()
        self.target_temp_label.setText(f"Target Temp: {self.temp_slider.value()} *F")
    
    def set_temp_clicked(self):
        train = self.get_selected_train()
        self.target_temp = self.temp_slider.value()
        print(f"Target temp set to {self.target_temp} *F")

        if self.train_states[train]["cabin_temp"] == self.target_temp:
            print("Temperature already at target")
        else:
            if not self.temp_timer.isActive():
                self.temp_timer.start(2000)

    def update_temp(self):
        train = self.get_selected_train()
        current_temp = self.train_states[train]["cabin_temp"]

        if current_temp < self.target_temp:
            self.train_states[train]["cabin_temp"] += 1
        elif current_temp > self.target_temp:
            self.train_states[train]["cabin_temp"] -= 1

        self.current_temp_label.setText(f"Current Temp: {self.train_states[train]['cabin_temp']} *F")

        if self.train_states[train]["cabin_temp"] == self.target_temp:
            self.temp_timer.stop()

    def return_home(self):
        self.close()
        self.main_window.show()

#################################################################################################

class PowerControl:
    def __init__(self, P_max = 100):
        self.Kp = 0.0
        self.Ki = 0.0
        self.P_max = P_max
        self.integral = 0
        self.P_k_1 = 0

    def update_gains(self, Kp, Ki):
        self.Kp = Kp
        self.Ki = Ki
        self.integral = 0
        self.P_k_1 = 0

    def compute_Pcmd(self, P_target, P_actual):
        error = P_target - P_actual
        #self.integral += error
        self.integral = max(min(self.integral + error, self.P_max), -self.P_max)#remove this line if issues with power
        P_cmd = self.P_k_1 + (self.Kp*error) + (self.Ki*self.integral)
        P_cmd = min(P_cmd, self.P_max)
        self.P_k_1 = P_cmd
        return P_cmd
    
##########################################################################################3

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.eb_status = 0
        self.sb_status = 0
        self.power_control = PowerControl()
        self.current_authority = 0
        self.current_speed = 0
        self.setGeometry(100, 100, 580, 450)

        self.train_states2 = {
            "Train 1": {"int_lights": False, "cab_lights": False, "left_door": False, "right_door": False, "cabin_temp": 70},
            "Train 2": {"int_lights": False, "cab_lights": False, "left_door": False, "right_door": False, "cabin_temp": 70},
            "Train 3": {"int_lights": False, "cab_lights": False, "left_door": False, "right_door": False, "cabin_temp": 70},
        }

        self.train_states = {
            "Train 1": {
                "left_door": False,
                "right_door": False,
                "outside_lights": False,
                "cabin_lights": False,
                "cabin_temp": 22,
                "service_brakes": False,
                "emergency_brakes": False,
                "problem": False,
                "Kp": 0.5,
                "Ki": 0.1,
                "P_target": 80,
                "P_actual": 50
            }
        }

        self.setWindowTitle("B Team Train Control")
        self.peripheral_window = None

        self.read_tb()

        layout = QVBoxLayout()

        title_label = QLabel("B Team Train Control")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; background-color: blue; color: white; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        content_layout = QHBoxLayout()
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignTop)

        self.peripheral_btn = QPushButton("Peripheral Controls")
        self.peripheral_btn.clicked.connect(self.open_peripheral_controls)
        self.auto_checkbox = QCheckBox("Automatic Mode")
        self.auto_checkbox.stateChanged.connect(self.auto_clicked)

        button_layout.addWidget(self.peripheral_btn)
        button_layout.addWidget(self.auto_checkbox)
        self.authority_label = QLabel(f"Authority: {self.current_authority} m")
        self.speed_label = QLabel(f"Current Speed: {self.current_speed} mph")

        button_layout.addWidget(self.authority_label)
        button_layout.addWidget(self.speed_label)

        self.service_brake_label = QLabel(f"Service Brake: {'On' if self.sb_status == 1 else 'Off'}")
        self.emergency_brake_label = QLabel(f"Emergency Brake: {'On' if self.eb_status == 1 else 'Off'}")
        self.left_door_label = QLabel(f"Left Door: {'On' if self.train_states['Train 1']['left_door'] else 'Off'}")
        self.right_door_label = QLabel(f"Right Door: {'On' if self.train_states['Train 1']['right_door'] else 'Off'}")
        self.cabin_lights_label = QLabel(f"Cabin Lights: {'On' if self.train_states['Train 1']['cabin_lights'] else 'Off'}")
        self.outside_lights_label = QLabel(f"Outside Lights: {'On' if self.train_states['Train 1']['outside_lights'] else 'Off'}")
        self.kp_label = QLabel(f"Kp: {self.train_states['Train 1']['Kp']}")
        self.ki_label = QLabel(f"Ki: {self.train_states['Train 1']['Ki']}")
        self.p_target_label = QLabel(f"P_target: {self.train_states['Train 1']['P_target']}")
        self.p_actual_label = QLabel(f"P_actual: {self.train_states['Train 1']['P_actual']}")

        button_layout.addWidget(self.service_brake_label)
        button_layout.addWidget(self.emergency_brake_label)
        button_layout.addWidget(self.left_door_label)
        button_layout.addWidget(self.right_door_label)
        button_layout.addWidget(self.cabin_lights_label)
        button_layout.addWidget(self.outside_lights_label)
        button_layout.addWidget(self.kp_label)
        button_layout.addWidget(self.ki_label)
        button_layout.addWidget(self.p_target_label)
        button_layout.addWidget(self.p_actual_label)

        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setMaximumWidth(200)
        content_layout.addWidget(button_container)

        #Constants Section

        constants_layout = QVBoxLayout()
        constants_title = QLabel("Set Constants")
        constants_title.setStyleSheet("font-size: 16px; font-weight: bold; text-decoration: underline")
        constants_title.setAlignment(Qt.AlignCenter)
        constants_layout.addWidget(constants_title)

        self.kp_label = QLabel("Kp Value:")
        self.kp_input = QLineEdit()
        self.ki_label = QLabel("Ki Value:")
        self.ki_input = QLineEdit()
        self.p_target_label = QLabel("Target Power:")
        self.p_target_input = QLineEdit()
        self.p_actual_label = QLabel("Actual Power:")
        self.p_actual_input = QLineEdit()
        self.P_cmd_label = QLabel("Commanded Power:")
        self.p_cmd_display = QLabel("0")

        self.set_constants_button = QPushButton("Apply Constants")
        self.set_constants_button.setStyleSheet("background-color: blue; color; white; font-size: 14px; font-weight: bold; padding: 10px;")
        self.set_constants_button.clicked.connect(self.calculate_power)

        constants_layout.addWidget(self.kp_label)
        constants_layout.addWidget(self.kp_input)
        constants_layout.addWidget(self.ki_label)
        constants_layout.addWidget(self.ki_input)
        constants_layout.addWidget(self.p_target_label)
        constants_layout.addWidget(self.p_target_input)
        constants_layout.addWidget(self.p_actual_label)
        constants_layout.addWidget(self.p_actual_input)
        constants_layout.addWidget(self.P_cmd_label)
        constants_layout.addWidget(self.p_cmd_display)
        constants_layout.addWidget(self.set_constants_button)

        constants_container = QWidget()
        constants_container.setLayout(constants_layout)
        constants_container.setMaximumWidth(300)
        content_layout.addWidget(constants_container)
        layout.addLayout(content_layout)

        #brake buttons
        brake_layout = QHBoxLayout()
        brake_layout.setAlignment(Qt.AlignLeft)

        self.sb_button = QPushButton("Service Brake")
        self.sb_button.setStyleSheet("background-color: orange; font-size: 14px; font-weight: bold; padding: 10px;")
        self.sb_button.setFixedWidth(220)
        self.sb_button.clicked.connect(self.sb_clicked)

        self.eb_button = QPushButton("Emergency Brake")
        self.eb_button.setStyleSheet("background-color: red; color: white; font-size: 14px; font-weight: bold; padding: 10px;")
        self.eb_button.setFixedWidth(220)
        self.eb_button.clicked.connect(self.eb_clicked)

        self.clear_brakes_button = QPushButton("Release Brakes")
        self.clear_brakes_button.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 10px;")
        self.clear_brakes_button.setFixedWidth(220)
        self.clear_brakes_button.clicked.connect(self.clear_brakes)


        brake_layout.addWidget(self.sb_button)
        brake_layout.addSpacing(10)
        brake_layout.addWidget(self.eb_button)
        brake_layout.addSpacing(10)
        brake_layout.addWidget(self.clear_brakes_button)
        layout.addLayout(brake_layout)

        self.setLayout(layout)

    def read_tb(self, file_path='TestBench_SW.csv'):
        data = {}
        try:
            with open(file_path, mode='r', newline='',encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)
                for row in csv_reader:
                    utility, state = row
                    data[utility] = state

            self.train_states["Train 1"]["left_door"] = data.get('Left_door', 'off') == 'on'
            self.train_states["Train 1"]["right_door"] = data.get('Right_door', 'off') == 'on'
            self.train_states["Train 1"]["outside_lights"] = data.get('Outside_lights', 'off') == 'on'
            self.train_states["Train 1"]["cabin_lights"] = data.get('Cabin_lights', 'off') == 'on'
            self.train_states["Train 1"]["cabin_temp"] = int(data.get('Cabin_temp', 22))
            self.train_states["Train 1"]["service_brakes"] = data.get('Service_brakes', 'off') == 'on'
            self.train_states["Train 1"]["emergency_brakes"] = data.get('Emergency_brakes', 'off') == 'on'
            self.train_states["Train 1"]["problem"] = data.get('Problem', 'off') == 'on'
            self.train_states["Train 1"]["Kp"] = float(data.get('Kp', 0.5))
            self.train_states["Train 1"]["Ki"] = float(data.get('Ki', 0.1))
            self.train_states["Train 1"]["P_target"] = int(data.get('P_target', 80))
            self.train_states["Train 1"]["P_actual"] = int(data.get('P_actual', 50))
            
            self.current_authority = int(data.get('Authority', 0))
            self.current_speed = int(data.get('Current_speed', 0))

            self.authority_label.setText(f"Authority: {self.current_authority} kW")
            self.speed_label.setText(f"Current Speed: {self.current_speed} km/h")

            self.update_train_states(data)

            print(f"Data read from test bench: {data}")
            return data
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
            return None
        except Exception as e:
            print(f"An error occured: {e}")
            return None
        
    def update_train_states(self, data):
        train = "Train 1"
        self.power_control.update_gains(float(data.get('Kp', 0)), float(data.get('Ki', 0)))

        self.train_states[train]["left_door"] = data.get('Left_door', 'off') == 'on'
        self.train_states[train]["right_door"] = data.get('Right_door', 'off') == 'on'
        self.train_states[train]["int_lights"] = data.get('Outside_lights', 'off') == 'on'
        self.train_states[train]["cab_lights"] = data.get('Cabin_lights', 'off') == 'on'
        self.train_states[train]["cabin_temp"] = int(data.get('Cabin_temp', 70))
                
        self.train_changed()

    def auto_clicked(self):
            if self.auto_checkbox.isChecked():
                print("Automatic Mode Enabled!")
            else:
                print("Automatic Mode Disabled")

    def open_peripheral_controls(self):
        if self.peripheral_window is None or not self.peripheral_window.isVisible():
            self.peripheral_window = PeripheralControlsPage(self, self.train_states2)
            self.peripheral_window.show()
            self.hide()

    def sb_clicked(self, checked=False):
        if self.eb_status == 1:
            print("Error: Emergency Brake is already active. Cannot activate service brake")
            self.train_states["service_brakes"] = False
        elif self.sb_status == 1:
            print("Error: Service Brake is already activated")
        else:
            self.sb_status = 1
            print("Service Brake Activated")
            self.train_states["service_brakes"] = True
            self.update_tb()

    def eb_clicked(self, checked=False):
        if self.sb_status == 1:
            print("Error: Service Brake is already active. Cannot activate emergency brake")
            self.train_states["emergency_brakes"] = False
        elif self.eb_status == 1:
            print("Error: Emergency Brake is already activated")
        else:
            self.eb_status = 1
            print("Emergency Brake Activated!")
            self.train_states["emergency_brakes"] = True
            self.update_tb()

    def update_tb(self):
        if self.train_states.get("service_brakes", False):
            self.service_brake_label.setText("Service Brake: On")
        else:
            self.service_brake_label.setText("Service Brake: Off")

        if self.train_states.get("emergency_brakes", False):
            self.emergency_brake_label.setText("Emergency Brake: On")
        else:
            self.emergency_brake_label.setText("Emergency Brake: Off")

    def clear_brakes(self):
        self.eb_status = 0
        self.sb_status = 0
        self.train_states["service_brakes"] = False
        self.train_states["emergency_brakes"] = False
        self.update_tb()
        print("Service and Emergency Brakes have been released")

    def calculate_power(self):
        try:
            kp = float(self.kp_input.text())
            ki = float(self.ki_input.text())
            P_target = float(self.p_target_input.text())
            P_actual = float(self.p_actual_input.text())

            self.power_control.update_gains(kp, ki)
            P_cmd = self.power_control.compute_Pcmd(P_target, P_actual)
            self.p_cmd_display.setText(str(P_cmd))
            print(f"Applied Constants: Kp={kp}, Ki={ki}, Computed Commanded Power={P_cmd} kW")
            #send to train model here
        except ValueError:
            print("Please enter valid numerical values for Kp, Ki, and Target Power")

#######################################################################

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
