#Philip Sherman
#Trains Group 2
#Train Controller SW UI
#2/19/2025

import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QFileSystemWatcher

class Constants:
    MPH_TO_MPS = 0.44704
    MPS_TO_MPH = 2.23694
    KMH_TO_MPS = 0.277778
    MPS_TO_KMH = 3.6
    KMH_TO_MPH = 0.621371

##########################################################################

class TrainState:
    def __init__(self):
        self.left_door = True
        self.right_door = True
        self.outside_lights = True
        self.cabin_lights = True
        self.cabin_temp = 70
        self.service_brakes = False
        self.emergency_brakes = False

##########################################################################################

class PowerController:
    def __init__(self):
        self.P_cmd = 0.0
        self.P_max = 120000
        self.uk = 0.0
        self.uk1 = 0.0
        self.ek = 0.0
        self.ek1 = 0.0
        self.T = 0.2
        self.manual_kp = 0.0
        self.manual_ki = 0.0
        self.P_k_1 = 0.0
        self.auto_kp = 10000
        self.auto_ki = 500

    def calculate_power(self, current_speed, target_speed, auto_mode=True, brakes_active=False):
        velocity_error = target_speed - current_speed
        self.ek = velocity_error
        
        if abs(self.P_cmd) < self.P_max:
            self.uk = self.uk1 + (self.T/2) * (self.ek + self.ek1)
        else:
            self.uk = self.uk1

        self.P_k_1 = self.P_cmd

        if brakes_active:
            self.P_cmd = 0
            self.uk = 0
            self.ek = 0
        else:
            kp = self.auto_kp if auto_mode else self.manual_kp
            ki = self.auto_ki if auto_mode else self.manual_ki

            P_term = kp * self.ek
            I_term = ki * self.uk
            self.P_cmd = P_term + I_term

            if self.P_cmd > self.P_max:
                self.P_cmd = self.P_max
            elif self.P_cmd < -self.P_max:
                self.P_cmd = -self.P_max

        self.uk1 = self.uk
        self.ek1 = self.ek

        return self.P_cmd
    
##########################################################################################

class BrakeController:
    def __init__(self):
        self.service_brake_active = False
        self.emergency_brake_active = False
        self.manual_eb_engaged = False

    def activate_service_brake(self):
        self.service_brake_active = True
        self.emergency_brake_active = False

    def activate_emergency_brake(self, manual=False):
        self.emergency_brake_active = True
        self.service_brake_active = False
        if manual:
            self.manual_eb_engaged = True

    def release_brakes(self):
        self.service_brake_active = False
        self.emergency_brake_active = False
        self.manual_eb_engaged = False

##########################################################################################

class DoorController:
    def __init__(self):
        self.door_timer = QTimer()
        self.left_door = True
        self.right_door = True

    def set_door_state(self, door_type, state):
        if door_type == "left":
            self.left_door = state
        else:
            self.right_door = state

    def start_door_timer(self, callback, delay=15000):
        self.door_timer.timeout.connect(callback)
        self.door_timer.start(delay)

    def stop_door_timer(self):
        self.door_timer.stop()

##########################################################################################

class TemperatureController:
    def __init__(self):
        self.target_temp = None
        self.temp_timer = QTimer()
        self.current_temp = 70
    
    def set_target_temp(self, temp):
        self.target_temp = temp
        if not self.temp_timer.isActive():
            self.temp_timer.start(2000)

    def update_temp(self):
        if self.current_temp < self.target_temp:
            self.current_temp += 1
        elif self.current_temp > self.target_temp:
            self.current_temp -= 1

        if self.current_temp == self.target_temp:
            self.temp_timer.stop()

##########################################################################################

