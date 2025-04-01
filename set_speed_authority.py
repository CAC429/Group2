import fileinput

def set_speed_authority(speed, authority):

    authority_message = 'Suggested_Authority='
    speed_message = 'Suggested_Speed='
    file_name = 'PLC_INPUTS.txt'

    with fileinput.input(file_name, inplace=True) as file:
        for line in file:
            if line.startswith('Suggested_Authority='):
                print(f'{authority_message}{','.join(map(str, authority))}')
            elif line.startswith('Suggested_Speed='):
                print(f'{speed_message}{','.join(map(str, speed))}')
            else:
                print(line, end='')