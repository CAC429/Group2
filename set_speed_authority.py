import global_variables
import json

def set_speed_authority(speed, authority):

    if global_variables.line == 0:
        try:
            with open('PLC_INPUTS.json', 'r') as file:
                data = json.load(file)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"CTC failed to read PLC_INPUTS JSON: {e}")
            return
    elif global_variables.line == 1:
        try:
            with open('PLC_INPUTS2.json', 'r') as file:
                data = json.load(file)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"CTC failed to read PLC_INPUTS2 JSON: {e}")
            return

    #update data
    data["Suggested_Speed"] = speed
    data["Suggested_Authority"] = authority

    print(speed)

    #dump into json
    if global_variables.line == 0:
        try:
            with open('PLC_INPUTS.json', 'w') as file:
                json.dump(data, file, indent=4)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to write PLC_INPUTS JSON: {e}")
            return
    elif global_variables.line == 1:
        print('hello')
        try:
            with open('PLC_INPUTS2.json', 'w') as file:
                json.dump(data, file, indent=4)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to write PLC_INPUTS2 JSON: {e}")
            return