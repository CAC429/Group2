import sys
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer

from greenlineoccup import find_blocks, load_csv  # Ensure this file exists

class ClickableBox(QPushButton):
    def __init__(self, index, row_data):
        super().__init__()
        self.index = index
        self.row_data = row_data  # Store corresponding row from CSV
        self.state = 0  # 0 for red, 1 for green
        self.setFixedSize(70, 70)

        label = row_data.get("Block Number", str(index))  # Default to index if missing
        self.setText((row_data.get("Section", "") + str(label)))

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
    
    def show_info(self):
        """Display block info in a message box."""
        info_text = f"Box {self.index}\nState: {'Green' if self.state else 'Red'}\n\n"
        info_text += "\n".join([f"{key}: {value}" for key, value in self.row_data.items()])
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Box Info")
        msg_box.setText(info_text)
        msg_box.setStyleSheet("background-color: white;")
        msg_box.exec_()
        
    def set_state(self, new_state):
        """Set the state of the block and update the color."""
        self.state = new_state
        self.update_color()


class GridWindow(QWidget):
    def __init__(self, csv_file, find_blocks_data_file):
        super().__init__()
        self.setWindowTitle("Green Line Blocks")
        self.layout = QGridLayout()
        self.boxes = []
        self.data_rows = self.load_csv(csv_file)
        self.find_blocks_data = load_csv(find_blocks_data_file)

        # Train position tracking
        self.train_position = 0  # Start at 0m

        for i in range(150):
            row_data = self.data_rows[i] if i < len(self.data_rows) else {}
            box = ClickableBox(i, row_data)
            self.boxes.append(box)
            self.layout.addWidget(box, i // 15, i % 15)  # Arrange in a 15x10 grid
        
        self.setLayout(self.layout)

        # Timer to update occupancy periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_blocks)
        self.timer.start(1000)  # Update every second
    
    def load_csv(self, csv_file):
        """Load the CSV file containing block information."""
        return load_csv(csv_file)
    
    def set_box_state(self, index, state):
        """Set the state of a box (green for occupied, red for free)."""
        if 0 <= index < len(self.boxes):
            print(f"Setting Block {index} to {'Green' if state else 'Red'}")  # Debugging
            self.boxes[index].set_state(state)

    def update_blocks(self):
        """Check the current train position and update block occupancy."""
        occupied_blocks = find_blocks(self.train_position, self.find_blocks_data)

        print(f"\nUpdating UI: Train at {self.train_position}m, Occupied Blocks: {occupied_blocks}")

        # Reset all blocks to red (not occupied)
        for box in self.boxes:
            box.set_state(0)

        # Set occupied blocks to green
        for block_num in occupied_blocks:
            # Find matching block index in the grid's dataset
            for i, row in enumerate(self.data_rows):
                if str(row.get("Block Number")) == str(block_num):
                    self.set_box_state(i, 1)
                    break  # Stop searching once we find the match

        # Ensure UI refresh
        self.repaint()

        # Move train forward (for testing)
        self.train_position += 50  # Move 50m per update
        if self.train_position > 24000:  # Reset position when exceeding max range
            self.train_position = 0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GridWindow("data1.csv", "data2.csv")  # Load CSV files
    window.show()
    sys.exit(app.exec_())