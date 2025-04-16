import json

#give two seconds before changing 0 to 1
def send_train(activate):

    with open('PLC_INPUTS.json', 'r') as file:
        data = json.load(file)
    
    #update train instance based on activate value
    if activate:
        data["train_instance"] = 1
    else:
        data["train_instance"] = 0

    #write back
    with open('PLC_INPUTS.json', 'w') as file:
        json.dump(data, file, indent=4)