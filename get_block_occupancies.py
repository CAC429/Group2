import fileinput
import global_variables

def get_block_occupancies():
    
    occupancies = []
    temp = ''
    file_name = 'PLC_OUTPUTS.txt'

    #read from wayside output file
    try:
        for line in fileinput.input(file_name):
            if line.startswith('Occupancy='):
                temp = line
    except FileNotFoundError:
        print('CTC: File not accessible')
    except Exception as e:
        print('CTC: File error')

    #eliminate commas or other erronious characters
    for c in temp:
        if c != '0' and c != '1':
            pass
        else:
            occupancies.append(c)
    
    #treat blocks under maintenance as occupied
    if global_variables.current_maintenance:
        for i in global_variables.current_maintenance:
            occupancies[i] = 1

    #swap from strings to integers
    occupancies = [int(i) for i in occupancies]

    return occupancies