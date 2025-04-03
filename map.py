import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QMessageBox, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from greenlineoccup import GreenLineOccupancy, load_csv, write_to_file, append_new_train_data, update_train_data, pass_count
import global_variables  # Ensure this module contains a `current_time` attribute

class ClickableBox(QPushButton):
    def __init__(self, index, row_data):
        super().__init__()
        self.index = index
        self.row_data = row_data
        self.state = 0  # 0 for vacant, 1 for occupied
        self.occupying_train = None
        self.setFixedSize(70, 70)

        label = row_data.get("Block Number", str(index))
        self.setText(f"{row_data.get('Section')} {label}")

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
            font-size: 20px;
            font-family: Arial;
            color: Black;
            """
        )
        self.setText(f"{self.row_data.get('Section')}{self.index}")

    def show_info(self):
        """Display block info in a message box."""
        columns_to_skip = ["route 1", "route 2"]

        filtered_row_data = {key: value for key, value in self.row_data.items() if key not in columns_to_skip}
        info_text = f"Box {self.index}\nState: {'Occupied' if self.state else 'Vacant'}\n\n"
        info_text += "\n".join([f"{key}: {value}" for key, value in filtered_row_data.items()])

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Box Info")
        msg_box.setText(info_text)
        msg_box.setStyleSheet("background-color: white;")
        msg_box.exec_()

    def set_state(self, new_state, train_id=None):
        """Set the state of the block and update the color."""
        self.state = new_state
        self.occupying_train = train_id
        self.update_color()

class GridWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Green Line Blocks")
        self.layout = QGridLayout()
        self.boxes = {}
        self.green_lines = []
        self.train_positions = []
        self.train_creations = 0  # Initialize train creation flag
        self.ticket_array = []  # Persistent ticket sales list

        # Load the grid data
        grid_data = load_csv("data2.csv")

        # Create blocks
        self.train_positions.append(0)
        for index, row_data in enumerate(grid_data):
            block_num = int(row_data.get("Block Number", -1))
            if block_num == -1:
                continue
            box = ClickableBox(block_num, row_data)
            self.boxes[block_num] = box
            row, col = divmod(index, 15)
            self.layout.addWidget(box, row, col)

        # Train list UI
        self.train_list_label = QLabel("Train Occupancy List:")
        self.train_list_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.train_list_layout = QVBoxLayout()
        self.train_list_layout.addWidget(self.train_list_label)
        self.train_list_display = QLabel("No trains are active.")
        self.train_list_layout.addWidget(self.train_list_display)
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.layout)
        self.main_layout.addLayout(self.train_list_layout)
        self.setLayout(self.main_layout)

        # Timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_blocks)
        self.timer.start(1000)  # Update every 500ms

    def read_train_creation_status(self):
        """Reads Train_Instance and Baud rates from PLC output file.
        Returns:
            tuple: (train_instance, baud_dict) where baud_dict contains Baud1-Baud4 with their values
        """
        baud_dict = {
            'Baud1': [],
            'Baud2': [],
            'Baud3': [],
            'Baud4': []
        }
        train_instance = 0

        try:
            with open("PLC_OUTPUTS_Baud_Train_Instance.txt", "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse Train_Instance
                    if line.startswith("Train_Instance="):
                        train_instance = int(line.split("=")[1])
                    
                    # Parse Baud rates
                    elif "-Baud" in line:
                        try:
                            baud_parts = line.split("=")
                            baud_name = baud_parts[0].split("-")[-1]  # Gets Baud1, Baud2, etc.
                            baud_values = [int(x) for x in baud_parts[1].split(",") if x.strip()]
                            
                            if baud_name in baud_dict:
                                baud_dict[baud_name] = baud_values
                        except (IndexError, ValueError) as e:
                            print(f"Error parsing baud line '{line}': {e}")
                            continue

            # Update instance variables
            self.train_creations = train_instance
            self.train_bauds = baud_dict
            
            return train_instance, baud_dict

        except Exception as e:
            print(f"Error reading PLC_OUTPUTS_Baud_Train_Instance.txt: {e}")
            return 0, {k: [] for k in baud_dict}  # Return defaults on error

    def read_train_output(self, train_number):
        """Reads Delta_Position, Station_Status, and Passengers from the specific train's output file."""
        try:
            file_path = f"train{train_number}_outputs.txt"
            with open(file_path, "r") as file:
                data = file.readlines()

            delta_position = None
            station_status = None
            passengers = None  # Add passengers variable

            for line in data:
                if line.startswith("Delta_Position:"):
                    delta_position = float(line.split(":")[1].strip())
                elif line.startswith("Station_Status:"):
                    station_status = int(line.split(":")[1].strip())
                elif line.startswith("Passengers:"):  # Read passengers count
                    passengers = int(line.split(":")[1].strip())

            return delta_position, station_status, passengers

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None, None, None  # Return None for all if an error occurs

    def get_speed_authority(self, block_number):
        """Determine the suggested speed authority based on block number and baud rates."""
        if not hasattr(self, 'train_bauds'):
            return "N/A"
        
        if 1 <= block_number <= 28:
            return f"Baud1: {self.train_bauds['Baud1']}"
        elif 29 <= block_number <= 76:
            return f"Baud2: {self.train_bauds['Baud2']}"
        elif 77 <= block_number <= 100:
            return f"Baud3: {self.train_bauds['Baud3']}"
        elif 101 <= block_number <= 150:
            return f"Baud4: {self.train_bauds['Baud4']}"
        return "N/A"

    def update_blocks(self):
        """Check train positions, update block occupancy, and log ticket sales with speed authority."""
        # Get train instance and baud rates
        train_instance, baud_rates = self.read_train_creation_status()
        
        # Track if we need to initialize file writing for new trains
        new_train_created = False
        previous_train_count = len(self.green_lines)

        # Create new train if needed
        if self.train_creations == 1 and (not self.green_lines or self.boxes.get(63).state == 0):
            print(f"Creating train {len(self.green_lines) + 1}...")
            self.create_next_train()
            new_train_created = True
            # Initialize ticket array for the new train
            self.green_lines[-1].ticket_array = []

        if not self.green_lines:
            return

        global_occupancy = {}
        train_statuses = []

        for train_number, green_line in enumerate(self.green_lines, start=1):
            try:
                if train_number > len(self.train_positions):
                    print(f"Skipping train {train_number} as it has no recorded position.")
                    continue

                # Read train data
                delta_position, station_status, passengers = self.read_train_output(train_number)
                if None in (delta_position, station_status, passengers):
                    print(f"Error reading train {train_number}'s data.")
                    continue

                # Update train position and get occupied blocks
                self.train_positions[train_number - 1] = delta_position
                occupied_blocks = green_line.find_blocks(delta_position)
                global_occupancy.update({block: train_number for block in occupied_blocks})
                train_statuses.append(f"Train {train_number}: {', '.join(map(str, occupied_blocks))}")

                # Safely get current time
                try:
                    current_time = global_variables.current_time.strftime("%H:%M")
                except:
                    current_time = "--:--"

                # Get speed authority for the first occupied block (or default if none)
                speed_auth = "N/A"
                if occupied_blocks:
                    block_num = occupied_blocks[0]
                    if 1 <= block_num <= 28:
                        speed_auth = f"{baud_rates['Baud1']}"
                    elif 29 <= block_num <= 76:
                        speed_auth = f"{baud_rates['Baud2']}"
                    elif 77 <= block_num <= 100:
                        speed_auth = f"{baud_rates['Baud3']}"
                    elif 101 <= block_num <= 150:
                        speed_auth = f"{baud_rates['Baud4']}"

                # Handle new train initialization
                if new_train_created and train_number > previous_train_count:
                    if train_number == 1:
                        write_to_file(
                            f"Train {train_number}:\n"
                            f"Overlapping Blocks at position {delta_position}m: {occupied_blocks}\n"
                            f"Suggested_Speed_Authority: {speed_auth}\n"
                            f"New passengers getting on: 0\n"
                            f"Total count: 0\n"
                            f"Ticket Sales History: []\n\n",
                            mode="w"
                        )
                    else:
                        append_new_train_data(
                            train_number,
                            occupied_blocks,
                            [],
                            0,
                            0,
                            delta_position,
                            speed_auth
                        )

                # Handle station arrivals and passenger counting
                if station_status == 1:
                    if not hasattr(green_line, 'station_visited'):
                        green_line.station_visited = False
                    
                    if not green_line.station_visited:
                        print(f"Train {train_number} is at a station. Running pass_count()...")
                        passengers, new_passengers, starting_pass = pass_count(passengers, station_status)
                        green_line.passengers_count = passengers
                        green_line.new_passengers = new_passengers

                        if not hasattr(green_line, 'ticket_array'):
                            green_line.ticket_array = []
                        
                        green_line.ticket_array.append([new_passengers, current_time])

                        update_train_data(
                            train_number,
                            occupied_blocks,
                            green_line.ticket_array,
                            new_passengers,
                            passengers,
                            delta_position,
                            speed_auth
                        )
                        green_line.station_visited = True
                
                # Reset station flag when leaving
                if station_status == 0 and hasattr(green_line, 'station_visited'):
                    green_line.station_visited = False

                # Update train data even when not at station
                update_train_data(
                    train_number,
                    occupied_blocks,
                    green_line.ticket_array if hasattr(green_line, 'ticket_array') else [],
                    green_line.new_passengers if hasattr(green_line, 'new_passengers') else 0,
                    green_line.passengers_count if hasattr(green_line, 'passengers_count') else 0,
                    delta_position,
                    speed_auth
                )

            except Exception as e:
                print(f"Error processing train {train_number}: {str(e)}")
                continue

        new_train_created = False

        # Update UI
        for box in self.boxes.values():
            box.set_state(1 if box.index in global_occupancy else 0)
        self.train_list_display.setText("\n".join(train_statuses) if train_statuses else "No trains are active.")
        
    def create_next_train(self):
        """Create a new train instance if there is no active train or block 63 is vacant."""
        grid_data = load_csv("data2.csv")
        new_green_line = GreenLineOccupancy(grid_data)
        self.green_lines.append(new_green_line)
        self.train_positions.append(0)  # Ensure positions are correctly tracked
        print(f"A new train has been created. Total trains: {len(self.green_lines)}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GridWindow()
    window.show()
    sys.exit(app.exec_())
