import sys
from PyQt5.QtWidgets import (QApplication, QWidget)
from main import TrackModelUI
from PyQt5.QtCore import QTimer

class testbench(QWidget):
    def __init__(self, window):
    # Trigger image and CSV loading through buttons
    ##window.upload_button.clicked.connect(window.Load_Display_CSV)

    # Create a QTimer to repeatedly call the functions
        timer = QTimer()
        timer.setInterval(1000)  # Interval in milliseconds (1000 ms = 1 second)
    
    # Define a function to update the state
        def update_state():
            position1 = 200
            position2 = 50
            status = 1
            #newWindow.Set_Fail_status(status)
            #window.Set_Train_Position(position1, position2)
    
    # Connect the QTimer to the update_state function
        timer.timeout.connect(update_state)
        timer.start()  # Start the timer

def main():
    app = QApplication(sys.argv)
    # Create the main window
    window = TrackModelUI()
    window.show()

    newWindow = testbench(window)
    newWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()