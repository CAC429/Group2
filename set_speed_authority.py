import json

def set_speed_authority(speed, authority):

    try:
        with open('PLC_INPUTS.json', 'r') as file:
            data = json.load(file)
    except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"CTC failed to read PLC_INPUTS JSON: {e}")
        return

    #update data
    data["Suggested_Speed"] = speed
    data["Suggested_Authority"] = authority

    #dump into json
    try:
        with open('PLC_INPUTS.json', 'w') as file:
            json.dump(data, file, indent=4)
    except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Failed to write PLC_INPUTS JSON: {e}")
        return