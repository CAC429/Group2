from datetime import datetime
import threading

current_time = datetime.now()

def update_time():
    global current_time
    current_time = datetime.now()
    threading.Timer(1.0, update_time).start()

# Start the time updater
update_time()