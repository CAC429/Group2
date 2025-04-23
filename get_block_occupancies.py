import global_variables
import json

def get_block_occupancies():

    #green line
    if global_variables.line == 0:
        try:
            with open('PLC_OUTPUTS.json', 'r') as file:
                data = json.load(file)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to read PLC_OUTPUTS JSON: {e}")
            return global_variables.block_occupancies
    #red line
    elif global_variables.line == 1:
        try:
            with open('PLC_OUTPUTS2.json', 'r') as file:
                data = json.load(file)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to read PLC_OUTPUTS2 JSON: {e}")
            return global_variables.block_occupancies
        
    occupancies = data["Occupancy"]

    #treat blocks in maintenance as occupied blocks
    if global_variables.current_maintenance:
        for i in global_variables.current_maintenance:
            occupancies[i] = 1

    return occupancies