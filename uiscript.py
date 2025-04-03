#Philip Sherman
#Trains Group 2
#Train Controller SW UI
#2/19/2025

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QFileSystemWatcher

#################################################################################################

class PowerControl:
    def __init__(self, P_max = 120, T=0.1, Kp=1, Ki=0.2):
        self.Kp = Kp
        self.Ki = Ki
        self.P_max = P_max
        self.T = T
        self.u_k_1 = 0
        self.e_k_1 = 0
        self.P_k_1 = 0
        self.direct_power_mode = False

    def update_gains(self, Kp, Ki):
        self.Kp = Kp
        self.Ki = Ki
        self.u_k_1 = 0
        self.e_k_1 = 0
        self.P_k_1 = 0

    def set_direct_power_mode(self,enable):
        self.direct_power_mode = enable
        if enable:
            self.u_k_1 = 0
            self.e_k_1 = 0

    def compute_Pcmd(self, suggested_speed, current_speed_mps):
        if self.direct_power_mode:
            P_cmd = min(suggested_speed, self.P_max)
            self.u_k_1 = 0
            self.e_k_1 = 0

        else:
            error = suggested_speed - current_speed_mps
            u_k = self.u_k_1 + (self.T/2) * (error + self.e_k_1)
            P_cmd = self.Kp * error + self.Ki * u_k

            if P_cmd >= self.P_max:
                P_cmd = self.P_max
                u_k = self.u_k_1
            elif P_cmd <= 0:
                P_cmd = 0
                u_k = self.u_k_1

            self.u_k_1 = u_k
            self.e_k_1 = error
        
        self.P_k_1 = P_cmd
        return P_cmd

    def auto_tune_gains(self, target_velocity, current_velocity):
        error = target_velocity - current_velocity

        if current_velocity == 0 and target_velocity > 0:
            self.Kp = 1.5
            self.Ki = 0.2
        else:
            error_percent = abs(error) / self.P_max

            if error_percent < 0.1:
                self.Kp = 0.8
                self.Ki = 0.05
            elif error_percent < 0.3:
                self.Kp = 1.2
                self.Ki = 0.1
            else:
                self.Kp = 2.0
                self.Ki = 0.2

        return self.Kp, self.Ki
    
