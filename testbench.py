import sys
from PyQt5.QtWidgets import QApplication
from main import TrackModelUI

def main():
    app = QApplication(sys.argv)
    
    # Create the main window
    window = TrackModelUI()
    window.show()

    # Trigger image and CSV loading through buttons
    window.upload_button.clicked.connect(window.Load_Display_CSV)

    position1 = 300
    position2 = 50
    status = 1
    window.Set_Fail_status(status)
    window.Set_Train_Position(position1, position2)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()