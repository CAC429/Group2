import fileinput

#give two seconds before changing 0 to 1
def send_train(activate):

    message = 'Train_Instance='
    file_name = 'PLC_INPUTS.txt'

    try:
        with fileinput.input(file_name, inplace=True) as file:
            for line in file:
                if line.startswith('Train_Instance='):
                    print(f'{message}{activate}')
                else:
                    print(line, end='')
    except FileNotFoundError:
        print('CTC: File not accessible')
    except Exception as e:
        print('CTC: File error')