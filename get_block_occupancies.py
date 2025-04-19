import global_variables
import json

def get_block_occupancies():
    
    try:
        with open('PLC_OUTPUTS.json', 'r') as file:
            data = json.load(file)
    except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Failed to read PLC_OUTPUTS JSON: {e}")
        return

    occupancies = data["Occupancy"]

    #treat blocks in maintenance as occupied blocks
    if global_variables.current_maintenance:
        for i in global_variables.current_maintenance:
            occupancies[i] = 1

    return occupancies