class TrainControllerUI(QWidget):
    def __init__(self):
        super().__init__()

        self.constants = Constants()
        self.train_state = TrainState()
        self.power_controller = PowerController()
        self.brake_controller = BrakeController()
        self.door_controller = DoorController()
        self.temp_controller = TemperatureController()

        self.current_speed_mps = 0
        self.current_authority = 0
        self.suggested_speed_mps = 20 * self.constants.MPH_TO_MPS
        self.suggested_authority = 0

        self.init_ui()
        self.init_timers()
        self.init_file_watcher()
        self.write_outputs(suggested_speed=20, suggested_authority=0, cabin_lights=True, exterior_lights=True, cabin_temp=70)

    def init_ui(self):
        self.setWindowTitle("B Team Train Control")
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout()
        self.create_title(main_layout)
        self.create_train_selection(main_layout)

        content_layout = QHBoxLayout()
        self.create_control_panel(content_layout)
        self.create_status_panel(content_layout)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        self.connect_signals()
        self.update_ui_from_state()

        # Disable controls initially since auto mode is enabled by default
        self.ext_light_on.setEnabled(False)
        self.ext_light_off.setEnabled(False)
        self.cabin_light_on.setEnabled(False)
        self.cabin_light_off.setEnabled(False)
        self.open_left.setEnabled(False)
        self.close_left.setEnabled(False)
        self.open_right.setEnabled(False)
        self.close_right.setEnabled(False)
        self.setpoint_input.setEnabled(False)
        self.kp_input.setEnabled(False)
        self.ki_input.setEnabled(False)
        self.set_constants_button.setEnabled(False)
        
    def create_title(self, layout):
        title_label = QLabel("B Team Train Control")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

    def create_train_selection(self, layout):
        self.train_select = QComboBox()
        self.train_select.addItems(["Train 1"])
        layout.addWidget(QLabel("Select Train:"))
        layout.addWidget(self.train_select)

    def create_control_panel(self, layout):
        control_panel = QGroupBox("Train Controls")
        control_layout = QVBoxLayout()
        
        self.create_light_controls(control_layout)
        self.create_door_controls(control_layout)
        self.create_temp_controls(control_layout)

        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)

    def create_light_controls(self, layout):
        light_group = QGroupBox("Light Controls")
        light_layout = QVBoxLayout()
        
        ext_light_group = QGroupBox("Exterior Lights")
        ext_light_layout = QHBoxLayout()
        self.ext_light_off = QPushButton("Off")
        self.ext_light_on = QPushButton("On")
        ext_light_layout.addWidget(self.ext_light_off)
        ext_light_layout.addWidget(self.ext_light_on)
        ext_light_group.setLayout(ext_light_layout)
        
        cabin_light_group = QGroupBox("Cabin Lights")
        cabin_light_layout = QHBoxLayout()
        self.cabin_light_off = QPushButton("Off")
        self.cabin_light_on = QPushButton("On")
        cabin_light_layout.addWidget(self.cabin_light_off)
        cabin_light_layout.addWidget(self.cabin_light_on)
        cabin_light_group.setLayout(cabin_light_layout)
        
        light_layout.addWidget(ext_light_group)
        light_layout.addWidget(cabin_light_group)
        light_group.setLayout(light_layout)
        layout.addWidget(light_group)

    def create_door_controls(self, layout):
        door_group = QGroupBox("Door Controls")
        door_layout = QVBoxLayout()
        
        left_door_layout = QHBoxLayout()
        self.open_left = QPushButton("OPEN LEFT")
        self.close_left = QPushButton("CLOSE LEFT")
        left_door_layout.addWidget(self.open_left)
        left_door_layout.addWidget(self.close_left)
        
        right_door_layout = QHBoxLayout()
        self.open_right = QPushButton("OPEN RIGHT")
        self.close_right = QPushButton("CLOSE RIGHT")
        right_door_layout.addWidget(self.open_right)
        right_door_layout.addWidget(self.close_right)
        
        door_layout.addLayout(left_door_layout)
        door_layout.addLayout(right_door_layout)
        door_group.setLayout(door_layout)
        layout.addWidget(door_group)

    def create_temp_controls(self, layout):
        temp_group = QGroupBox("Temperature Control")
        temp_layout = QVBoxLayout()
        
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(40)
        self.temp_slider.setMaximum(80)
        self.temp_slider.setTickPosition(QSlider.TicksBelow)
        self.temp_slider.setTickInterval(1)
        
        self.current_temp_label = QLabel("Current Temp: -- °F")
        self.target_temp_label = QLabel("Target Temp: -- °F")
        self.set_temp_btn = QPushButton("Set Cabin Temp")
        
        temp_layout.addWidget(QLabel("Set Temperature:"))
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.current_temp_label)
        temp_layout.addWidget(self.target_temp_label)
        temp_layout.addWidget(self.set_temp_btn)
        temp_group.setLayout(temp_layout)
        layout.addWidget(temp_group)

    def create_status_panel(self, layout):
        status_panel = QGroupBox("Train Status and Power Control")
        status_layout = QVBoxLayout()
        
        self.create_status_display(status_layout)
        self.create_power_controls(status_layout)
        self.create_brake_controls(status_layout)
        
        status_panel.setLayout(status_layout)
        layout.addWidget(status_panel)

    def create_status_display(self, layout):
        status_group = QGroupBox("Current Status")
        status_display_layout = QVBoxLayout()
        
        self.suggested_authority_label = QLabel("Suggested Authority: 0 m")
        self.suggested_speed_label = QLabel("Suggested speed: 0 mph")
        self.authority_label = QLabel("Current Authority: 0 m")
        self.speed_label = QLabel("Current Speed: 0 mph")
        self.service_brake_label = QLabel("Service Brake: Off")
        self.emergency_brake_label = QLabel("Emergency Brake: Off")
        self.left_door_label = QLabel("Left Door: Closed")
        self.right_door_label = QLabel("Right Door: Closed")
        self.cabin_lights_label = QLabel("Cabin Lights: Off")
        self.outside_lights_label = QLabel("Outside Lights: Off")
        self.temperature_label = QLabel("Cabin Temp: -- °F")
        self.p_cmd_label = QLabel("Commanded Power: 0 kW")

        status_display_layout.addWidget(self.suggested_authority_label)
        status_display_layout.addWidget(self.suggested_speed_label)
        status_display_layout.addWidget(self.authority_label)
        status_display_layout.addWidget(self.speed_label)
        status_display_layout.addWidget(self.service_brake_label)
        status_display_layout.addWidget(self.emergency_brake_label)
        status_display_layout.addWidget(self.left_door_label)
        status_display_layout.addWidget(self.right_door_label)
        status_display_layout.addWidget(self.cabin_lights_label)
        status_display_layout.addWidget(self.outside_lights_label)
        status_display_layout.addWidget(self.temperature_label)
        status_display_layout.addWidget(self.p_cmd_label)
        
        status_group.setLayout(status_display_layout)
        layout.addWidget(status_group)

    def create_power_controls(self, layout):
        power_group = QGroupBox("Power Control")
        power_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.setpoint_input = QLineEdit("0")
        form_layout.addRow("Setpoint Speed (mph):", self.setpoint_input)
        
        self.kp_input = QLineEdit("0")
        form_layout.addRow("Kp Value:", self.kp_input)

        self.ki_input = QLineEdit("0")
        form_layout.addRow("Ki Value:", self.ki_input)
        
        self.p_cmd_display = QLabel("0 kW")
        form_layout.addRow("Commanded Power:", self.p_cmd_display)
        
        self.set_constants_button = QPushButton("Update Power")
        
        power_layout.addLayout(form_layout)
        power_layout.addWidget(self.set_constants_button)
        power_group.setLayout(power_layout)
        layout.addWidget(power_group)

        # Initialize disabled since auto mode is default
        self.setpoint_input.setEnabled(False)
        self.kp_input.setEnabled(False)
        self.ki_input.setEnabled(False)
        self.set_constants_button.setEnabled(False)

    def create_brake_controls(self, layout):
        brake_group = QGroupBox("Brake Controls")
        brake_layout = QHBoxLayout()
        
        self.sb_button = QPushButton("Service Brake")
        self.sb_button.setStyleSheet("background-color: orange;")
        self.eb_button = QPushButton("Emergency Brake")
        self.eb_button.setStyleSheet("background-color: red; color: white;")
        self.clear_brakes_button = QPushButton("Release Brakes")
        self.clear_brakes_button.setStyleSheet("background-color: green; color: white;")
        
        brake_layout.addWidget(self.sb_button)
        brake_layout.addWidget(self.eb_button)
        brake_layout.addWidget(self.clear_brakes_button)
        brake_group.setLayout(brake_layout)
        layout.addWidget(brake_group)
        
        self.auto_checkbox = QCheckBox("Automatic Mode")
        self.auto_checkbox.setChecked(True)
        layout.addWidget(self.auto_checkbox)

    def init_timers(self):
        self.master_timer = QTimer(self)
        self.master_timer.timeout.connect(self.update_from_files)
        self.master_timer.start(1000)

        self.door_controller.door_timer.timeout.connect(self.close_doors_after_delay)
        self.temp_controller.temp_timer.timeout.connect(self.update_temp)

    def init_file_watcher(self):
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath('train1_outputs.json')
        self.file_watcher.fileChanged.connect(self.update_from_files)

    def connect_signals(self):
        # Light controls
        self.ext_light_off.clicked.connect(lambda: self.set_light_state("outside_lights", False))
        self.ext_light_on.clicked.connect(lambda: self.set_light_state("outside_lights", True))
        self.cabin_light_off.clicked.connect(lambda: self.set_light_state("cabin_lights", False))
        self.cabin_light_on.clicked.connect(lambda: self.set_light_state("cabin_lights", True))
        
        # Door controls
        self.open_left.clicked.connect(lambda: self.set_door_state("left", False))
        self.close_left.clicked.connect(lambda: self.set_door_state("left", True))
        self.open_right.clicked.connect(lambda: self.set_door_state("right", False))
        self.close_right.clicked.connect(lambda: self.set_door_state("right", True))
        
        # Temperature controls
        self.temp_slider.valueChanged.connect(self.update_temp_label)
        self.set_temp_btn.clicked.connect(self.set_temp_clicked)
        
        # Brake controls
        self.sb_button.clicked.connect(self.sb_clicked)
        self.eb_button.clicked.connect(self.eb_clicked)
        self.clear_brakes_button.clicked.connect(self.clear_brakes)
        
        # Power controls
        self.set_constants_button.clicked.connect(self.calculate_power)
        self.auto_checkbox.stateChanged.connect(self.auto_clicked)
  
    def set_light_state(self, light_type, state):
        setattr(self.train_state, light_type, state)
        self.update_ui_from_state()
        if light_type == "cabin_lights":
            self.write_outputs(cabin_lights=state)
        elif light_type == "outside_lights":
            self.write_outputs(exterior_lights=state)
        self.update_tb()

    def set_door_state(self, door_type, state):
        self.door_controller.set_door_state(door_type, state)
        self.update_ui_from_state()
        self.write_outputs(**{f"{door_type}_door": int(not state)})
        self.update_tb()

    def update_ui_from_state(self):

        # Update light buttons
        self.ext_light_on.setEnabled(not self.train_state.outside_lights)
        self.ext_light_off.setEnabled(self.train_state.outside_lights)
        self.cabin_light_on.setEnabled(not self.train_state.cabin_lights)
        self.cabin_light_off.setEnabled(self.train_state.cabin_lights)
        
        # Update door buttons
        self.open_left.setEnabled(self.door_controller.left_door)
        self.close_left.setEnabled(not self.door_controller.left_door)
        self.open_right.setEnabled(self.door_controller.right_door)
        self.close_right.setEnabled(not self.door_controller.right_door)
        
        # Update labels
        self.left_door_label.setText(f"Left Door: {'Closed' if self.door_controller.left_door else 'Open'}")
        self.right_door_label.setText(f"Right Door: {'Closed' if self.door_controller.right_door else 'Open'}")
        self.cabin_lights_label.setText(f"Cabin Lights: {'On' if self.train_state.cabin_lights else 'Off'}")
        self.outside_lights_label.setText(f"Outside Lights: {'On' if self.train_state.outside_lights else 'Off'}")
        self.temperature_label.setText(f"Cabin Temp: {self.temp_controller.current_temp} °F")
        
        # Update brake status
        self.service_brake_label.setText(f"Service Brake: {'On' if self.brake_controller.service_brake_active else 'Off'}")
        self.emergency_brake_label.setText(f"Emergency Brake: {'On' if self.brake_controller.emergency_brake_active else 'Off'}")
        
        # Update temperature display
        self.temperature_label.setText(f"Cabin Temp: {self.temp_controller.current_temp} °F")
        self.current_temp_label.setText(f"Current Temp: {self.temp_controller.current_temp} °F")
        self.temp_slider.setValue(self.temp_controller.current_temp)

    def update_temp_label(self):
        self.target_temp_label.setText(f"Target Temp: {self.temp_slider.value()} °F")
    
    def set_temp_clicked(self):
        self.temp_controller.set_target_temp(self.temp_slider.value())
        print(f"Target temp set to {self.temp_slider.value()} °F")

    def update_temp(self):
        self.temp_controller.update_temp()
        self.current_temp_label.setText(f"Current Temp: {self.temp_controller.current_temp} °F")
        self.temperature_label.setText(f"Cabin Temp: {self.temp_controller.current_temp} °F")
        self.write_outputs(cabin_temp=self.temp_controller.current_temp)

    def read_train_outputs(self, file_path='train1_outputs.json'):
        try:
            with open(file_path, mode='r') as file:
                data = json.load(file)

            speed_mph = float(data.get('Actual_Speed', 0))
            self.current_speed_mps = speed_mph * self.constants.MPH_TO_MPS
            self.current_authority = float(data.get('Actual_Authority', 0))
            delta_position = float(data.get('Delta_Position', 0))

            suggested_speed_auth = data.get('Suggested_Speed_Authority', '')
            if suggested_speed_auth and all(bit in '01' for bit in suggested_speed_auth):
                if len(suggested_speed_auth) < 10:
                    suggested_speed_auth = suggested_speed_auth.ljust(10, '0')
                msb = suggested_speed_auth[0]  # First bit determines speed (0) or authority (1)
                remaining_bits = suggested_speed_auth[1:] if len(suggested_speed_auth) > 1 else '0'
            
            # Convert remaining bits to decimal value
                value = int(remaining_bits, 2) if remaining_bits else 0

                if msb == '1':
                # Handle authority
                    self.suggested_authority = value
                    self.write_outputs(suggested_authority=value)
                else:
                # Handle speed - use value directly as mph
                    if value > 0:
                        suggested_speed_mph = value
                        self.suggested_speed_mps = suggested_speed_mph * self.constants.MPH_TO_MPS
                        self.write_outputs(suggested_speed=suggested_speed_mph)
            else:
            # Default case if format is invalid
                suggested_speed_mph = 20
                self.suggested_speed_mps = suggested_speed_mph * self.constants.MPH_TO_MPS
                self.write_outputs(suggested_speed=suggested_speed_mph)

            beacon_data = data.get('Beacon', '')
            station_distance = float('inf')
            station_side = 'right'

            if beacon_data:
                beacon_parts = beacon_data.split(', ')
                beacon_dict = {}
                for part in beacon_parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        beacon_dict[key.strip()] = value.strip()

                if 'station_distance' in beacon_dict:
                    try:
                        station_distance = float(beacon_dict['station_distance'])
                    except ValueError:
                        station_distance = float('inf')

                if 'station_side' in beacon_dict:
                    station_side = beacon_dict['station_side'].lower()

            if (abs(station_distance - delta_position) <= 5 and not self.brake_controller.service_brake_active):
                self.brake_controller.activate_service_brake()
                self.write_outputs(service_brake=1)
                print(f"Service brake activated - approaching station.")

            if(self.current_speed_mps < 0.1 and
               self.brake_controller.service_brake_active and
               abs(station_distance - delta_position) <= 5 and
               not self.door_controller.door_timer.isActive() and
               (self.door_controller.left_door or self.door_controller.right_door)):
                
                if station_side == 'left':
                    self.door_controller.set_door_state("left", False)
                    self.write_outputs(left_door=0, right_door=1)
                    print("Opening LEFT doors at station")
                else:
                    self.door_controller.set_door_state("right", False)
                    self.write_outputs(left_door=1, right_door=0)
                    print("Opening RIGHT doors at station")

                self.update_ui_from_state()
                self.door_controller.start_door_timer(self.close_doors_after_delay)

            brake_fail = data.get('Brake_Fail', False)
            signal_fail = data.get('Signal_Fail', False)
            engine_fail = data.get('Engine_Fail', False)
            emergency_brake = data.get('Emergency_Brake', False)

            if not self.brake_controller.manual_eb_engaged:
                new_eb_status = brake_fail or signal_fail or engine_fail or emergency_brake

                if new_eb_status != self.brake_controller.emergency_brake_active:
                    self.write_outputs(emergency_brake=1 if new_eb_status else 0)

                if new_eb_status:
                    self.brake_controller.activate_emergency_brake()
                else:
                    self.brake_controller.emergency_brake_active = False

            service_brake = data.get('Service_Brake', False)
            if service_brake and not self.brake_controller.emergency_brake_active:
                self.brake_controller.activate_service_brake()
                self.write_outputs(service_brake=1)
            
            current_speed_mph = self.current_speed_mps * self.constants.MPS_TO_MPH
            suggested_speed_mph = self.suggested_speed_mps * self.constants.MPS_TO_MPH

            self.suggested_authority_label.setText(f"Suggested Authority: {self.suggested_authority} m")
            self.suggested_speed_label.setText(f"Suggested Speed: {suggested_speed_mph:.1f} mph")
            self.authority_label.setText(f"Current Authority: {self.current_authority:.2f} m")
            self.speed_label.setText(f"Current Speed: {current_speed_mph:.1f} mph")
            self.service_brake_label.setText(f"Service Brake: {'On' if self.brake_controller.service_brake_active else 'Off'}")
            self.emergency_brake_label.setText(f"Emergency Brake: {'On' if self.brake_controller.emergency_brake_active else 'Off'}")

            return True
                
        except Exception as e:
            print(f"Error reading test bench: {e}")
            return False
        
    def auto_clicked(self):
        auto_mode = self.auto_checkbox.isChecked()

        if auto_mode:
            print("Automatic Mode Enabled!")
            self.master_timer.start(1000)
            self.ext_light_on.setEnabled(False)
            self.ext_light_off.setEnabled(False)
            self.cabin_light_on.setEnabled(False)
            self.cabin_light_off.setEnabled(False)
            self.open_left.setEnabled(False)
            self.close_left.setEnabled(False)
            self.open_right.setEnabled(False)
            self.close_right.setEnabled(False)

            # Disable power control inputs
            self.setpoint_input.setEnabled(False)
            self.kp_input.setEnabled(False)
            self.ki_input.setEnabled(False)
            self.set_constants_button.setEnabled(False)
            
            # Clear any manual input values
            self.setpoint_input.clear()
            self.kp_input.clear()
            self.ki_input.clear()
        else:
            print("Automatic Mode Disabled")
            self.master_timer.stop()

            self.ext_light_on.setEnabled(not self.train_state.outside_lights)
            self.ext_light_off.setEnabled(self.train_state.outside_lights)
            self.cabin_light_on.setEnabled(not self.train_state.cabin_lights)
            self.cabin_light_off.setEnabled(self.train_state.cabin_lights)
            self.open_left.setEnabled(self.door_controller.left_door)
            self.close_left.setEnabled(not self.door_controller.left_door)
            self.open_right.setEnabled(self.door_controller.right_door)
            self.close_right.setEnabled(not self.door_controller.right_door)

            # Enable power control inputs
            self.setpoint_input.setEnabled(True)
            self.kp_input.setEnabled(True)
            self.ki_input.setEnabled(True)
            self.set_constants_button.setEnabled(True)
            
            # Set default values for manual mode
            self.setpoint_input.setText("0")
            self.kp_input.setText("0")
            self.ki_input.setText("0")

    def sb_clicked(self):
        if not self.brake_controller.emergency_brake_active:
            self.brake_controller.activate_service_brake()
            self.write_outputs(service_brake=1)
            print("Service Brake Engaged")

    def close_doors_after_delay(self):
        self.door_controller.stop_door_timer()
        self.door_controller.set_door_state("left", True)
        self.door_controller.set_door_state("right", True)
        self.write_outputs(left_door=1, right_door=1)
        self.update_ui_from_state()
        print("Doors closed after delay")

    def write_outputs(self, power=None, emergency_brake=None, service_brake=None, 
                    suggested_speed=None, suggested_authority=None,
                    left_door=None, right_door=None, cabin_lights=None, exterior_lights=None, cabin_temp=None):
        try:
            try:
                with open('TC_outputs.json', 'r') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}

            if power is not None:
                data['Commanded_Power'] = round(power, 2)
            if emergency_brake is not None:
                data['Emergency_Brake'] = bool(emergency_brake)
            if service_brake is not None:
                data['Service_Brake'] = bool(service_brake)
            if suggested_speed is not None:
                data['Suggested_Speed'] = round(suggested_speed, 1)
            if suggested_authority is not None:
                data['Suggested_Authority'] = round(suggested_authority, 1)
            if left_door is not None:
                data['Left_Door'] = bool(left_door)
            if right_door is not None:
                data['Right_Door'] = bool(right_door)
            if cabin_lights is not None:
                data['Cabin_Lights'] = bool(cabin_lights)
            if exterior_lights is not None:
                data['Exterior_Lights'] = bool(exterior_lights)
            if cabin_temp is not None:
                data['Cabin_Temp'] = int(cabin_temp)

            with open('TC_outputs.json', 'w') as f:
                json.dump(data, f, indent=4)
            
        except Exception as e:
            print(f"Error writing to TC_outputs.json: {e}")

    def eb_clicked(self, checked=False):
        self.brake_controller.activate_emergency_brake(manual=True)
        self.write_outputs(emergency_brake=1)
        print("Emergency Brake Engaged")           

    def update_tb(self):
        self.service_brake_label.setText(f"Service Brake: {'On' if self.brake_controller.service_brake_active else 'Off'}")
        self.emergency_brake_label.setText(f"Emergency Brake: {'On' if self.brake_controller.emergency_brake_active else 'Off'}")

        if self.brake_controller.service_brake_active:
            self.write_outputs(service_brake=1)
        if self.brake_controller.emergency_brake_active:
            self.write_outputs(emergency_brake=1)

    def clear_brakes(self):
        self.brake_controller.release_brakes()
        self.write_outputs(emergency_brake=0, service_brake=0)
        print("Brakes Released")
        self.service_brake_label.setText("Service Brake: Off")
        self.emergency_brake_label.setText("Emergency Brake: Off")

    def calculate_power(self):
        try:
            auto_mode = self.auto_checkbox.isChecked()
            
            if auto_mode:
                target_speed = self.suggested_speed_mps
            else:
                self.power_controller.manual_kp = float(self.kp_input.text())
                self.power_controller.manual_ki = float(self.ki_input.text())
                target_speed = float(self.setpoint_input.text()) * self.constants.MPH_TO_MPS

            power = self.power_controller.calculate_power(
                self.current_speed_mps,
                target_speed,
                auto_mode,
                self.brake_controller.service_brake_active or self.brake_controller.emergency_brake_active
            )

            power_kw = power / 1000
            self.p_cmd_display.setText(f"{power_kw:.2f} kW")
            self.p_cmd_label.setText(f"Commanded Power: {power_kw:.2f} kW")
            self.write_outputs(power=power)

        except ValueError:
            print("Please enter valid numerical values for Kp and Ki")

    def update_power_display(self):
        self.calculate_power()

    def update_from_files(self):
        self.read_train_outputs()
        self.update_power_display()    
    
#######################################################################

def main():
    app = QApplication([])
    window = TrainControllerUI()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

