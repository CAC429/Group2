import global_variables
import json

#give two seconds before changing 0 to 1
def send_train(activate):

    #green line
    if global_variables.line == 0:
        try:
            with open('PLC_INPUTS.json', 'r') as file:
                data = json.load(file)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to read PLC_INPUTS JSON: {e}")
            return
    #red line
    elif global_variables.line == 1:
        try:
            with open('PLC_INPUTS2.json', 'r') as file:
                data = json.load(file)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to read PLC_INPUTS2 JSON: {e}")
            return
    
    #update train instance based on activate value
    if activate:
        data["Train_Instance"] = 1
    else:
        data["Train_Instance"] = 0

    #write back
    #green line
    if global_variables.line == 0:
        try:
            with open('PLC_INPUTS.json', 'w') as file:
                json.dump(data, file, indent=4)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to write PLC_INPUTS JSON: {e}")
            return
    #red line
    elif global_variables.line == 1:
        try:
            with open('PLC_INPUTS2.json', 'w') as file:
                json.dump(data, file, indent=4)
        except (PermissionError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to write PLC_INPUTS2 JSON: {e}")
            return