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
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.green_tab = QWidget()
        self.red_tab = QWidget()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.green_tab, "Green Line")
        self.tab_widget.addTab(self.red_tab, "Red Line")
        
        # Create content for each tab
        self.setup_green_tab()
        self.setup_red_tab()
        
        # Add tab widget to main layout
        layout.addWidget(self.tab_widget)
        
        self.setWindowTitle("Track Layout and Peripherals")
        self.setGeometry(100, 100, 800, 600)
    
    def setup_green_tab(self):
        """Setup the Green Line tab with grid and switch window"""
        layout = QVBoxLayout(self.green_tab)
        
        # Create Green Line widgets
        self.grid_window = GridWindow("data2.csv", "data1.csv", 0)  # Green Line operational and info files
        self.switch_window = SwitchWindow()  # Green Line switch window
        
        # Add them to the layout
        layout.addWidget(self.grid_window)
        layout.addWidget(self.switch_window)
    
    def setup_red_tab(self):
        """Setup the Red Line tab with grid and switch window"""
        layout = QVBoxLayout(self.red_tab)
        
        # Create Red Line widgets
        self.red_grid_window = GridWindow("data4.csv", "data3.csv", 1)  # Red Line operational and info files
        self.red_switch_window = SwitchWindow2()  # Red Line switch window
        
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
        self.operational_file = operational_file
        self.info_file = info_file
        self.line_number = line_number  # 0 for Green, 1 for Red
        self.setWindowTitle("Track Blocks")
        self.class_lines = []
        self.train_positions = []
        self.train_creations = 0
        self.ticket_array = []
        self.manual_failures = {}  # Track manual failures {block_num: failure_type}
        
        # Set the appropriate line class based on line number
        if self.line_number == 0:  # Green Line
            self.line_class = GreenLineOccupancy
            #self.beacon_blocks = GREEN_BEACON_BLOCKS  # You'll need to define these
        else:  # Red Line
            self.line_class = RedLineOccupancy
            #self.beacon_blocks = RED_BEACON_BLOCKS  # You'll need to define these
            
        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_blocks)
        self.timer.start(1000)  # Update every second

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create grid layout
        self.grid_layout = QGridLayout()
        self.boxes = {}
        
        # Load both CSV files
        grid_data = load_csv(self.operational_file)  # Operational data
        block_info_data = load_csv(self.info_file)  # Informational data
        
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
        """Create a new train instance and initialize its data"""
        try:
            print(f"Creating train {len(self.class_lines) + 1}...")
            grid_data = load_csv(self.operational_file)
            new_class_line = self.line_class(grid_data)
            
            # Initialize train data structures
            new_class_line.ticket_array = []
            new_class_line.passengers_count = 0
            new_class_line.new_passengers = 0
            
            self.class_lines.append(new_class_line)
            self.train_positions.append(0)
            print(f"New train created. Total trains: {len(self.class_lines)}")
            
        except Exception as e:
            print(f"Error creating train: {e}")

    def read_train_creation_status(self):
        """Read train instance and baud rates from PLC JSON file"""
        baud_dict = {
            'Baud1': '0', 
            'Baud2': '0',
            'Baud3': '0',
            'Baud4': '0'
        }
        train_instance = 0

        try:
            with open("PLC_OUTPUTS_Baud_Train_Instance.json", "r") as file:
                data = json.load(file)
                train_instance = data.get("Train_Instance", 0)
                
                # Extract baud values from Train_Bauds dictionary
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
        """Main update loop handling train movements, failures, and data recording"""
        try:
            # Only proceed if this grid matches the active line
            if global_variables.line != self.line_number:
                return
                
            # Read train creation status first
            self.train_creations, baud_rates = self.read_train_creation_status()
            
            previous_train_count = len(self.class_lines)
            # Create new train if needed
            if (self.train_creations == 1 and 
                (not self.class_lines or self.boxes.get(63).state == 0)):
                self.create_next_train()

            if not self.class_lines:
                return

            global_occupancy = {}
            train_statuses = []

            for train_number, class_line in enumerate(self.class_lines, start=1):
                try:
                    if train_number > len(self.train_positions):
                        print(f"Skipping train {train_number} - no position data")
                        continue

                    # Read train data
                    delta_position, station_status, passengers = self.read_train_output(train_number)
                    if None in (delta_position, station_status, passengers):
                        print(f"Error reading train {train_number} data")
                        continue

                    # Update position and get occupied blocks
                    self.train_positions[train_number - 1] = delta_position
                    occupied_blocks = class_line.find_blocks(delta_position)
                    global_occupancy.update({block: train_number for block in occupied_blocks})
                    train_statuses.append(f"Train {train_number}: {', '.join(map(str, occupied_blocks))}")

                    # Check for beacon blocks
                    beacon_info = None
                    for block in occupied_blocks:
                        # Check special conditions first
                        if block == 78 and delta_position > 7500:
                            beacon_info = beacons.get("beacon 6")
                            break
                        elif block == 15 and delta_position > 15700:
                            beacon_info = beacons.get("beacon 16")
                            break
                        elif block == 21 and delta_position > 15700:
                            beacon_info = beacons.get("beacon 17")
                            break
                        elif block in BEACON_BLOCKS:
                            beacon_info = beacons.get(BEACON_BLOCKS[block])
                            break

                    # Get current time for records
                    try:
                        current_time = global_variables.current_time.strftime("%H:%M")
                    except:
                        current_time = "--:--"

                    # Determine speed authority
                    if occupied_blocks:
                        block_num = occupied_blocks[0]
                        if 1 <= block_num <= 28:
                            speed_auth = self.train_bauds['Baud1']
                        elif 29 <= block_num <= 76:
                            speed_auth = self.train_bauds['Baud2']
                        elif 77 <= block_num <= 100:
                            speed_auth = self.train_bauds['Baud3']
                        elif 101 <= block_num <= 150:
                            speed_auth = self.train_bauds['Baud4']
                        else:
                            speed_auth = "0"  # Default if block number is out of range
                    else:
                        speed_auth = "N/A"

                    # Handle new train initialization
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
                                f"Beacon Info: {beacon_info}\n\n",
                                mode="w"
                            )
                        else:
                            append_new_train_data(
                                train_number,
                                occupied_blocks,
                                global_tickets,
                                0,  # new_passengers
                                0,  # total_passengers
                                delta_position,
                                speed_auth,
                                beacon_info
                            )

                    # Handle station arrivals
                    if station_status == 1:
                        if not hasattr(class_line, 'station_cooldown'):
                            class_line.station_cooldown = False
                        
                        if not class_line.station_cooldown:
                            print(f"Train {train_number} at station - processing passengers")
                            passengers, new_passengers, starting_pass = pass_count(passengers, station_status)
                            class_line.passengers_count = passengers
                            class_line.new_passengers = new_passengers
                            class_line.station_cooldown = True  # Set cooldown
                            
                            current_time = str(global_variables.current_time)[11:16]
                            global_tickets.append([new_passengers, current_time])

                            update_train_data(
                                train_number,
                                occupied_blocks,
                                global_tickets,
                                class_line.new_passengers,
                                class_line.passengers,
                                delta_position,
                                speed_auth,
                                beacon_info
                            )
                        
                    # Reset cooldown when leaving station
                    if station_status == 0 and hasattr(class_line, 'station_cooldown'):
                        class_line.station_cooldown = False

                    # Update train data (whether at station or not)
                    update_train_data(
                        train_number,
                        occupied_blocks,
                        global_tickets,
                        class_line.new_passengers,
                        class_line.passengers_count,
                        delta_position,
                        speed_auth,
                        beacon_info
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
                    # Failures already handled above

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

            # Update only the occupancy array
            plc_data["Occupancy"] = [1 if block_num in occupancy_dict else 0 
                                    for block_num in range(1, 151)]
            
            # Write back the complete data (with only occupancy changed)
            with open("PLC_INPUTS.json", "w") as file:
                json.dump(plc_data, file, indent=4)

        except Exception as e:
            print(f"Error updating PLC inputs: {e}")
            # Try to write minimal data if full update fails
            try:
                with open("PLC_INPUTS.json", "w") as file:
                    json.dump({
                        "Occupancy": [1 if block_num in occupancy_dict else 0 
                                    for block_num in range(1, 151)]
                    }, file)
            except Exception as e:
                print(f"Critical error writing minimal PLC inputs: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())