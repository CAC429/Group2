from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QFileSystemWatcher
import csv

class PowerControl:
    def __init__(self, P_max=100):
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
        self.integral = max(min(self.integral + error, self.P_max), -self.P_max)
        P_cmd = self.P_k_1 + (self.Kp * error) + (self.Ki * self.integral)
        P_cmd = min(P_cmd, self.P_max)
        self.P_k_1 = P_cmd
        return P_cmd

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.eb_status = 0
        self.sb_status = 0
        self.power_control = PowerControl()
        self.current_authority = 0
        self.current_speed = 0
        self.suggested_authority = 0
        self.suggested_speed = 0
        self.acceleration_rate = 0.5
        self.max_speed = 70
        
        # Initialize train states with all possible keys
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
        
        # Set up timers
        self.acceleration_timer = QTimer(self)
        self.acceleration_timer.timeout.connect(self.accelerate_train)
        self.acceleration_timer.start(100)
        
        self.temp_timer = QTimer(self)
        self.temp_timer.timeout.connect(self.update_temp)
        self.target_temp = None
        
        # File watcher for automatic updates
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath('TestBench_SW.csv')
        self.file_watcher.fileChanged.connect(self.handle_file_changed)
        
        self.init_ui()
        self.read_tb()  # Initial read of test bench
        
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
        
        self.authority_label = QLabel("Authority: 0 m")
        self.speed_label = QLabel("Current Speed: 0 mph")
        self.service_brake_label = QLabel("Service Brake: Off")
        self.emergency_brake_label = QLabel("Emergency Brake: Off")
        self.left_door_label = QLabel("Left Door: Closed")
        self.right_door_label = QLabel("Right Door: Closed")
        self.cabin_lights_label = QLabel("Cabin Lights: Off")
        self.outside_lights_label = QLabel("Outside Lights: Off")
        self.temperature_label = QLabel("Cabin Temp: -- °F")
        
        status_display_layout.addWidget(self.authority_label)
        status_display_layout.addWidget(self.speed_label)
        status_display_layout.addWidget(self.service_brake_label)
        status_display_layout.addWidget(self.emergency_brake_label)
        status_display_layout.addWidget(self.left_door_label)
        status_display_layout.addWidget(self.right_door_label)
        status_display_layout.addWidget(self.cabin_lights_label)
        status_display_layout.addWidget(self.outside_lights_label)
        status_display_layout.addWidget(self.temperature_label)
        
        status_group.setLayout(status_display_layout)
        status_layout.addWidget(status_group)
        
        # Power control
        power_group = QGroupBox("Power Control")
        power_layout = QVBoxLayout()
        
        self.kp_input = QLineEdit("0.5")
        self.ki_input = QLineEdit("0.1")
        self.p_target_input = QLineEdit("80")
        self.p_actual_input = QLineEdit("50")
        self.p_cmd_display = QLabel("0")
        
        form_layout = QFormLayout()
        form_layout.addRow("Kp Value:", self.kp_input)
        form_layout.addRow("Ki Value:", self.ki_input)
        form_layout.addRow("Target Power:", self.p_target_input)
        form_layout.addRow("Actual Power:", self.p_actual_input)
        form_layout.addRow("Commanded Power:", self.p_cmd_display)
        
        self.set_constants_button = QPushButton("Calculate Power")
        
        power_layout.addLayout(form_layout)
        power_layout.addWidget(self.set_constants_button)
        power_group.setLayout(power_layout)
        status_layout.addWidget(power_group)
        
        # Brake controls
        brake_group = QGroupBox("Brake Controls")
        brake_layout = QHBoxLayout()
        
        self.sb_button = QPushButton("Service Brake")
        self.eb_button = QPushButton("Emergency Brake")
        self.clear_brakes_button = QPushButton("Release Brakes")
        
        brake_layout.addWidget(self.sb_button)
        brake_layout.addWidget(self.eb_button)
        brake_layout.addWidget(self.clear_brakes_button)
        brake_group.setLayout(brake_layout)
        status_layout.addWidget(brake_group)
        
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
        
        # Initial UI update
        self.train_changed()
    
    def handle_file_changed(self, path):
        """Handle changes to the test bench file"""
        print(f"Detected change in {path}, reloading...")
        self.read_tb()
    
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
        """Update all UI elements based on current train state"""
        train = self.get_selected_train()
        state = self.train_states[train]
        
        # Update button states
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
    
    # ... (keep your existing methods but ensure they use update_ui_from_state)
    
    def read_tb(self, file_path='TestBench_SW.csv'):
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)
                data = {row[0]: row[1] for row in csv_reader if len(row) >= 2}
            
            train = "Train 1"
            
            # Update train states from CSV data
            self.train_states[train]["left_door"] = data.get('Left_door', 'off') == 'on'
            self.train_states[train]["right_door"] = data.get('Right_door', 'off') == 'on'
            self.train_states[train]["outside_lights"] = data.get('Outside_lights', 'off') == 'on'
            self.train_states[train]["cabin_lights"] = data.get('Cabin_lights', 'off') == 'on'
            self.train_states[train]["cabin_temp"] = int(data.get('Cabin_temp', 22))
            self.train_states[train]["service_brakes"] = data.get('Service_brakes', 'off') == 'on'
            self.train_states[train]["emergency_brakes"] = data.get('Emergency_brakes', 'off') == 'on'
            self.train_states[train]["Kp"] = float(data.get('Kp', 0.5))
            self.train_states[train]["Ki"] = float(data.get('Ki', 0.1))
            self.train_states[train]["P_target"] = float(data.get('P_target', 80))
            self.train_states[train]["P_actual"] = float(data.get('P_actual', 50))
            
            # Update power control
            self.power_control.update_gains(
                self.train_states[train]["Kp"],
                self.train_states[train]["Ki"]
            )
            
            # Update UI
            self.update_ui_from_state()
            
            # Update power control fields
            self.kp_input.setText(str(self.train_states[train]["Kp"]))
            self.ki_input.setText(str(self.train_states[train]["Ki"]))
            self.p_target_input.setText(str(self.train_states[train]["P_target"]))
            self.p_actual_input.setText(str(self.train_states[train]["P_actual"]))
            
            # Calculate and display commanded power
            P_cmd = self.power_control.compute_Pcmd(
                self.train_states[train]["P_target"],
                self.train_states[train]["P_actual"]
            )
            self.p_cmd_display.setText(f"{P_cmd:.2f}")
            
            return True
            
        except Exception as e:
            print(f"Error reading test bench: {e}")
            return False

    # ... (keep your other existing methods)

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()