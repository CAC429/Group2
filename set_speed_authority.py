import json

def set_speed_authority(speed, authority):

    with open('PLC_INPUTS.json', 'r') as file:
        data = json.load(file)

    #update data
    data["Suggested_Speed"] = speed
    data["Suggested_Authority"] = authority

    #dump into json
    with open('PLC_INPUTS.json', 'w') as file:
        json.dump(data, file, indent=4)