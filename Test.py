import unittest

with open("PLC_OUTPUTS.txt", "r") as file:
    for line in file:
        if line.startswith("Track_Failure="):
            Track_Failure_Out = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Light_Control="):
            Light_Control_Out = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Actual_Switch_Position="):
            Actual_Switch_Position_Out = list(map(int, line.strip().split("=")[1].split(",")))

class TestGreenLineOutputs(unittest.TestCase):
    def test_track_failure(self):
        expected = [0] * 150
        expected[0] = 1
        actual = Track_Failure_Out
        self.assertEqual(actual, expected, "Track failure mismatch!")

    def test_light_control(self):
        expected = [0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1]
        actual = Light_Control_Out
        self.assertEqual(actual, expected, "Light control mismatch!")

    def test_switch_positions(self):
        expected = [0, 1, 1, 1, 1, 0]
        actual = Actual_Switch_Position_Out
        self.assertEqual(actual, expected, "Switch positions mismatch!")

    

if __name__ == '__main__':
    unittest.main()