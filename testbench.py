import sys
from PyQt5.QtWidgets import QApplication, QInputDialog
from main import TrackModelUI

def main():
    app = QApplication(sys.argv)
    
    # Create the main window
    window = TrackModelUI()
    window.show()

    # Ask for the CSV file name using a dialog
    csv_file, ok = QInputDialog.getText(window, 'CSV File', 'Enter the name of the CSV file to load (e.g., data.csv):')
    if ok and csv_file:
        window.Load_Display_CSV(csv_file)
        window.table.setVisible(True)

    # Ask for the boolean input for the switch function using a dialog
    switch_input, ok = QInputDialog.getText(window, 'Rail position', 'Enter 0 for station B or 1 for station C')
    if ok:
        switch_state = True if switch_input.strip().lower() == 'true' else False
        window.Switch_Function(switch_state)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
