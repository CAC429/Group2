from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout, QPushButton, 
                            QMessageBox, QVBoxLayout, QLabel, QHBoxLayout, 
                            QLineEdit, QComboBox, QTabWidget)
from PyQt5.QtCore import QTimer
from greenlineoccup import GreenLineOccupancy, load_csv, write_to_file, append_new_train_data, update_train_data, pass_count, BEACON_BLOCKS
from redlineoccup import RedLineOccupancy, load_csv, write_to_file, append_new_train_data, update_train_data, pass_count, BEACON_BLOCKS
import global_variables
from switch_window import SwitchWindow
from switch_window2 import SwitchWindow2  # New Red Line switch window
from beacons import beacons
import sys
import json

global_tickets = []
# Format: {block_num: failure_type}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.clear_occupancy_data()
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs with their respective CSV files
        self.green_tab = QWidget()
        self.red_tab = QWidget()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.green_tab, "Green Line")
        self.tab_widget.addTab(self.red_tab, "Red Line")
        
        # Create content for each tab with correct CSV files
        self.setup_green_tab()
        self.setup_red_tab()
        
        # Add tab widget to main layout
        layout.addWidget(self.tab_widget)
        
        self.setWindowTitle("Track Layout and Peripherals")
        self.setGeometry(100, 100, 800, 600)

    def clear_occupancy_data(self):
        """Clear the occupancy data file when UI starts"""
        try:
            with open("occupancy_data.json", "w") as file:
                json.dump({"trains": []}, file, indent=4)
            print("Cleared occupancy data at startup")
        except Exception as e:
            print(f"Error clearing occupancy data: {e}")

    def setup_green_tab(self):
        """Setup the Green Line tab with grid and switch window"""
        layout = QHBoxLayout(self.green_tab)
        
        # Create Green Line widgets with Green Line CSV files
        self.grid_window = GridWindow("data2.csv", "data1.csv", 0)  # Pass line_number=0 for Green Line
        self.switch_window = SwitchWindow()
        
        # Add them to the layout
        layout.addWidget(self.grid_window)
        layout.addWidget(self.switch_window)
    
    def setup_red_tab(self):
        """Setup the Red Line tab with grid and switch window"""
        layout = QHBoxLayout(self.red_tab)
        
        # Create Red Line widgets with Red Line CSV files
        self.red_grid_window = GridWindow("data4.csv", "data3.csv", 1)  # Pass line_number=1 for Red Line
        self.red_switch_window = SwitchWindow2()
        
        # Add them to the layout
        layout.addWidget(self.red_grid_window)
        layout.addWidget(self.red_switch_window)

class ClickableBox(QPushButton):
    def __init__(self, index, grid_data, block_info_data):
        super().__init__()
        self.index = index
        self.grid_data = grid_data  # From operational data CSV
        self.block_info = block_info_data  # From display info CSV
        self.state = 0  # 0 for vacant, 1 for occupied
        self.occupying_train = None
        self.failure_type = None
        self.setFixedSize(40, 40)

        label = grid_data.get("Block Number", str(index))
        self.setText(f"{grid_data.get('Section')} {label}")

        self.update_color()
        self.clicked.connect(self.show_info)

    def update_color(self):
        """Update block color based on occupancy state."""
        color = "green" if self.state == 1 else "white"
        self.setStyleSheet(
            f"""
            background-color: {color}; 
            border: 1px solid black; 
            font-weight: bold;
            font-size: 10px;
            font-family: Arial;
            color: Black;
            """
        )
        self.setText(f"{self.grid_data.get('Section')}{self.index}")

    def show_info(self):
        """Display comprehensive block info from both CSVs, skipping length and speed limit."""
        info_text = f"Block {self.index}\n"
        info_text += f"State: {'Occupied' if self.state else 'Vacant'}\n"
        
        if self.failure_type:
            info_text += f"Failure: {self.failure_type}\n"
        if self.occupying_train:
            info_text += f"Occupied by: {self.occupying_train}\n"
        
        # Add additional block info if available
        if self.block_info:
            info_text += "\nBlock Information:\n"
            for key, value in self.block_info.items():
                # Skip these specific columns and block number
                if key not in ["Block Number", "Block Length (m)", "Speed Limit (Km/Hr)", "c"]:
                    info_text += f"{key}: {value}\n"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Block Details")
        msg_box.setText(info_text)
        msg_box.exec_()

    def set_state(self, new_state, train_id=None, failure_type=None):
        """Set the state of the block and update the color."""
        self.state = new_state
        self.occupying_train = train_id
        self.failure_type = failure_type
        self.update_color()

