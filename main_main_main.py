import subprocess

tc_process = subprocess.Popen(["python", "uiscript.py"])
tm_process = subprocess.Popen(["python", "Main_Train_Model.py"])

tc_process.wait()
tm_process.wait()
