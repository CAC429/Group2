import subprocess

# Start both scripts as subprocesses
TC_HW_process = subprocess.Popen(["python", "train_controller_HW.py"])
train_model_process = subprocess.Popen(["python", "train_model.py"])

# Wait for both processes to finish (optional)
TC_HW_process.wait()
train_model_process.wait()