class GridWindow(QWidget):
    def __init__(self, operational_file, info_file, line_number):
        super().__init__()
        self.initialoperational_file = operational_file  # For initial UI setup
        self.initialinfo_file = info_file  # For initial UI setup
        self.line_number = line_number  # 0 for Green, 1 for Red
        self.setWindowTitle("Track Blocks")
        
        # Set operational files based on line number
        if self.line_number == 0:  # Green Line
            self.line_class = GreenLineOccupancy
            self.operational_file = "data2.csv"
            self.info_file = "data1.csv"
        elif self.line_number == 1:  # Red Line
            self.line_class = RedLineOccupancy
            self.operational_file = "data4.csv"
            self.info_file = "data3.csv"
            
        self.class_lines = []
        self.train_positions = []
        self.train_creations = 0
        self.ticket_array = []
        self.manual_failures = {}
        self.position = 0
        
        self.init_ui()
        try:
            with open("TIMER.json", "r") as file:
                inputs = json.load(file)
            time = inputs.get("timer_interval")
        except FileNotFoundError:
            print("error")
            time = 1000
        except Exception as e:
            print("unexpected: {e}")
            time = 1000
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_blocks)
        self.timer.start(time)
        

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create grid layout
        self.grid_layout = QGridLayout()
        self.boxes = {}
        
        # Load both CSV files
        grid_data = load_csv(self.initialoperational_file)  # Operational data
        block_info_data = load_csv(self.initialinfo_file)  # Informational data
        
        # Create mapping of block numbers to their info with validation
        block_info_map = {}
        for row in block_info_data:
            try:
                block_num = row.get("Block Number", "").strip()
                if block_num:  # Only process if block number exists
                    block_info_map[int(block_num)] = row
            except (ValueError, AttributeError):
                continue  # Skip rows with invalid block numbers
        
        # Initialize first train position
        self.train_positions.append(0)
        
        # Create all blocks with validation
        for index, row_data in enumerate(grid_data):
            try:
                block_num_str = row_data.get("Block Number", "").strip()
                if not block_num_str:  # Skip if no block number
                    continue
                    
                block_num = int(block_num_str)
                
                # Get corresponding block info if available
                block_info = block_info_map.get(block_num, {})
                
                box = ClickableBox(block_num, row_data, block_info)
                self.boxes[block_num] = box
                row, col = divmod(index, 15)
                self.grid_layout.addWidget(box, row, col)
                
            except (ValueError, AttributeError):
                continue  # Skip invalid block numbers
        
        # Add grid to main layout
        grid_widget = QWidget()
        grid_widget.setLayout(self.grid_layout)
        main_layout.addWidget(grid_widget)
        
        # Create control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # Block number input
        self.block_input = QLineEdit()
        self.block_input.setPlaceholderText("Block Number")
        self.block_input.setFixedWidth(100)
        control_layout.addWidget(QLabel("Block:"))
        control_layout.addWidget(self.block_input)
        
        # Failure type dropdown
        self.failure_type_combo = QComboBox()
        self.failure_type_combo.addItems(["Broken Rail", "Track Circuit Failure", "Power Failure"])
        control_layout.addWidget(QLabel("Failure Type:"))
        control_layout.addWidget(self.failure_type_combo)
        
        # Set Failure button
        set_failure_btn = QPushButton("Set/Clear Failure")
        set_failure_btn.clicked.connect(self.toggle_block_failure)
        control_layout.addWidget(set_failure_btn)
        
        # Add stretch to push everything left
        control_layout.addStretch()
        
        main_layout.addWidget(control_panel)

    def toggle_block_failure(self):
        """Toggle failure state for the specified block"""
        try:
            block_num = int(self.block_input.text())
            if block_num not in self.boxes:
                QMessageBox.warning(self, "Invalid Block", "Please enter a valid block number")
                return
            
            failure_type = self.failure_type_combo.currentText()
            box = self.boxes[block_num]
            
            if block_num in self.manual_failures:
                # Clear failure
                box.set_state(0, failure_type=None)
                del self.manual_failures[block_num]
                global_variables.global_failures.pop(block_num, None)  # Remove from global failures
                print(f"Cleared failure from block {block_num}")
            else:
                # Set failure
                box.set_state(1, failure_type=failure_type)
                self.manual_failures[block_num] = failure_type
                global_variables.global_failures[block_num] = failure_type  # Add to global failures
                print(f"Set {failure_type} on block {block_num}")
                
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid block number")
            
    def show_switch_window(self):
        """Show the switch positions window"""
        if self.switch_window is None:
            self.switch_window = SwitchWindow()
        self.switch_window.show()

    def create_next_train(self):
        """Create a new train instance using the correct CSV files"""
        try:
            print(f"Creating train {len(self.class_lines) + 1}...")
            print(f"Using operational file: {self.operational_file}")
            
            # Use the correct operational file based on line number
            grid_data = load_csv(self.operational_file)
            new_class_line = self.line_class(grid_data)
            
            # Initialize train data structures
            new_class_line.ticket_array = []
            new_class_line.passengers_count = 0
            new_class_line.new_passengers = 0
            new_class_line.current_beacon_info = None  # Initialize beacon info
            
            self.class_lines.append(new_class_line)
            self.train_positions.append(0)
            print(f"New train created. Total trains: {len(self.class_lines)}")
            
        except Exception as e:
            print(f"Error creating train: {e}")

    def init_train_instance_file(self):
        """Initialize the train_instance.json file if it doesn't exist"""
        try:
            with open("train_instance.json", "w") as file:
                json.dump({"train_instance": 0}, file)
        except Exception as e:
            print(f"Error initializing train_instance.json: {e}")

    def update_train_instance_file(self, instance_status):
        """Update the train_instance.json file with new status"""
        try:
            with open("train_instance.json", "w") as file:
                json.dump({"train_instance": instance_status}, file)
        except Exception as e:
            print(f"Error updating train_instance.json: {e}")

    def read_train_creation_status(self):
        """Read train instance and baud rates from PLC JSON file"""
        train_instance = 0
        if global_variables.line == 0:
            baud_dict = {
                'Baud1': '0', 
                'Baud2': '0',
                'Baud3': '0',
                'Baud4': '0'
            }
            try:
                with open("PLC_OUTPUTS_Baud_Train_Instance.json", "r") as file:
                    data = json.load(file)
                    train_instance = data.get("Train_Instance", 0)
                    
                    if train_instance == 1:
                        self.update_train_instance_file(1)
                    else:
                        self.update_train_instance_file(0)
                    
                    train_bauds = data.get("Train_Bauds", {})
                    for key, value in train_bauds.items():
                        if 'Baud1' in key:
                            baud_dict['Baud1'] = value
                        elif 'Baud2' in key:
                            baud_dict['Baud2'] = value
                        elif 'Baud3' in key:
                            baud_dict['Baud3'] = value
                        elif 'Baud4' in key:
                            baud_dict['Baud4'] = value

            except Exception as e:
                print(f"Error reading PLC outputs: {e}")
        
        elif global_variables.line == 1:
            baud_dict = {
                'Baud1': '0', 
                'Baud2': '0',
                'Baud3': '0',
                'Baud4': '0',
                'Baud5': '0', 
                'Baud6': '0',
                'Baud7': '0',
                'Baud8': '0'
            }
            try:
                with open("PLC_OUTPUTS_Baud_Train_Instance2.json", "r") as file:
                    data = json.load(file)
                    train_instance = data.get("Train_Instance", 0)
                    
                    if train_instance == 1:
                        self.update_train_instance_file(1)
                    else:
                        self.update_train_instance_file(0)
                    
                    train_bauds = data.get("Train_Bauds", {})
                    for key, value in train_bauds.items():
                        if 'Baud1' in key:
                            baud_dict['Baud1'] = value
                        elif 'Baud2' in key:
                            baud_dict['Baud2'] = value
                        elif 'Baud3' in key:
                            baud_dict['Baud3'] = value
                        elif 'Baud4' in key:
                            baud_dict['Baud4'] = value
                        elif 'Baud5' in key:
                            baud_dict['Baud5'] = value
                        elif 'Baud6' in key:
                            baud_dict['Baud6'] = value
                        elif 'Baud7' in key:
                            baud_dict['Baud7'] = value
                        elif 'Baud8' in key:
                            baud_dict['Baud8'] = value

            except Exception as e:
                print(f"Error reading PLC outputs: {e}")
        
        self.train_creations = train_instance
        self.train_bauds = baud_dict
        return train_instance, baud_dict

    def read_train_output(self, train_number):
        """Read train position and status from its JSON output file"""
        try:
            file_path = f"train{train_number}_outputs.json"
            with open(file_path, "r") as file:
                data = json.load(file)
                return (
                    data.get("Delta_Position"),
                    data.get("Station_Status"),
                    data.get("Passengers")
                )
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Train {train_number} outputs JSON file not found or invalid")
        except Exception as e:
            print(f"Error reading train {train_number} outputs: {e}")
        return None, None, None

    def update_blocks(self):
        try:
            if global_variables.line != self.line_number:
                return
                
            self.train_creations, baud_rates = self.read_train_creation_status()
            
            previous_train_count = len(self.class_lines)
            if (self.train_creations == 1 and 
                (not self.class_lines or self.boxes.get(63).state == 0) and (global_variables.line == 0)):
                self.create_next_train()
            elif (self.train_creations == 1 and 
                (not self.class_lines or self.boxes.get(9).state == 0) and (global_variables.line == 1)):
                self.create_next_train()
            if not self.class_lines:
                return

            global_occupancy = {}
            train_statuses = []

            for train_number, class_line in enumerate(self.class_lines, start=1):
                try:
                    delta_position, station_status, passengers = self.read_train_output(train_number)
                    if None in (delta_position, station_status, passengers):
                        continue
                    
                    self.train_positions[train_number - 1] = delta_position
                    occupied_blocks, elevation = class_line.find_blocks(delta_position)
                    global_occupancy.update({block: train_number for block in occupied_blocks})

                    # Initialize beacon_info with previous value if it exists
                    if not hasattr(class_line, 'current_beacon_info'):
                        class_line.current_beacon_info = None
                        
                    # Check for beacon blocks
                    new_beacon_info = None
                    if global_variables.line == 0:
                        for block in occupied_blocks:
                            if block == 78 and delta_position > 7500:
                                new_beacon_info = beacons.get("beacon 6")
                                break
                            elif block == 15 and delta_position > 15700:
                                new_beacon_info = beacons.get("beacon 16")
                                break
                            elif block == 21 and delta_position > 15700:
                                new_beacon_info = beacons.get("beacon 17")
                                break
                            elif block in BEACON_BLOCKS:
                                new_beacon_info = beacons.get(BEACON_BLOCKS[block])
                                break
                    elif global_variables.line == 1:
                        for block in occupied_blocks:
                            if block == 49 and delta_position > 4600:
                                new_beacon_info = beacons.get("beacon 9")
                                break
                            elif block == 46 and delta_position > 4600:
                                new_beacon_info = beacons.get("beacon 10")
                                break
                            elif block == 36 and delta_position > 4600:
                                new_beacon_info = beacons.get("beacon 11")
                                break
                            elif block == 26 and delta_position > 4600:
                                new_beacon_info = beacons.get("beacon 12")
                                break
                            elif block == 22 and delta_position > 4600:
                                new_beacon_info = beacons.get("beacon 13")
                                break
                            elif block == 17 and delta_position > 4600:
                                new_beacon_info = beacons.get("beacon 14")
                                break
                            elif block in BEACON_BLOCKS:
                                new_beacon_info = beacons.get(BEACON_BLOCKS[block])
                                break

                    # Only update beacon info if we hit a new beacon
                    if new_beacon_info is not None:
                        class_line.current_beacon_info = new_beacon_info

                    # Get current time for records
                    try:
                        current_time = global_variables.current_time.strftime("%H:%M")
                    except:
                        current_time = "--:--"

                    # Determine speed authority
                    if occupied_blocks and global_variables.line == 0:
                        block_num = occupied_blocks[0]
                        if 1 <= block_num <= 28:
                            speed_auth = self.train_bauds['Baud1']
                        elif 29 <= block_num <= 76:
                            speed_auth = self.train_bauds['Baud2']
                        elif 77 <= block_num <= 100:
                            speed_auth = self.train_bauds['Baud3']
                        elif 101 <= block_num <= 150:
                            speed_auth = self.train_bauds['Baud4']
                    elif occupied_blocks and global_variables.line == 1:
                        block_num = occupied_blocks[0]
                        if 1 <= block_num <= 27:
                            speed_auth = self.train_bauds['Baud1']
                        elif 72 <= block_num <= 76:
                            speed_auth = self.train_bauds['Baud2']
                        elif 28 <= block_num <= 33:
                            speed_auth = self.train_bauds['Baud3']
                        elif 34 <= block_num <= 38:
                            speed_auth = self.train_bauds['Baud4']
                        elif 67 <= block_num <= 71:
                            speed_auth = self.train_bauds['Baud5']
                        elif 39 <= block_num <= 44:
                            speed_auth = self.train_bauds['Baud6']
                        elif 45 <= block_num <= 52:
                            speed_auth = self.train_bauds['Baud7']
                        elif 53 <= block_num <= 66:
                            speed_auth = self.train_bauds['Baud8']
                    else:
                        speed_auth = "N/A"

                    new_train_created = (train_number > previous_train_count)
                    if new_train_created:
                        if train_number == 1:
                            write_to_file(
                                f"Train {train_number}:\n"
                                f"Position: {delta_position}m\n"
                                f"Occupied Blocks: {occupied_blocks}\n"
                                f"Suggested_Speed_Authority: {speed_auth}\n"
                                f"Passengers: 0\n"
                                f"Ticket Sales: []\n"
                                f"Beacon Info: {class_line.current_beacon_info}\n"
                                f"Elevation: {elevation}m\n\n",
                                mode="w"
                            )
                        else:
                            append_new_train_data(
                                train_number,
                                occupied_blocks,
                                global_tickets,
                                0,
                                0,
                                delta_position,
                                speed_auth,
                                class_line.current_beacon_info,
                                elevation
                            )

                    if station_status == 1:
                        if not hasattr(class_line, 'station_cooldown'):
                            class_line.station_cooldown = False
                        
                        if not class_line.station_cooldown:
                            passengers, new_passengers, starting_pass = pass_count(passengers, station_status)
                            class_line.passengers_count = passengers
                            class_line.new_passengers = new_passengers
                            class_line.station_cooldown = True
                            
                            current_time = str(global_variables.current_time)[11:16]
                            global_tickets.append([new_passengers, current_time])

                            update_train_data(
                                train_number,
                                occupied_blocks,
                                global_tickets,
                                class_line.new_passengers,
                                class_line.passengers_count,
                                delta_position,
                                speed_auth,
                                class_line.current_beacon_info,
                                elevation
                            )
                        
                    if station_status == 0 and hasattr(class_line, 'station_cooldown'):
                        class_line.station_cooldown = False

                    update_train_data(
                        train_number,
                        occupied_blocks,
                        global_tickets,
                        class_line.new_passengers,
                        class_line.passengers_count,
                        delta_position,
                        speed_auth,
                        class_line.current_beacon_info,
                        elevation
                    )

                except Exception as e:
                    print(f"Error processing train {train_number}: {e}")
                    continue

            # Apply manual failures (override train occupancy)
            for block_num, failure_type in self.manual_failures.items():
                if block_num in self.boxes:
                    self.boxes[block_num].set_state(1, train_id=f"Failure: {failure_type}")
                    global_occupancy[block_num] = f"Failure: {failure_type}"

            # Update all block states
            for box in self.boxes.values():
                if box.index not in global_occupancy and box.index not in self.manual_failures:
                    box.set_state(0)
                elif box.index in global_occupancy:
                    if isinstance(global_occupancy[box.index], int):  # Regular train
                        box.set_state(1, train_id=global_occupancy[box.index])

            self.update_plc_inputs(global_occupancy)
            
        except Exception as e:
            print(f"Error in update_blocks: {e}")

    def update_plc_inputs(self, occupancy_dict):
        """Update only the occupancy array in PLC_INPUTS.json while preserving all other data"""
        try:
            # First load the existing PLC inputs data
            try:
                with open("PLC_INPUTS.json", "r") as file:
                    plc_data = json.load(file)
            except FileNotFoundError:
                # If file doesn't exist, create a new one with default structure
                plc_data = {
                    "Suggested_Speed": [20]*150,
                    "Suggested_Authority": [100]*150,
                    "Occupancy": [0]*150,
                    "Default_Switch_Position": [0]*6,
                    "Train_Instance": 0
                }
            except json.JSONDecodeError:
                print("Error: PLC_INPUTS.json contains invalid JSON, creating new file")
                plc_data = {
                    "Suggested_Speed": [20]*150,
                    "Suggested_Authority": [100]*150,
                    "Occupancy": [0]*150,
                    "Default_Switch_Position": [0]*6,
                    "train_instance": 0
                }
            
            # Set the correct number of blocks based on line
            if global_variables.line == 1:
                x = 76  # Red Line has 75 blocks
            else:
                x = 151  # Green Line has 150 blocks
                
            # Update only the occupancy array
            plc_data["Occupancy"] = [1 if block_num in occupancy_dict else 0 
                                    for block_num in range(1, x)]
            
            # Write back the complete data
            with open("PLC_INPUTS.json", "w") as file:
                json.dump(plc_data, file, indent=4)

        except Exception as e:
            print(f"Error updating PLC inputs: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())