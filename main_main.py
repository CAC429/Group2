import subprocess

# Start both scripts as subprocesses
ctc_process = subprocess.Popen(["python", "CTC_base.py"])
wayside_process = subprocess.Popen(["python", "Wayside_Controller.py"])

# Wait for both processes to finish (optional)
ctc_process.wait()
wayside_process.wait()