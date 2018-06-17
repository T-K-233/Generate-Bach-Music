import os

_note = 480
_tempo = 402685


def read_from_chmid(filename):
    print('—— Started ——')
    in_file = open(filename)
    in_text = in_file.read()
    in_file.close()
    main_arr = in_text.split(' ')
    return main_arr

def cvt_to_csv(main_arr, k_shift):
    result_text = '0, 0, Header, 1, 2, '+str(_note)+'\n1, 0, Start_track\n1, 0, Tempo, '+str(_tempo)+'\n1, 0, End_track\n2, 0, Start_track\n'
    t = 0
    keys = []
    for i in range(0, 160):
        keys.append(False)

    for line in main_arr:
        line = line.replace('~', '')
        for pos, is_on in enumerate(keys):
            if chr(pos) not in line and is_on:
                result_text += '2, '+str(t)+', Note_off_c, 0, '+str(pos+k_shift)+', 0\n'
                keys[pos] = False
            if chr(pos) in line and not is_on:
                result_text += '2, '+str(t)+', Note_on_c, 0, '+str(pos+k_shift)+', 107\n'
                keys[pos] = True
        t += 24
    result_text += '2, '+str(t)+', End_track\n'
    result_text += '0, 0, End_of_file'
    return result_text

def write_to_file(result_text):
    result_file = open('py_result.csv', 'w+')
    result_file.write(str(result_text))
    result_file.close()
    print('Converting to midi....')
    os.system(".\Csvmidi.exe .\py_result.csv .\py_result.mid")
    print('—— Done! ——')
    print('Midi outputed as "py_result.mid"')

def run(_filename, _k_shift=20):
    arr = read_from_chmid(_filename)
    string = cvt_to_csv(arr, _k_shift)
    write_to_file(string)

run('temp/py_result.txt', _k_shift=0)