##########################################################################################3

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.MPH_TO_MPS = 0.44704
        self.MPS_TO_MPH = 2.23694
        self.KMH_TO_MPS = 0.277778
        self.MPS_TO_KMH = 3.6
        self.KMH_TO_MPH = 0.621371

        self.suggested_authority = 0
        self.suggested_speed_mps = 20 * self.MPH_TO_MPS
        self.suggested_speed_kmh = 0
        self.write_outputs(suggested_speed=20, suggested_authority=0)

        #MASTER TIMER
        self.master_timer = QTimer(self)
        self.master_timer.timeout.connect(self.update_from_files)
        self.master_timer.start(1000) # 1 second interval

        self.eb_status = 0
        self.sb_status = 0
        self.power_control = PowerControl()
        self.current_authority = 0
        self.current_speed_mps = 0
        #self.acceleration_rate = 0.5
        self.target_temp = None
        #self.service_brake_decel = 1.2
        #self.emergency_brake_decel = 2.73
        self.service_brake_active = False
        self.emergency_brake_active = False

        self.manual_eb_engaged = False

        #self.brake_timer = QTimer(self)
        #self.brake_timer.timeout.connect(self.apply_braking)

        self.train_states = {
            "Train 1": {
                "left_door": False,
                "right_door": False,
                "outside_lights": False,
                "cabin_lights": False,
                "cabin_temp": 70,
                "service_brakes": False,
                "emergency_brakes": False,
                "problem": False,
                "Kp": 0.5,
                "Ki": 0.1,
                "P_target": 80,
                "P_actual": 50
            }
        }

        self.door_timer = QTimer(self)
        self.door_timer.timeout.connect(self.close_doors_after_delay)

        self.train_states["Train 1"]["left_door"] = False
        self.train_states["Train 1"]["right_door"] = False
        self.write_outputs(left_door=0, right_door=0)

        #self.acceleration_timer = QTimer(self)
        #self.acceleration_timer.timeout.connect(self.accelerate_train)
        
        self.temp_timer = QTimer(self)
        self.temp_timer.timeout.connect(self.update_temp)

        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath('train1_outputs.txt')
        self.file_watcher.fileChanged.connect(self.update_from_files)

        self.init_ui()
        self.read_train_outputs()
        #self.acceleration_timer.start(100)

    def init_ui(self):
        self.setWindowTitle("B Team Train Control")
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("B Team Train Control")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; background-color: blue; color: white; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Train selection
        self.train_select = QComboBox()
        self.train_select.addItems(self.train_states.keys())
        self.train_select.currentIndexChanged.connect(self.train_changed)
        main_layout.addWidget(QLabel("Select Train:"))
        main_layout.addWidget(self.train_select)
        
        # Content area
        content_layout = QHBoxLayout()
        
        # Left panel - controls
        control_panel = QGroupBox("Train Controls")
        control_layout = QVBoxLayout()
        
        # Lights control
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
        
        # Door control
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
        
        # Temperature control
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
        
        # Add to control layout
        control_layout.addWidget(light_group)
        control_layout.addWidget(door_group)
        control_layout.addWidget(temp_group)
        control_panel.setLayout(control_layout)
        
        # Right panel - status and power control
        status_panel = QGroupBox("Train Status and Power Control")
        status_layout = QVBoxLayout()
        
        # Status display
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
        status_layout.addWidget(status_group)
        
        # Power control
        power_group = QGroupBox("Power Control")
        power_layout = QVBoxLayout()
        
        self.kp_input = QLineEdit("0")
        self.ki_input = QLineEdit("0")
        self.p_cmd_display = QLabel("0 kW")
        
        form_layout = QFormLayout()
        form_layout.addRow("Kp Value:", self.kp_input)
        form_layout.addRow("Ki Value:", self.ki_input)
        form_layout.addRow("Commanded Power:", self.p_cmd_display)
        
        self.set_constants_button = QPushButton("Update Power")
        
        power_layout.addLayout(form_layout)
        power_layout.addWidget(self.set_constants_button)
        power_group.setLayout(power_layout)
        status_layout.addWidget(power_group)
        
        # Brake controls
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
        status_layout.addWidget(brake_group)
        
        self.auto_checkbox = QCheckBox("Automatic Mode")
        self.auto_checkbox.setChecked(True)
        status_layout.addWidget(self.auto_checkbox)

        status_panel.setLayout(status_layout)

        # Add panels to content layout
        content_layout.addWidget(control_panel)
        content_layout.addWidget(status_panel)
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)
        
        # Connect signals
        self.ext_light_off.clicked.connect(lambda: self.set_light_state("outside_lights", False))
        self.ext_light_on.clicked.connect(lambda: self.set_light_state("outside_lights", True))
        self.cabin_light_off.clicked.connect(lambda: self.set_light_state("cabin_lights", False))
        self.cabin_light_on.clicked.connect(lambda: self.set_light_state("cabin_lights", True))
        
        self.open_left.clicked.connect(lambda: self.set_door_state("left_door", True))
        self.close_left.clicked.connect(lambda: self.set_door_state("left_door", False))
        self.open_right.clicked.connect(lambda: self.set_door_state("right_door", True))
        self.close_right.clicked.connect(lambda: self.set_door_state("right_door", False))
        
        self.temp_slider.valueChanged.connect(self.update_temp_label)
        self.set_temp_btn.clicked.connect(self.set_temp_clicked)
        
        self.sb_button.clicked.connect(self.sb_clicked)
        self.eb_button.clicked.connect(self.eb_clicked)
        self.clear_brakes_button.clicked.connect(self.clear_brakes)
        
        self.set_constants_button.clicked.connect(self.calculate_power)
        self.auto_checkbox.stateChanged.connect(self.auto_clicked)

        # Initial UI update
        self.train_changed()

        self.ext_light_on.setEnabled(False)
        self.ext_light_off.setEnabled(False)
        self.cabin_light_on.setEnabled(False)
        self.cabin_light_off.setEnabled(False)

        self.open_left.setEnabled(False)
        self.close_left.setEnabled(False)
        self.open_right.setEnabled(False)
        self.close_right.setEnabled(False)

        self.kp_input.setEnabled(False)
        self.ki_input.setEnabled(False)
        self.set_constants_button.setEnabled(False)

    def set_light_state(self, light_type, state):
        train = self.get_selected_train()
        self.train_states[train][light_type] = state
        self.update_ui_from_state()
        self.update_tb()

    def set_door_state(self, door_type, state):
        train = self.get_selected_train()
        self.train_states[train][door_type] = state
        self.update_ui_from_state()
        self.update_tb()

    def update_ui_from_state(self):
        train = self.get_selected_train()
        state = self.train_states[train]

        self.ext_light_on.setEnabled(not state["outside_lights"])
        self.ext_light_off.setEnabled(state["outside_lights"])
        self.cabin_light_on.setEnabled(not state["cabin_lights"])
        self.cabin_light_off.setEnabled(state["cabin_lights"])
        
        self.open_left.setEnabled(not state["left_door"])
        self.close_left.setEnabled(state["left_door"])
        self.open_right.setEnabled(not state["right_door"])
        self.close_right.setEnabled(state["right_door"])
        
        # Update labels
        self.left_door_label.setText(f"Left Door: {'Open' if state['left_door'] else 'Closed'}")
        self.right_door_label.setText(f"Right Door: {'Open' if state['right_door'] else 'Closed'}")
        self.cabin_lights_label.setText(f"Cabin Lights: {'On' if state['cabin_lights'] else 'Off'}")
        self.outside_lights_label.setText(f"Outside Lights: {'On' if state['outside_lights'] else 'Off'}")
        self.temperature_label.setText(f"Cabin Temp: {state['cabin_temp']} °F")
        
        # Update brake status
        self.service_brake_label.setText(f"Service Brake: {'On' if state['service_brakes'] else 'Off'}")
        self.emergency_brake_label.setText(f"Emergency Brake: {'On' if state['emergency_brakes'] else 'Off'}")
        
        # Update temperature display
        self.temperature_label.setText(f"Cabin Temp: {state['cabin_temp']} °F")
        self.current_temp_label.setText(f"Current Temp: {state['cabin_temp']} °F")
        self.temp_slider.setValue(state["cabin_temp"])

    def get_selected_train(self):
        return self.train_select.currentText()

    def train_changed(self):
        self.update_ui_from_state()

    def update_temp_label(self):
        self.target_temp_label.setText(f"Target Temp: {self.temp_slider.value()} °F")
    
    def set_temp_clicked(self):
        train = self.get_selected_train()
        self.target_temp = self.temp_slider.value()
        print(f"Target temp set to {self.target_temp} °F")

        self.temperature_label.setText(f"Cabin Temp: {self.train_states[train]['cabin_temp']} °F")

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

        self.current_temp_label.setText(f"Current Temp: {self.train_states[train]['cabin_temp']} °F")
        self.temperature_label.setText(f"Cabin Temp: {self.train_states[train]['cabin_temp']} °F")

        if self.train_states[train]["cabin_temp"] == self.target_temp:
            self.temp_timer.stop()

    def read_train_outputs(self, file_path='train1_outputs.txt'):
        try:
            with open(file_path, mode='r') as file:
                lines = file.readlines()

            data = {}
            for line in lines:
                if ':' in line:
                    parts = line.strip().split(':', 1)
                    if len(parts) == 2:
                        key, value = parts
                        data[key.strip()] = value.strip()

            
            speed_mph = float(data.get('Actual_Speed', 0))
            self.current_speed_mps = speed_mph * self.MPH_TO_MPS

            if self.current_speed_mps > self.suggested_speed_mps:
                self.current_speed_mps = self.suggested_speed_mps

            suggested_speed_auth = data.get('Suggested_Speed_Authority', '')
            if suggested_speed_auth and all(bit in '01' for bit in suggested_speed_auth):
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
                        self.suggested_speed_mps = suggested_speed_mph * self.MPH_TO_MPS
                        self.write_outputs(suggested_speed=suggested_speed_mph)
            else:
            # Default case if format is invalid
                suggested_speed_mph = 20
                self.suggested_speed_mps = suggested_speed_mph * self.MPH_TO_MPS
                self.write_outputs(suggested_speed=suggested_speed_mph)


            self.current_authority = float(data.get('Actual_Authority', 0))
            delta_position = float(data.get('Delta_Position', 0))

            beacon_str = data.get('Beacon', '{}')
            try:
                beacon_data = eval(beacon_str)
                station_distance = float(beacon_data.get('station_distance', float('inf')))

                if abs(station_distance - delta_position) <= 10:
                    self.sb_clicked()
                    print(f"Service brake activated - approaching station. Distance: {abs(station_distance - delta_position):.2f}m")
            except:
                pass

            brake_fail = data.get('Brake_Fail', '0') == '1'
            signal_fail = data.get('Signal_Fail', '0') == '1'
            engine_fail = data.get('Engine_Fail', '0') == '1'
            emergency_brake = data.get('Emergency_Brake', '0') == '1'

            if not self.manual_eb_engaged:
                new_eb_status = brake_fail or signal_fail or engine_fail or emergency_brake

                if new_eb_status != self.emergency_brake_active:
                    self.write_outputs(emergency_brake=1 if new_eb_status else 0)

                if new_eb_status:
                    self.emergency_brake_active = True
                    self.service_brake_active = False
                    #self.brake_timer.start(100)
                else:
                    self.emergency_brake_active = False

            service_brake = data.get('Service_Brake', '0') == '1'
            if service_brake and not self.emergency_brake_active:
                self.service_brake_active = True
                self.write_outputs(service_brake=1)
            
            current_speed_mph = self.current_speed_mps * self.MPS_TO_MPH
            suggested_speed_mph = self.suggested_speed_mps * self.MPS_TO_MPH

            self.suggested_authority_label.setText(f"Suggested Authority: {self.suggested_authority} m")
            self.suggested_speed_label.setText(f"Suggested Speed: {suggested_speed_mph:.1f} mph")
            self.authority_label.setText(f"Current Authority: {self.current_authority:.2f} m")
            self.speed_label.setText(f"Current Speed: {current_speed_mph:.1f} mph")
            
            self.service_brake_label.setText(f"Service Brake: {'On' if self.service_brake_active else 'Off'}")
            self.emergency_brake_label.setText(f"Emergency Brake: {'On' if self.emergency_brake_active else 'Off'}")

            return True
                
        except Exception as e:
            print(f"Error reading test bench: {e}")
            return False
        
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
            self.master_timer.start(1000)
            
            # Disable controls in automatic mode
            self.ext_light_on.setEnabled(False)
            self.ext_light_off.setEnabled(False)
            self.cabin_light_on.setEnabled(False)
            self.cabin_light_off.setEnabled(False)
            
            self.open_left.setEnabled(False)
            self.close_left.setEnabled(False)
            self.open_right.setEnabled(False)
            self.close_right.setEnabled(False)
            
            self.kp_input.setEnabled(False)
            self.ki_input.setEnabled(False)
            self.set_constants_button.setEnabled(False)
        else:
            print("Automatic Mode Disabled")
            self.master_timer.stop()
            
            # Re-enable controls in manual mode
            train = self.get_selected_train()
            state = self.train_states[train]
            
            self.ext_light_on.setEnabled(not state["outside_lights"])
            self.ext_light_off.setEnabled(state["outside_lights"])
            self.cabin_light_on.setEnabled(not state["cabin_lights"])
            self.cabin_light_off.setEnabled(state["cabin_lights"])
            
            self.open_left.setEnabled(not state["left_door"])
            self.close_left.setEnabled(state["left_door"])
            self.open_right.setEnabled(not state["right_door"])
            self.close_right.setEnabled(state["right_door"])
            
            self.kp_input.setEnabled(True)
            self.ki_input.setEnabled(True)
            self.set_constants_button.setEnabled(True)

    def sb_clicked(self):
        if not self.emergency_brake_active:
            self.service_brake_active = True
            self.emergency_brake_active = False
            self.write_outputs(service_brake=1)
            #self.acceleration_timer.stop()
            #self.brake_timer.start(100)
            print("Service Brake Engaged")
            self.open_appropriate_doors()

    def open_appropriate_doors(self):
        try:
            with open('train1_outputs.txt', mode='r') as file:
                lines = file.readlines()

            beacon_str = '{}'
            for line in lines:
                if line.startswith('Beacon:'):
                    beacon_str = line.split(':', 1)[1].strip()
                    break

            beacon_data = eval(beacon_str)
            station_side = beacon_data.get('station_side', 'right').lower()

            self.train_states["Train 1"]["left_door"] = False
            self.train_states["Train 1"]["right_door"] = False

            if station_side == 'left':
                self.train_states["Train 1"]["left_door"] = True
                self.write_outputs(left_door=1, right_door=0)
                print("Opening LEFT doors")
            else:  # default to right
                self.train_states["Train 1"]["right_door"] = True
                self.write_outputs(left_door=0, right_door=1)
                print("Opening RIGHT doors")
                
            # Update UI
            self.update_ui_from_state()
            
            # Start timer to close doors after 10 seconds
            self.door_timer.start(10000)  # 10,000 ms = 10 seconds
            
        except Exception as e:
            print(f"Error opening doors: {e}")

    def close_doors_after_delay(self):
        self.door_timer.stop()
        self.train_states["Train 1"]["left_door"] = False
        self.train_states["Train 1"]["right_door"] = False
        self.write_outputs(left_door=0, right_door=0)
        self.update_ui_from_state()
        print("Doors closed after delay")

    def write_outputs(self, power=None, emergency_brake=None, service_brake=None, 
                    suggested_speed=None, suggested_authority=None,
                    left_door=None, right_door=None):
        try:
            try:
                with open('TC_outputs.txt', 'r') as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []

            updates = {
                "Commanded Power": None if power is None else f"{power:.2f}",
                "Emergency Brake": None if emergency_brake is None else str(emergency_brake),
                "Service Brake": None if service_brake is None else str(service_brake),
                "Suggested Speed": None if suggested_speed is None else f"{suggested_speed:.1f}",
                "Suggested Authority": None if suggested_authority is None else f"{suggested_authority:.1f}",
                "Left Door": None if left_door is None else str(left_door),
                "Right Door": None if right_door is None else str(right_door)
            }

            updated = False
            found_keys = set()
            for i, line in enumerate(lines):
                if ':' in line:
                    key = line.split(':')[0].strip()
                    if key in updates and updates[key] is not None:
                        lines[i] = f"{key}: {updates[key]}\n"
                        updates[key] = None
                        updated = True

            for key in updates:
                if updates[key] is not None:
                    lines.append(f"{key}: {updates[key]}\n")
                    updated = True

            if updated:
                with open('TC_outputs.txt', 'w') as f:
                    f.writelines(lines)
        except Exception as e:
            print(f"Error writing to TC_outputs.txt: {e}")

    def apply_service_brake(self):
        if self.current_speed_mps > 0:
            self.current_speed_mps -= self.deceleration_rate * 0.1
            if self.current_speed_mps < 0:
                self.current_speed_mps = 0

            current_speed_mph = self.current_speed_mps / self.MPH_TO_MPS
            self.speed_label.setText(f"Current Speed: {self.current_speed_mph:.2f} mph")
        else:
            self.timer.stop()

    def eb_clicked(self, checked=False):
        self.emergency_brake_active = True
        self.manual_eb_engaged = True
        self.service_brake_active = False
        self.write_outputs(emergency_brake=1)
        #self.acceleration_timer.stop()
        print("Emergency Brake Engaged")            

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
        self.service_brake_active = False
        self.emergency_brake_active = False
        self.manual_eb_engaged = False
        self.write_outputs(emergency_brake=0, service_brake=0)

        #suggested_speed_mps = self.suggested_speed_kmh * self.KMH_TO_MPS
        #if self.current_speed_mps < suggested_speed_mps:
        #    self.acceleration_timer.start(100)

        print("Brakes Released")
        self.service_brake_label.setText("Service Brake: Off")
        self.emergency_brake_label.setText("Emergency Brake: Off")


    def calculate_power(self):
        try:
            train = self.get_selected_train()

            if self.auto_checkbox.isChecked():
                self.power_control.set_direct_power_mode(False)
                Kp, Ki = self.power_control.auto_tune_gains(self.suggested_speed_mps, self.current_speed_mps)

                self.kp_input.setText(f"{Kp:.2f}")
                self.ki_input.setText(f"{Ki:.2f}")
            else:
                self.power_control.set_direct_power_mode(True)
                Kp = float(self.kp_input.text())
                Ki = float(self.ki_input.text())

            self.power_control.update_gains(Kp, Ki)
            P_cmd = self.power_control.compute_Pcmd(self.suggested_speed_mps, self.current_speed_mps)

            self.p_cmd_display.setText(f"{P_cmd:.2f} kW")
            self.p_cmd_label.setText(f"Commanded Power: {P_cmd:.2f} kW")

            self.write_outputs(power=P_cmd)

            self.train_states[train]["Kp"] = Kp
            self.train_states[train]["Ki"] = Ki

            print(f"Commanded Power: {P_cmd:.2f} kW")

        except ValueError:
            print("Please enter valid numerical values for Kp and Ki")

    #def accelerate_train(self):
    #    if not (self.service_brake_active or self.emergency_brake_active):
    #        suggested_speed_mps = self.suggested_speed_kmh * self.KMH_TO_MPS #Convert km/h to mps

    #        if self.current_speed_mps < suggested_speed_mps:
    #            #self.current_speed_mps += self.acceleration_rate * 0.1
    #            self.current_speed_mps = min(self.current_speed_mps, suggested_speed_mps)

    #            current_speed_mph = self.current_speed_mps * self.MPS_TO_MPH
    #            self.speed_label.setText(f"Current Speed: {current_speed_mph:.1f} mph")

    #            self.update_power_display()
    #        else:
    #            self.acceleration_timer.stop()

    def update_power_display(self):
        P_cmd = self.power_control.compute_Pcmd(
            self.suggested_speed_mps,
            self.current_speed_mps
        )
        self.p_cmd_label.setText(f"Commanded Power: {P_cmd:.2f} kW")
        self.write_outputs(power=P_cmd)

    def update_from_files(self):
        self.read_train_outputs()
        self.update_power_display()

        if self.current_speed_mps > self.suggested_speed_mps:
            self.current_speed_mps = self.suggested_speed_mps
            current_speed_mph = self.current_speed_mps * self.MPS_TO_MPH
            self.speed_label.setText(f"Current Speed: {current_speed_mph:.1f} mph")

        #suggested_speed_mps = self.suggested_speed_kmh * self.KMH_TO_MPS

        #if (self.current_speed_mps < suggested_speed_mps and
        #    not self.service_brake_active and
        #    not self.emergency_brake_active):
        #    if not self.acceleration_timer.isActive():
        #        self.acceleration_timer.start(100)
        #else:
        #    self.acceleration_timer.stop()

    #def write_outputs(self, power=None, emergency_brake=None, service_brake=None, suggested_speed=None, suggested_authority=None):
    #    try:
    #        try:
    #            with open('TC_outputs.txt', 'r') as f:
    #               lines = f.readlines()
    #        except FileNotFoundError:
    #            lines = []

    #        updates = {
    #            "Commanded Power": None if power is None else f"{power:.2f}",
    #            "Emergency Brake": None if emergency_brake is None else str(emergency_brake),
    #            "Service Brake": None if service_brake is None else str(service_brake),
    #            "Suggested Speed": None if suggested_speed is None else f"{suggested_speed * self.KMH_TO_MPH:.1f}",
    #            "Suggested Authority": None if suggested_authority is None else f"{suggested_authority:.1f}"
    #        }

     #       updated = False
      #      found_keys = set()
     #       for i, line in enumerate(lines):
     #         if ':' in line:
    #                key = line.split(':')[0].strip()
      #              if key in updates and updates[key] is not None:
       #                 lines[i] = f"{key}: {updates[key]}\n"
        #                updates[key] = None
         #               updated = True
#
 #           for key in updates:
  #              if updates[key] is not None:
   #                 lines.append(f"{key}: {updates[key]}\n")
    #                updated = True
#
 #           if updated:
  #              with open('TC_outputs.txt', 'w') as f:
   #                 f.writelines(lines)
    #    except Exception as e:
     #       print(f"Error writing to TC_outputs.txt: {e}")


    
#######################################################################

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
