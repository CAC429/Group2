from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QGridLayout, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import sys
import json

class SwitchWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track System Monitor")
        self.setFixedSize(1000, 800)
        
        self.switch_widgets = []
        self.light_widgets = []
        self.failure_widgets = []
        self.crossbar_widgets = []
        self.active_failures = set()
        
        self.init_ui()
        
        # Initialize with default values (all switches in position 0)
        self.update_display({
            'switch_positions': [0, 0, 0, 0, 0, 0],
            'track_failures': [0]*12,
            'light_control': [0]*12,
            'crossbar_control': [0, 0]
        })
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_plc_updates)
        self.timer.start(1000)

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        title = QLabel("Track System Monitor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 24px; padding: 10px;")
        main_layout.addWidget(title)
        
        quadrants = QWidget()
        grid_layout = QGridLayout(quadrants)
        grid_layout.setSpacing(15)
        
        # Quadrant 1: Switch Positions (Top Left)
        switch_group = QGroupBox("Switch Positions")
        switch_layout = QVBoxLayout()
        
        switch_grid = QWidget()
        # Use QGridLayout for the switches to arrange them in pairs
        switch_grid_layout = QGridLayout(switch_grid)
        switch_grid_layout.setHorizontalSpacing(30)  # Space between columns
        switch_grid_layout.setVerticalSpacing(20)    # Space between rows
        
        # Create 6 switch displays in 3 rows × 2 columns
        for switch_num in range(1, 7):
            switch_widget = QWidget()
            switch_widget.setFixedSize(200, 150)
            
            layout = QVBoxLayout(switch_widget)
            layout.setAlignment(Qt.AlignCenter)
            
            # Image display
            switch_image = QLabel()
            switch_image.setFixedSize(160, 130)
            switch_image.setAlignment(Qt.AlignCenter)
            switch_image.setStyleSheet("""
                background-color: lightgray;
                border: 2px solid black;
                border-radius: 5px;
            """)
            
            # Label
            switch_label = QLabel(f"Switch {switch_num}")
            switch_label.setAlignment(Qt.AlignCenter)
            switch_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            
            layout.addWidget(switch_image)
            layout.addWidget(switch_label)
            
            # Calculate row and column positions for pairing
            row = (switch_num - 1) // 2  # 0, 0, 1, 1, 2, 2
            col = (switch_num - 1) % 2   # 0, 1, 0, 1, 0, 1
            switch_grid_layout.addWidget(switch_widget, row, col)
            
            self.switch_widgets.append({
                'number': switch_num,
                'image': switch_image,
                'position': -1
            })
        
        switch_layout.addWidget(switch_grid)
        switch_group.setLayout(switch_layout)
        grid_layout.addWidget(switch_group, 0, 0)
        
        # Quadrant 2: Active Track Failures (Top Right)
        failure_group = QGroupBox("Active Track Failures")
        failure_layout = QVBoxLayout()
        
        self.failure_scroll = QScrollArea()
        self.failure_scroll.setWidgetResizable(True)
        failure_content = QWidget()
        self.failure_content_layout = QVBoxLayout(failure_content)
        self.failure_content_layout.setAlignment(Qt.AlignTop)
        
        self.no_failures_label = QLabel("No active track failures")
        self.no_failures_label.setAlignment(Qt.AlignCenter)
        self.no_failures_label.setStyleSheet("font-style: italic; color: gray;")
        self.failure_content_layout.addWidget(self.no_failures_label)
        
        self.failure_scroll.setWidget(failure_content)
        failure_layout.addWidget(self.failure_scroll)
        failure_group.setLayout(failure_layout)
        grid_layout.addWidget(failure_group, 0, 1)
        
        # Quadrant 3: Light Control (Bottom Left)
        light_group = QGroupBox("Light Control")
        light_layout = QVBoxLayout()
        
        light_grid = QWidget()
        light_grid_layout = QGridLayout(light_grid)
        light_grid_layout.setHorizontalSpacing(10)
        light_grid_layout.setVerticalSpacing(10)
        
        for light_num in range(1, 13):
            light_widget = QLabel(f"Light {light_num}")
            light_widget.setAlignment(Qt.AlignCenter)
            light_widget.setFixedSize(70, 40)
            light_widget.setStyleSheet("""
                background-color: gray;
                border: 1px solid black;
                border-radius: 3px;
            """)
            
            row = (light_num - 1) // 4
            col = (light_num - 1) % 4
            light_grid_layout.addWidget(light_widget, row, col)
            
            self.light_widgets.append(light_widget)
        
        light_layout.addWidget(light_grid)
        light_group.setLayout(light_layout)
        grid_layout.addWidget(light_group, 1, 0)
        
        # Quadrant 4: Crossbar Control (Bottom Right)
        crossbar_group = QGroupBox("Crossbar Control")
        crossbar_layout = QVBoxLayout()
        
        crossbar_grid = QWidget()
        crossbar_grid_layout = QHBoxLayout(crossbar_grid)
        crossbar_grid_layout.setSpacing(20)
        
        for crossbar_num in range(1, 3):
            crossbar_widget = QLabel(f"Crossbar {crossbar_num}")
            crossbar_widget.setAlignment(Qt.AlignCenter)
            crossbar_widget.setFixedSize(100, 60)
            crossbar_widget.setStyleSheet("""
                background-color: gray;
                border: 1px solid black;
                border-radius: 5px;
            """)
            
            crossbar_grid_layout.addWidget(crossbar_widget)
            self.crossbar_widgets.append(crossbar_widget)
        
        crossbar_layout.addWidget(crossbar_grid)
        crossbar_group.setLayout(crossbar_layout)
        grid_layout.addWidget(crossbar_group, 1, 1)
        
        main_layout.addWidget(quadrants)

    # [Rest of the methods remain exactly the same as previous version...]
    def update_switches(self, switch_positions):
        """Update switch images based on positions"""
        for widget in self.switch_widgets:
            switch_num = widget['number']
            if switch_num <= len(switch_positions):
                current_pos = switch_positions[switch_num - 1]
                
                if widget['position'] != current_pos:
                    try:
                        image_path = f"switch{switch_num}{current_pos}.png"
                        pixmap = QPixmap(image_path)
                        
                        if pixmap.isNull():
                            widget['image'].setStyleSheet("""
                                background-color: lightgray;
                                border: 2px solid black;
                                border-radius: 5px;
                            """)
                            print(f"Switch {switch_num} image not found: {image_path}")
                        else:
                            widget['image'].setStyleSheet("border: 2px solid black; border-radius: 5px;")
                            widget['image'].setPixmap(
                                pixmap.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                            
                        widget['position'] = current_pos
                        
                    except Exception as e:
                        print(f"Error loading switch {switch_num} image: {e}")
                        widget['image'].setStyleSheet("""
                            background-color: lightgray;
                            border: 2px solid black;
                            border-radius: 5px;
                        """)

    def update_display(self, plc_data):
        """Update all displays based on PLC data"""
        self.update_switches(plc_data['switch_positions'])
        self.update_failures(plc_data['track_failures'])
        self.update_lights(plc_data['light_control'])
        self.update_crossbars(plc_data['crossbar_control'])
    
    def update_failures(self, failures):
        """Update track failure indicators - only show active failures"""
        current_failures = set()
        
        for i, status in enumerate(failures[:150], start=1):
            if status == 1:
                current_failures.add(i)
        
        for block in list(self.active_failures):
            if block not in current_failures:
                for i in reversed(range(self.failure_content_layout.count())):
                    widget = self.failure_content_layout.itemAt(i).widget()
                    if widget and widget.property("block_num") == block:
                        self.failure_content_layout.removeWidget(widget)
                        widget.deleteLater()
        
        for block in current_failures:
            if block not in self.active_failures:
                failure_widget = QLabel(f"Track {block} FAILURE")
                failure_widget.setProperty("block_num", block)
                failure_widget.setAlignment(Qt.AlignCenter)
                failure_widget.setStyleSheet("""
                    background-color: red;
                    color: white;
                    border: 1px solid darkred;
                    border-radius: 3px;
                    padding: 5px;
                    font-weight: bold;
                """)
                self.failure_content_layout.addWidget(failure_widget)
        
        self.active_failures = current_failures
        self.no_failures_label.setVisible(len(self.active_failures) == 0)
    
    def update_lights(self, lights):
        """Update light control indicators"""
        for i, widget in enumerate(self.light_widgets):
            if i < len(lights):
                status = lights[i]
                color = "red" if status == 1 else "lime"
                widget.setStyleSheet(f"""
                    background-color: {color};
                    border: 1px solid black;
                    border-radius: 3px;
                """)
    
    def update_crossbars(self, crossbars):
        """Update crossbar control indicators"""
        for i, widget in enumerate(self.crossbar_widgets):
            if i < len(crossbars):
                status = crossbars[i]
                color = "yellow" if status == 1 else "gray"
                widget.setStyleSheet(f"""
                    background-color: {color};
                    border: 1px solid black;
                    border-radius: 5px;
                """)
    
    def check_plc_updates(self):
        """Check for updates in PLC outputs and update display"""
        plc_data = self.read_plc_outputs()
        self.update_display(plc_data)
    
    def read_plc_outputs(self, file_path="PLC_OUTPUTS.json"):
        """Read all relevant PLC outputs from JSON file"""
        plc_data = {
            'switch_positions': [0, 0, 0, 0, 0, 0],
            'track_failures': [0]*150,
            'light_control': [0]*12,
            'crossbar_control': [0, 0]
        }
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Update from JSON data
            plc_data.update({
                'switch_positions': data.get("Actual_Switch_Position", [0]*6),
                'track_failures': data.get("Track_Failure", [0]*150),
                'light_control': data.get("Light_Control", [0]*12),
                'crossbar_control': data.get("Cross_Bar_Control", [0, 0])
            })
            
        except FileNotFoundError:
            print(f"PLC outputs JSON file not found: {file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON in PLC outputs file: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading PLC outputs: {e}")
            
        return plc_data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = SwitchWindow()
    panel.show()
    sys.exit(app.exec_())
