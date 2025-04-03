import subprocess

# Start both scripts as subprocesses
ctc_process = subprocess.Popen(["python", "CTC_base.py"])
wayside_process = subprocess.Popen(["python", "Wayside_Controller.py"])
track_model_process = subprocess.Popen(["python", "map.py"])
train_model_process = subprocess.Popen(["python", "Main_Train_Model.py"])
train_controller_process = subprocess.Popen(["python", "uiscript.py"])
# Wait for both processes to finish (optional)
ctc_process.wait()
wayside_process.wait()
track_model_process.wait()
train_model_process.wait()
train_controller_process.wait()