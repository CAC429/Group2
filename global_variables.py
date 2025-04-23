from datetime import datetime

system_multiplier = 1
timer_interval = int(1000 / system_multiplier)
#0 -> green line, 1 -> red line
line = 0
current_maintenance = []
block_occupancies = []
current_time = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
if line == 0:
    static_speed = [20]*116 + [15]*5 + [20]*29
    static_authority = [100]*12 + [150]*8 + [300]*4 + [200] + [100] + [50]*36 + [100]*2 + [200]*2 + [100]*10 + [300]*9 + [100] + [86.6] + [100] + [75]*12 + [35] + [100]*2 + [80] + [100]*2 + [90] + [100]*6 + [162] + [100]*2 + [50]*2 + [40] + [50]*28 + [184] + [40] + [35]
elif line == 1:
    static_speed = [20]*76
    static_authority = [50]*6 + [75]*6 + [70] + [60]*2 + [50] + [200] + [400]*2 + [200] + [100]*3 + [50]*5 + [60]*2 + [50]*9 + [60]*2 + [50]*4 + [75]*3 + [50]*3 + [43.2] + [50]*2 + [75]*12 + [50]*10
dynamic_speed = []
dynamic_authority = []