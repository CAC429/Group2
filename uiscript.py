# Philip Sherman
# Trains Group 2
# Train Controller SW UI
# Created: 2/19/2025
# Last Updated: 4/24/2025

import json
import os
from glob import glob
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

class TrainState:
    def __init__(self):
        # Door states
        self.left_door = False
        self.right_door = False
        
        # Light states
        self.outside_lights = True
        self.cabin_lights = True
        
        # Temperature
        self.cabin_temp = 70
        
        # Brake states
        self.service_brakes = False
        self.emergency_brakes = False
        
        # Speed and authority
        self.current_speed_mph = 0
        self.suggested_speed_mph = 20
        self.current_authority = 0
        self.suggested_authority = 0
        
        # Station handling
        self.stopping_sequence_active = False
        self.station_stop_cooldown = False
        self.leaving_station = False
        
        # Position and beacon
        self.delta_position = 0
        self.beacon = ""

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
    
class BrakeController:
    def __init__(self):
        self.service_brake_active = False
        self.emergency_brake_active = False
        self.manual_brake = False

    def activate_service_brake(self, manual=False):
        if not self.emergency_brake_active:
            self.service_brake_active = True
            self.emergency_brake_active = False
            self.manual_brake = manual

    def activate_emergency_brake(self, manual=False):
        self.emergency_brake_active = True
        self.service_brake_active = False
        self.manual_brake = manual

    def release_brakes(self):
        self.service_brake_active = False
        self.emergency_brake_active = False
        self.manual_brake = False

class DoorController:
    def __init__(self, train_state):
        self.door_timer = QTimer()
        self.left_door = False
        self.right_door = False
        self.train_state = train_state  # Store reference to train state
        
    def set_door_state(self, door_type, state):
        if state:
            if self.train_state.current_speed_mph > 0.1:  # Now uses the stored state
                print("Cannot open doors while train is moving")
                return
        if door_type == "left":
            self.left_door = state
        else:
            self.right_door = state

    def start_door_timer(self, callback, delay=15000):
        self.door_timer.timeout.connect(callback)
        self.door_timer.start(delay)

    def stop_door_timer(self):
        self.door_timer.stop()

class TemperatureController:
    def __init__(self):
        self.target_temp = 70
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

class TrainControllerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.constants = Constants()
        self.train_instances = {}  # Dictionary to store train instances
        self.current_train_id = None

        self.cleanup_output_files()
        
        self.init_ui()
        self.scan_for_trains()
        self.init_timers()
        self.update_ui_from_state()

    def read_timer_interval(self):
        try:
            with open('TIMER.json', 'r') as f:
                timer_data = json.load(f)
                return int(timer_data.get('timer_interval', 1000))  # Default to 1000ms if not found
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            print("Warning: Could not read TIMER.json, using default interval of 1000ms")
            return 1000  # Default value

    def cleanup_output_files(self):
        try:
            output_files = glob('TC*_outputs.json')
            for file in output_files:
                try:
                    os.remove(file)
                    print(f"Deleted existing output file: {file}")
                except Exception as e:
                    print(f"Error deleting file {file}: {e}")
        except Exception as e:
            print(f"Error cleaning up output files: {e}")
        
    def scan_for_trains(self):
        train_files = glob('train*_outputs.json')
        
        for file in train_files:
            try:
                train_id = file.split('train')[1].split('_outputs.json')[0]
                if train_id not in self.train_instances:
                    self.train_instances[train_id] = self.create_train_instance()
                    self.initialize_output_file(f"TC{train_id}_outputs.json")

                if f"Train {train_id}" not in [self.train_select.itemText(i) for i in range(self.train_select.count())]:
                    self.train_select.addItem(f"Train {train_id}")
            except Exception as e:
                print(f"Error processing train file {file}: {e}")
        
        if self.train_instances and self.current_train_id is None:
            self.current_train_id = next(iter(self.train_instances.keys()))
            self.train_select.setCurrentText(f"Train {self.current_train_id}")

    def initialize_output_file(self, filename):
        default_values = {
            "Commanded Power": 0.0,
            "Suggested Speed": 20.0,
            "Suggested Authority": 0,
            "Emergency Brake": False,
            "Service Brake": False,
            "Left Door": False,
            "Right Door": False,
            "Cabin Lights": True,
            "Exterior Lights": True,
            "Cabin Temp": 70
        }    
        try:
            with open(filename, 'w') as f:
                json.dump(default_values, f, indent=4)
        except Exception as e:
            print(f"Error initializing {filename}: {e}")

    def create_train_instance(self):
        state = TrainState()  # Create the state first
        return {
            'state': state,
            'power_controller': PowerController(),
            'brake_controller': BrakeController(),
            'door_controller': DoorController(state),  # Pass the state to DoorController
            'temp_controller': TemperatureController()
        }
    
    def get_current_train(self):
        if self.current_train_id is None or self.current_train_id not in self.train_instances:
            return None
        return self.train_instances[self.current_train_id]
    
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
        
    def create_title(self, layout):
        title_label = QLabel("B Team Train Control")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

    def create_train_selection(self, layout):
        self.train_select = QComboBox()
        layout.addWidget(QLabel("Select Train:"))
        layout.addWidget(self.train_select)
        self.train_select.currentTextChanged.connect(self.on_train_selected)

    def on_train_selected(self, text):
        try:
            train_id = text.split(' ')[1]  # Extract ID from "Train X"
            if train_id in self.train_instances:
                self.current_train_id = train_id
                self.update_ui_from_state()
        except Exception as e:
            print(f"Error switching trains: {e}")

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
        interval = self.read_timer_interval()
        self.master_timer.start(interval)

        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPaths(glob('train*_outputs.json'))
        self.file_watcher.fileChanged.connect(self.handle_file_changed)

    def handle_file_changed(self, path):
        try:
            train_id = path.split('train')[1].split('_outputs.json')[0]
            if train_id == self.current_train_id:
                self.update_from_files()
        except Exception as e:
            print(f"Error handling file change: {e}")

    def connect_signals(self):
        # Light controls
        self.ext_light_off.clicked.connect(lambda: self.set_light_state("outside_lights", False))
        self.ext_light_on.clicked.connect(lambda: self.set_light_state("outside_lights", True))
        self.cabin_light_off.clicked.connect(lambda: self.set_light_state("cabin_lights", False))
        self.cabin_light_on.clicked.connect(lambda: self.set_light_state("cabin_lights", True))
        
        # Door controls
        self.open_left.clicked.connect(lambda: self.set_door_state("left", True))
        self.close_left.clicked.connect(lambda: self.set_door_state("left", False))
        self.open_right.clicked.connect(lambda: self.set_door_state("right", True))
        self.close_right.clicked.connect(lambda: self.set_door_state("right", False))
        
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
        train = self.get_current_train()
        if train is None:
            return
            
        setattr(train['state'], light_type, state)
        self.update_ui_from_state()
        
        output_file = f"TC{self.current_train_id}_outputs.json"
        if light_type == "cabin_lights":
            self.write_outputs(output_file, cabin_lights=state)
        elif light_type == "outside_lights":
            self.write_outputs(output_file, exterior_lights=state)
        self.update_tb()

    def set_door_state(self, door_type, state):
        train = self.get_current_train()
        if train is None:
            return
            
        train['door_controller'].set_door_state(door_type, state)
        self.update_ui_from_state()
        
        output_file = f"TC{self.current_train_id}_outputs.json"
        self.write_outputs(output_file, **{f"{door_type}_door": int(state)})
        self.update_tb()

    def update_ui_from_state(self):
        train = self.get_current_train()
        if train is None:
            return
            
        state = train['state']  # Make sure we're using the instance
        door_controller = train['door_controller']
        temp_controller = train['temp_controller']
        brake_controller = train['brake_controller']

        # Update controls enabled state
        self.set_controls_enabled_state(not self.auto_checkbox.isChecked())
        
        # Update labels
        self.left_door_label.setText(f"Left Door: {'Open' if door_controller.left_door else 'Closed'}")
        self.right_door_label.setText(f"Right Door: {'Open' if door_controller.right_door else 'Closed'}")
        self.cabin_lights_label.setText(f"Cabin Lights: {'On' if state.cabin_lights else 'Off'}")
        self.outside_lights_label.setText(f"Outside Lights: {'On' if state.outside_lights else 'Off'}")
        self.temperature_label.setText(f"Cabin Temp: {temp_controller.current_temp} °F")
        
        # Update brake status
        self.service_brake_label.setText(f"Service Brake: {'On' if brake_controller.service_brake_active else 'Off'}")
        self.emergency_brake_label.setText(f"Emergency Brake: {'On' if brake_controller.emergency_brake_active else 'Off'}")
        
        # Update temperature display
        self.temperature_label.setText(f"Cabin Temp: {temp_controller.current_temp} °F")
        self.current_temp_label.setText(f"Current Temp: {temp_controller.current_temp} °F")
        self.temp_slider.setValue(temp_controller.current_temp)

    def update_temp_label(self):
        self.target_temp_label.setText(f"Target Temp: {self.temp_slider.value()} °F")
    
    def set_temp_clicked(self):
        train = self.get_current_train()
        if train is None:
            return
            
        train['temp_controller'].set_target_temp(self.temp_slider.value())
        print(f"Target temp set to {self.temp_slider.value()} °F")
        
        output_file = f"TC{self.current_train_id}_outputs.json"
        self.write_outputs(output_file, cabin_temp=self.temp_slider.value())

    def update_temp(self):
        train = self.get_current_train()
        if train is None:
            return
            
        train['temp_controller'].update_temp()
        self.current_temp_label.setText(f"Current Temp: {train['temp_controller'].current_temp} °F")
        self.temperature_label.setText(f"Cabin Temp: {train['temp_controller'].current_temp} °F")
        
        output_file = f"TC{self.current_train_id}_outputs.json"
        self.write_outputs(output_file, cabin_temp=train['temp_controller'].current_temp)

    def read_train_outputs(self, file_path=None):
        if self.current_train_id is None:
            return False
                    
        train = self.get_current_train()
        if train is None:
            return False

        try:
            file_path = file_path or f'train{self.current_train_id}_outputs.json'
            
            # Safely read and parse the file
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                print(f"Train outputs file not found: {file_path}")
                return False
            except json.JSONDecodeError:
                print(f"Invalid JSON in train outputs file: {file_path}")
                return False

            # Speed is already in MPH
            train['state'].current_speed_mph = float(data.get('Actual_Speed', 0))
            train['state'].current_authority = float(data.get('Actual_Authority', 0))
            train['state'].delta_position = float(data.get('Delta_Position', 0))
            train['state'].beacon = data.get('Beacon', '')
            
            # Suggested speed and authority handling
            suggested_speed_auth = data.get('Suggested_Speed_Authority', '').strip()
            output_file = f"TC{self.current_train_id}_outputs.json"
            
            if suggested_speed_auth:
                # No padding - use the binary string as-is
                mode_bit = suggested_speed_auth[0] if len(suggested_speed_auth) > 0 else '0'
                value_bits = suggested_speed_auth[1:] if len(suggested_speed_auth) > 1 else '0'
                
                # Convert binary to decimal
                try:
                    value = int(value_bits, 2) if value_bits else 0
                except ValueError:
                    value = 0
                    print(f"Invalid binary value in Suggested_Speed_Authority: {value_bits}")
                
                if mode_bit == '0':  # Speed value
                    train['state'].suggested_speed_mph = value
                    self.write_outputs(output_file, suggested_speed=value)
                else:  # Authority value
                    train['state'].suggested_authority = value
                    self.write_outputs(output_file, suggested_authority=value)

                    if value == 0:
                        print("Activating emergency brake: suggested authority is 0")
                        train['brake_controller'].activate_emergency_brake()
                        self.write_outputs(output_file, emergency_brake=1, service_brake=0)

            # Update UI labels
            self.speed_label.setText(f"Current Speed: {train['state'].current_speed_mph:.1f} mph")
            self.suggested_speed_label.setText(f"Suggested Speed: {train['state'].suggested_speed_mph:.1f} mph")
            self.authority_label.setText(f"Current Authority: {train['state'].current_authority:.1f} m")
            self.suggested_authority_label.setText(f"Suggested Authority: {train['state'].suggested_authority:.1f} m")

            # Check for emergency brake or failures
            emergency_brake_active = bool(data.get('Emergency_Brake', 0))
            brake_fail = bool(data.get('Brake_Fail', 0))
            signal_fail = bool(data.get('Signal_Fail', 0))
            engine_fail = bool(data.get('Engine_Fail', 0))
            
            if emergency_brake_active or brake_fail or signal_fail or engine_fail:
                print("Safety system activated - emergency conditions detected")
                train['brake_controller'].activate_emergency_brake()
                output_file = f"TC{self.current_train_id}_outputs.json"
                self.write_outputs(output_file, emergency_brake=1, service_brake=0)
                print("Emergency brake activated due to:")
                if emergency_brake_active:
                    print("- Emergency brake command from track")
                if brake_fail:
                    print("- Brake failure detected")
                if signal_fail:
                    print("- Signal failure detected")
                if engine_fail:
                    print("- Engine failure detected")
            else:
                # Only release brakes if they were activated by these conditions
                if (train['brake_controller'].emergency_brake_active and 
                    not train['brake_controller'].manual_brake):
                    train['brake_controller'].release_brakes()
                    output_file = f"TC{self.current_train_id}_outputs.json"
                    self.write_outputs(output_file, emergency_brake=0)

            return True
            
        except Exception as e:
            print(f"Error reading train outputs: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def auto_clicked(self):
        auto_mode = self.auto_checkbox.isChecked()
        train = self.get_current_train()
        if train is None:
            return

        if auto_mode:
            print("Automatic Mode Enabled!")
            interval = self.read_timer_interval()
            self.master_timer.start(interval)
            self.set_controls_enabled_state(False)  # Disable and gray out controls

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
            self.set_controls_enabled_state(True)  # Enable controls

            # Enable power control inputs
            self.setpoint_input.setEnabled(True)
            self.kp_input.setEnabled(True)
            self.ki_input.setEnabled(True)
            self.set_constants_button.setEnabled(True)
            
            # Set default values for manual mode
            self.setpoint_input.setText("0")
            self.kp_input.setText("0")
            self.ki_input.setText("0")

    def set_controls_enabled_state(self, enabled):
        # Light controls
        self.ext_light_off.setEnabled(enabled and self.get_current_train()['state'].outside_lights)
        self.ext_light_on.setEnabled(enabled and not self.get_current_train()['state'].outside_lights)
        self.cabin_light_off.setEnabled(enabled and self.get_current_train()['state'].cabin_lights)
        self.cabin_light_on.setEnabled(enabled and not self.get_current_train()['state'].cabin_lights)
        
        # Door controls
        door_controller = self.get_current_train()['door_controller']
        self.open_left.setEnabled(enabled and not door_controller.left_door)  # Enable open button if door is closed
        self.close_left.setEnabled(enabled and door_controller.left_door)     # Enable close button if door is open
        self.open_right.setEnabled(enabled and not door_controller.right_door)  # Enable open button if door is closed
        self.close_right.setEnabled(enabled and door_controller.right_door)     # Enable close button if door is open
        
        # Set styles to gray out when disabled
        style = "background-color: #e0e0e0; color: #a0a0a0;" if not enabled else ""
        self.ext_light_off.setStyleSheet(style)
        self.ext_light_on.setStyleSheet(style)
        self.cabin_light_off.setStyleSheet(style)
        self.cabin_light_on.setStyleSheet(style)
        self.open_left.setStyleSheet(style)
        self.close_left.setStyleSheet(style)
        self.open_right.setStyleSheet(style)
        self.close_right.setStyleSheet(style)

    def sb_clicked(self):
        train = self.get_current_train()
        if train is None:
            return
            
        brake_controller = train['brake_controller']
        
        # Toggle service brake if emergency brake isn't manually engaged
        if not brake_controller.emergency_brake_active:
            # Toggle the service brake state
            brake_controller.activate_service_brake(manual=True)
            print("Service Brake Engaged through manual")
            
            # Update outputs and UI
            output_file = f"TC{self.current_train_id}_outputs.json"
            self.write_outputs(output_file, service_brake=1, emergency_brake=0)
            self.update_ui_from_state()
            self.update_tb()

    def close_doors_after_delay(self, door_controller):
        door_controller.stop_door_timer()
        door_controller.set_door_state("left", True)
        door_controller.set_door_state("right", True)
        output_file = f"TC{self.current_train_id}_outputs.json"
        self.write_outputs(output_file, left_door=1, right_door=1)
        self.update_ui_from_state()
        print("Doors closed after delay")

    def write_outputs(self, filename, **kwargs):
        try:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {
                    "Commanded Power": 0.0,
                    "Suggested Speed": 20.0,
                    "Suggested Authority": 0,
                    "Emergency Brake": False,
                    "Service Brake": False,
                    "Left Door": False,
                    "Right Door": False,
                    "Cabin Lights": True,
                    "Exterior Lights": True,
                    "Cabin Temp": 70
                }

            # Update all provided values
            for key, value in kwargs.items():
                if key == "power":
                    data["Commanded Power"] = round(value, 2)
                elif key == "suggested_speed":
                    data["Suggested Speed"] = int(value)
                elif key == "suggested_authority":
                    data['Suggested Authority'] = int(value)
                elif key == "service_brake":
                    data["Service Brake"] = bool(value)
                elif key == "emergency_brake":
                    data["Emergency Brake"] = bool(value)
                elif key == "left_door":
                    data["Left Door"] = bool(value)
                elif key == "right_door":
                    data["Right Door"] = bool(value)
                elif key == "cabin_lights":
                    data["Cabin Lights"] = bool(value)
                elif key == "exterior_lights":
                    data["Exterior Lights"] = bool(value)
                elif key == "cabin_temp":
                    data["Cabin Temp"] = int(value)

            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            print(f"Error writing to {filename}: {e}")

    def eb_clicked(self, checked=False):
        train = self.get_current_train()
        if train is None:
            return
            
        brake_controller = train['brake_controller']
        
        # Toggle emergency brake if service brake isn't manually engaged
        if not brake_controller.service_brake_active:
            brake_controller.activate_emergency_brake(manual=True)
            output_file = f"TC{self.current_train_id}_outputs.json"
            self.write_outputs(output_file, emergency_brake=1, service_brake=0)
            print("Emergency Brake Engaged")
            self.update_ui_from_state()
            self.update_tb()           

    def update_tb(self):
        train = self.get_current_train()
        if train is None:
            return
            
        brake_controller = train['brake_controller']
        
        self.service_brake_label.setText(f"Service Brake: {'On' if brake_controller.service_brake_active else 'Off'}")
        self.emergency_brake_label.setText(f"Emergency Brake: {'On' if brake_controller.emergency_brake_active else 'Off'}")

        output_file = f"TC{self.current_train_id}_outputs.json"
        if brake_controller.service_brake_active:
            self.write_outputs(output_file, service_brake=1)
        if brake_controller.emergency_brake_active:
            self.write_outputs(output_file, emergency_brake=1)

    def clear_brakes(self):
        train = self.get_current_train()
        if train is None:
            return
            
        train['brake_controller'].release_brakes()
        output_file = f"TC{self.current_train_id}_outputs.json"
        self.write_outputs(output_file, emergency_brake=0, service_brake=0)
        print("Brakes Released")
        self.update_ui_from_state()

    def calculate_power(self):
        train = self.get_current_train()
        if train is None:
            return
        
        brake = train['brake_controller']
        power = train['power_controller']
        
        # Always zero power if brakes are active
        if brake.service_brake_active or brake.emergency_brake_active:
            power.P_cmd = 0
            output_file = f"TC{self.current_train_id}_outputs.json"
            self.write_outputs(output_file, power=0)
            self.p_cmd_label.setText("Commanded Power: 0 kW (Brakes Active)")
            return
            
        try:
            auto_mode = self.auto_checkbox.isChecked()
            brakes_active = (train['brake_controller'].service_brake_active or 
                            train['brake_controller'].emergency_brake_active)

            if brakes_active:
                power = 0
            else:
                if auto_mode:
                    # Use suggested speed (convert from MPH to m/s)
                    target_speed_mps = train['state'].suggested_speed_mph * self.constants.MPH_TO_MPS
                    current_speed_mps = train['state'].current_speed_mph * self.constants.MPH_TO_MPS
                else:
                    # Manual mode - get speed from input (already in MPH)
                    target_speed_mps = float(self.setpoint_input.text()) * self.constants.MPH_TO_MPS
                    current_speed_mps = train['state'].current_speed_mph * self.constants.MPH_TO_MPS
                
                power = train['power_controller'].calculate_power(
                    current_speed_mps,
                    target_speed_mps,
                    auto_mode,
                    brakes_active
                )

            # Update UI and output file
            power_kw = power / 1000
            self.p_cmd_display.setText(f"{power_kw:.2f} kW")
            self.p_cmd_label.setText(f"Commanded Power: {power_kw:.2f} kW")
            output_file = f"TC{self.current_train_id}_outputs.json"
            self.write_outputs(output_file, power=power)

        except Exception as e:
            print(f"Power calculation error: {e}")
            QMessageBox.warning(self, "Calculation Error", f"Power calculation failed: {str(e)}")

    def update_power_display(self):
        self.calculate_power()

    def update_from_files(self):
        self.scan_for_trains()
        if self.read_train_outputs():
            self.update_ui_from_state()
            
            train = self.get_current_train()
            if train is None:
                return
                    
            state = train['state']
            
            # Only check for station approach if we're moving (speed > 0.1 mph)
            if state.current_speed_mph > 0.1 and not state.station_stop_cooldown:
                try:
                    beacon = state.beacon.strip("{}")  # Remove curly braces
                    beacon_dict = {}
                    
                    # Safely parse the beacon string
                    if beacon:
                        try:
                            beacon_dict = eval(f"dict({beacon})")
                        except:
                            # Fallback for malformed beacon data
                            items = [item.strip().split(":") for item in beacon.split(",") if ":" in item]
                            beacon_dict = {k.strip().strip("'"): v.strip().strip("'") for k, v in items}
                    
                    if 'station_distance' in beacon_dict:
                        try:
                            station_distance = float(beacon_dict['station_distance'])
                            delta_position = state.delta_position

                            #print(f"DEBUG - Delta: {delta_position}, Station Dist: {station_distance}")
                            #print(f"DEBUG - Difference: {abs(delta_position - station_distance)}")

                            if (abs(delta_position - station_distance) <= 10
                                    and not state.stopping_sequence_active):
                                self.handle_station_stop()
                        except ValueError as e:
                            print(f"Error converting station distance: {e}")
                            
                except Exception as e:
                    print(f"Error checking station distance: {e}")
                    print(f"Beacon content: {state.beacon}")
                    
        self.check_speed_and_brake()
        self.update_power_display()

    def handle_station_stop(self):
        train = self.get_current_train()
        if train is None or train['state'].stopping_sequence_active:
            return
            
        state = train['state']

        train['brake_controller'].activate_service_brake()
        print("Service brake activated")
        train['brake_controller'].manual_brake = False  # Ensure auto control
        
        # Force power to 0
        train['power_controller'].P_cmd = 0
        
        # Update outputs
        output_file = f"TC{self.current_train_id}_outputs.json"
        self.write_outputs(output_file, service_brake=1, power=0)
        
        print("FORCE BRAKE ACTIVATED AND POWER ZEROED")
        
        # Start stopping sequence
        state.stopping_sequence_active = True
        if hasattr(self, 'stopping_timer'):
            self.stopping_timer.stop()
        
        self.stopping_timer = QTimer(self)
        self.stopping_timer.timeout.connect(self.check_station_stop_sequence)
        self.stopping_timer.start(100)  # Check every 100ms

    def check_station_stop_sequence(self):
        train = self.get_current_train()
        if train is None:
            if hasattr(self, 'stopping_timer'):
                self.stopping_timer.stop()
            return
            
        state = train['state']
        current_speed = state.current_speed_mph
        
        # Check if train has come to complete stop
        if current_speed <= 0.1:  # Consider stopped below 0.1 mph
            print("STOP SEQ CHECK - Train has stopped - completing sequence")
            if hasattr(self, 'stopping_timer'):
                self.stopping_timer.stop()
            self.complete_station_stop_sequence()

    def complete_station_stop_sequence(self):
        train = self.get_current_train()
        if train is None:
            return
            
        state = train['state']
        door_controller = train['door_controller']
        
        # Determine door side
        door_side = "right"  
        try:
            beacon = state.beacon.strip("{}")
            if beacon:
                beacon_dict = eval(f"dict({beacon})")
                if 'station_side' in beacon_dict:
                    door_side = beacon_dict['station_side'].lower()
        except Exception as e:
            print(f"Error parsing beacon for door side: {e}")
            
        # Open the appropriate door
        door_controller.set_door_state(door_side, True)
        output_file = f"TC{self.current_train_id}_outputs.json"
        self.write_outputs(output_file, **{f"{door_side}_door": 1})
        print(f"{door_side.capitalize()} doors opened")
        
        # Start timer for door closing (15 seconds based on timer interval)
        base_door_delay = 15000
        interval = self.read_timer_interval()
        scaled_door_delay = base_door_delay * (interval / 1000)

        door_controller.start_door_timer(
            lambda: self.finish_station_stop_sequence(door_side), int(scaled_door_delay))

    def check_speed_and_brake(self):
        if not self.auto_checkbox.isChecked():
            return
            
        train = self.get_current_train()
        if train is None:
            return
        
        if getattr(train['brake_controller'], 'manual_brake', False):
            print("manual is activated")
            return

        # Don't apply service brakes if we're in the process of leaving the station
        if getattr(train, 'leaving_station', False):
            print("Train is leaing station")
            return

        current_speed_mph = train['state'].current_speed_mph
        suggested_speed_mph = train['state'].suggested_speed_mph
        
        # Convert to m/s for power calculations if needed
        current_speed_mps = current_speed_mph * self.constants.MPH_TO_MPS
        suggested_speed_mps = suggested_speed_mph * self.constants.MPH_TO_MPS
        
        # More lenient threshold for brake activation
        speed_diff = current_speed_mps - suggested_speed_mps
        threshold = 0.5  # m/s difference threshold
        
        if speed_diff > threshold:
            if not train['brake_controller'].service_brake_active and not train['state'].stopping_sequence_active:
                print(f"Speed exceeded - activating service brake (Current: {current_speed_mph:.1f} mph, Suggested: {suggested_speed_mph:.1f} mph)")
                train['brake_controller'].activate_service_brake()
                print("Service Brake Pulled - decelerating")
                output_file = f"TC{self.current_train_id}_outputs.json"
                self.write_outputs(output_file, service_brake=1)
        elif train['brake_controller'].service_brake_active and speed_diff <= threshold and not train['state'].stopping_sequence_active:
            print(f"Speed within limits - releasing service brake (Current: {current_speed_mph:.1f} mph, Suggested: {suggested_speed_mph:.1f} mph)")
            train['brake_controller'].release_brakes()
            output_file = f"TC{self.current_train_id}_outputs.json"
            self.write_outputs(output_file, service_brake=0)

    def finish_station_stop_sequence(self, door_side):
        try:
            train = self.get_current_train()
            if train is None:
                return
                
            state = train['state']
            
            # Close doors
            train['door_controller'].set_door_state(door_side, False)
            output_file = f"TC{self.current_train_id}_outputs.json"
            self.write_outputs(output_file, **{f"{door_side}_door": 0})
            print(f"{door_side.capitalize()} doors closed")

            train['brake_controller'].release_brakes()
            self.write_outputs(output_file, service_brake = 0)
            
            # Clear stopping flag but keep cooldown for a short time
            state.stopping_sequence_active = False
            state.station_stop_cooldown = True
            state.leaving_station = True

            interval = self.read_timer_interval()

            base_cooldown = 3000
            base_leaving = 2000

            scaled_cooldown = base_cooldown * (interval / 1000)
            scaled_leaving = base_leaving * (interval / 1000)
            
            # Clear cooldown after 5 seconds (shorter than before)
            QTimer.singleShot(int(scaled_cooldown), lambda: setattr(state, 'station_stop_cooldown', False))
            
            # Clear leaving station flag after 2 seconds
            QTimer.singleShot(int(scaled_leaving), lambda: setattr(state, 'leaving_station', False))

        except Exception as e:
            print(f"Error in station stop sequence: {e}")
            train = self.get_current_train()
            if train:
                train['state'].leaving_station = False
                train['state'].stopping_sequence_active = False


def main():
    app = QApplication([])
    window = TrainControllerUI()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
