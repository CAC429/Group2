from PyQt5.QtWidgets import *
from datetime import timedelta
import global_variables

def system_timer():
    global_variables.current_time += timedelta(seconds = 1)