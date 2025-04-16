import json

def set_speed_authority(speed, authority):

    with open('PLC_INPUTS.json', 'r') as file:
        data = json.load(file)

    #update data
    data["suggested_speed"] = speed
    data["suggested_authority"] = authority

    #dump into json
    with open('PLC_INPUTS.json', 'w') as file:
        json.dump(data, file, indent=4)