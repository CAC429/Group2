import subprocess

tc_hw_process = subprocess.Popen(["python", "train_controller_HW.py"])
tm_process = subprocess.Popen(["python", "Main_Train_Model.py"])

tc_hw_process.wait()
tm_process.wait()