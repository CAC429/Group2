# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget

# Create the application object
app = QApplication(sys.argv)

# Create the main window
window = QWidget()
window.setWindowTitle('My First PyQt5 Window')
window.setGeometry(100, 100, 400, 300)  # x, y, width, height
window.show()

# Run the application event loop
sys.exit(app.exec_())

#hiii