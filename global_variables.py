from datetime import datetime

#speed = [45]*12 + [70]*4 + [60]*4 + [70]*6 + [30]*36 + [70]*4 + [40]*10 + [70]*9 + [25]*15 + [26] +[28]*8 + [30]*7 + [15]*5 + [20]*29
#blue, red, green
system_multiplier = 1
timer_interval = int(1000 / system_multiplier)
line = 'green'
current_maintenance = []
block_occupancies = []
current_time = datetime.now()
if line == 'green':
    static_speed = [20]*150
    static_authority = [100]*12 + [150]*8 + [300]*4 + [200] + [100] + [50]*36 + [100]*2 + [200]*2 + [100]*10 + [300]*9 + [100] + [86.6] + [100] + [75]*12 + [35] + [100]*2 + [80] + [100]*2 + [90] + [100]*6 + [162] + [100]*2 + [50]*2 + [40] + [50]*28 + [184] + [40] + [35]
dynamic_speed = []
dynamic_authority = []