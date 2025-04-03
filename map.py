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
        """Reads Train_Creations value from PLC_OUTPUTS.txt."""
        try:
            with open("PLC_OUTPUTS_Baud_Train_Instance.txt", "r") as file:
                for line in file:
                    if "Train_Instance" in line:
                        _, value = line.strip().split("=")
                        self.train_creations = int(value.strip())
                        break
        except Exception as e:
            print(f"Error reading PLC_OUTPUTS_Baud_Train_Instance.txt: {e}")

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

    def update_blocks(self):
        """Check train positions, update block occupancy, and log ticket sales."""
        self.read_train_creation_status()

        # Ensure a train is created if Train_Creations is 1
        if self.train_creations == 1 and not self.green_lines:
            print("Creating the first train...")
            self.create_next_train()

        if not self.green_lines:
            return

        global_occupancy = {}
        train_statuses = []

        for train_number, green_line in enumerate(self.green_lines, start=1):
            if train_number > len(self.train_positions):
                print(f"Skipping train {train_number} as it has no recorded position.")
                continue  # Avoid index errors

            # Read Delta_Position, Station_Status, and Passengers
            delta_position, station_status, passengers = self.read_train_output(train_number)

            if delta_position is None or station_status is None or passengers is None:
                print(f"Error reading train {train_number}'s data.")
                continue

            # Update train position
            self.train_positions[train_number - 1] = delta_position

            # Log occupancy
            occupied_blocks = green_line.find_blocks(self.train_positions[train_number - 1])
            global_occupancy.update({block: train_number for block in occupied_blocks})
            
            train_statuses.append(f"Train {train_number}: {', '.join(map(str, occupied_blocks))}")

            # **NEW: Call pass_count() if Station_Status is 1**
            if station_status == 1:
                print(f"Train {train_number} is at a station. Calling pass_count function...")

                passengers, new_passengers, starting_pass = pass_count(passengers, station_status)

                # Update the train's stored passenger count
                green_line.passengers_count = passengers

                print(f"Train {train_number} - Passengers Onboard: {passengers}, New: {new_passengers}, Initial: {starting_pass}")

        # Update UI
        for box in self.boxes.values():
            box.set_state(1 if box.index in global_occupancy else 0)

        self.train_list_display.setText("\n".join(train_statuses) if train_statuses else "No trains are active.")

        # Create additional trains if needed
        if self.train_creations == 1 and self.boxes.get(63).state == 0:
            self.create_next_train()


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
