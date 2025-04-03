#Philip Sherman
#Trains Group 2
#Train Controller SW UI Test Bench
#2/19/2025

import sys
import unittest
from PyQt5.QtWidgets import QApplication, QComboBox, QLabel, QPushButton, QLineEdit
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from uiscript import MainWindow

class TestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        QTest.qWaitForWindowExposed(self.window)
    
    def tearDown(self):
        self.window.close()

    def test_constant_input(self):
        ki_input = self.window.findChild(QLineEdit, "ki_input")
        kp_input = self.window.findChild(QLineEdit, "kp_input")
        submit_button = self.window.findChild(QPushButton, "submit_constants")

        self.assertIsNotNone(ki_input, "ki_input not found")
        self.assertIsNotNone(kp_input, "kp_input not found")
        self.assertIsNotNone(submit_button, "submit_constants not found")

        ki_input.setFocus()
        QTest.keyClicks(ki_input, "1.5")

        kp_input.setFocus()
        QTest.keyClicks(kp_input, "2.0")
        QTest.mouseClick(submit_button, Qt.LeftButton)

        self.assertEqual(float(ki_input.text()), 1.5)
        self.assertEqual(float(kp_input.text()), 2.0)

    def test_train_selection(self):
        dropdown = self.window.findChild(QComboBox, "train_selector")
        label = self.window.findChild(QLabel, "stats_display")

        self.assertIsNotNone(dropdown, "train_selector not found")
        self.assertIsNotNone(label, "stats_display not found")

        dropdown.setCurrentIndex(1)
        self.assertIn("Train 2", label.text())

    def test_power_calculation(self):
        ki_input = self.window.findChild(QLineEdit, "ki_input")
        kp_input = self.window.findChild(QLineEdit, "kp_input")
        calculate_button = self.window.findChild(QPushButton, "calculate_power")
        output_label = self.window.findChild(QLabel, "power_output")

        self.assertIsNotNone(ki_input, "ki_input not found")
        self.assertIsNotNone(kp_input, "kp_input not found")
        self.assertIsNotNone(calculate_button, "calculate_power not found")
        self.assertIsNotNone(output_label, "power_output not found")

        ki_input.setFocus()
        QTest.keyClicks(ki_input, "1.0")

        kp_input.setFocus()
        QTest.keyClicks(kp_input, "2.0")

        QTest.mouseClick(calculate_button, Qt.LeftButton)

        self.assertTrue(float(output_label.text()) > 0, "Power output not updated")

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

if __name__ == "__main__":
    unittest.main()
