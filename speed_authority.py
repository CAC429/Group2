from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from main import *
from routes_maintenance import *
from speed_authority import *
from get_block_occupancies import *
from set_speed_authority import set_speed_authority

import global_variables
import math

class speed_authority(QWidget):
    #accept parent parameter (CTC_base)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.parent_window = parent #store reference

        layout = QHBoxLayout()
        
        ###
        #SPEED/AUTHORITY TIMER
        ###
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_speed_authority)
        self.timer.setInterval(global_variables.timer_interval)
        self.timer.start()

        ###
        #GRID
        ###
        #scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        #grid for speed/authority
        container = QWidget()
        statistics = QGridLayout(container)
        statistics.setSpacing(40)

        self.blocks = 150
        cols = 10
        self.labels = [QLabel(f'Block {i+1}\nSpeed: {global_variables.static_speed[i]} km/hr\nAuthority: {global_variables.static_authority[i]} km') for i in range(self.blocks)]
        for i in self.labels:
            pass
        for i in range(self.blocks):
            statistics.addWidget(self.labels[i], i // cols, i % cols)

        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    ###
    #RUNS EVERY x SECONDS
    ###
    def update_speed_authority(self):

        #store speed, authority, occupancies
        #sped and authority are copies so the static values aren't impacted
        speed = global_variables.static_speed[:]
        authority = global_variables.static_authority[:]
        global_variables.block_occupancies = get_block_occupancies()

        for i in range(len(global_variables.block_occupancies)):
            self.labels[i].setStyleSheet('color: black')
            #if block is occupied
            if global_variables.block_occupancies[i] == 1:
                #impact block before
                if i >= 1:
                    self.labels[i-1].setStyleSheet('color: red')
                    authority[i-1] = authority[i-1] / 4
                    speed[i-1] = speed[i-1] / 4
                #impact two blocks before
                if i >= 2:
                    self.labels[i-2].setStyleSheet('color: orange')
                    speed[i-2] = speed[i-2] / 2
    
        #set global speed and authority to new values
        global_variables.dynamic_speed = [math.floor(i) for i in speed]
        global_variables.dynamic_authority = [math.floor(i) for i in authority]

        [label.setText(f'Block {i+1}\nSpeed: {global_variables.dynamic_speed[i]} km/hr\nAuthority: {global_variables.dynamic_authority[i]} km') for i, label in enumerate(self.labels)]
        #change text for blocks in maintenance
        if global_variables.current_maintenance:
            for i in global_variables.current_maintenance:
                self.labels[i].setText(f'Block {i+1}\n !UNDER!\n!MAINTENANCE!')

        #update wayside controller (binary authority)
        set_speed_authority(global_variables.dynamic_speed, global_variables.dynamic_authority)
