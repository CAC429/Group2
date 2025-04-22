from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QApplication, QLabel)
from PyQt5.QtCore import Qt
import sys

class LineTab(QWidget):
    """Base class for both line tabs"""
    def __init__(self, line_color, switch_window_class):
        super().__init__()
        self.line_color = line_color
        self.switch_window_class = switch_window_class
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        layout = QHBoxLayout(self)
        
        # Create grid window
        grid_class = globals()[f"{self.line_color.capitalize()}LineGrid"]
        self.grid_window = grid_class()
        
        # Create switch window
        self.switch_window = self.switch_window_class()
        
        # Add to layout (grid on left, switch panel on right)
        layout.addWidget(self.grid_window, stretch=3)  # 75% width
        layout.addWidget(self.switch_window, stretch=1)  # 25% width

class GreenLineGrid(QWidget):
    """Your existing Green Line grid implementation"""
    def __init__(self):
        super().__init__()
        # Your existing green line grid code here
        self.setStyleSheet("background-color: #e8f5e9;")
        label = QLabel("GREEN LINE GRID")
        label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(label)

class RedLineGrid(QWidget):
    """Red Line grid implementation"""
    def __init__(self):
        super().__init__()
        # Similar to green line but for red line
        self.setStyleSheet("background-color: #ffebee;")
        label = QLabel("RED LINE GRID")
        label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(label)

class GreenLineSwitchWindow(QWidget):
    """Your existing Green Line switch window"""
    def __init__(self):
        super().__init__()
        # Your existing switch window code
        self.setStyleSheet("background-color: #c8e6c9;")
        label = QLabel("GREEN LINE SWITCHES")
        label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(label)

class RedLineSwitchWindow(QWidget):
    """Red Line switch window"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #ffcdd2;")
        label = QLabel("RED LINE SWITCHES")
        label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(label)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Train System Control")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Add tabs
        self.green_tab = LineTab("green", GreenLineSwitchWindow)
        self.red_tab = LineTab("red", RedLineSwitchWindow)
        
        self.tabs.addTab(self.green_tab, "Green Line")
        self.tabs.addTab(self.red_tab, "Red Line")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())