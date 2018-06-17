import os
import re

print('—— Started ——')

def read_from_file(filename, doConvert):
    if doConvert:
        csv_filename = filename.replace('.mid', '.csv')
        os.system(".\Midicsv.exe .\midi\\"+filename+" .\csv\\"+csv_filename)
        in_file = open(".\csv\\"+csv_filename)
    else:
        in_file = open(".\csv\\"+filename)
    in_text_arr = in_file.readlines()
    in_file.close()
    return in_text_arr

def cvt_to_arr(in_text):
    main_arr = []
    tempo = 0
    for line in in_text:
        if not re.search('Note_on_c', line) and not re.search('Note_off_c', line):
            continue
        line_arr = line.split(', ')
        line_arr[1] = int(line_arr[1])
        line_arr[4] = int(line_arr[4])
        line_arr[5] = int(line_arr[5][:-1])
        if re.search('Note_off_c', line) or line_arr[5] is 0:
            line_arr[2] = False
        elif re.search('Note_on_c', line) and line_arr[5] is not 0:
            line_arr[2] = True
        line_arr.pop(5)
        line_arr.pop(3)
        line_arr.pop(0)
        # line_arr[ time, is_open, note_num ]
        main_arr.append(line_arr)
    main_arr.sort()
    return main_arr

def cvt_to_string(main_arr, k_shift):
    t = 0
    keys = []

    result_text = ''

    for i in range(0, 160):
        keys.append(False)

    for item in main_arr:
        while(item[0]-t >= 24):
            t+=24
            all_mute = True
            for pos, note in enumerate(keys):
                if note:
                    all_mute = False
                    result_text += chr(pos+k_shift)
                # elif not note:
                #     result_text += '0'
            if all_mute:
                result_text += '~'
            result_text += ' '
        keys[item[2]-k_shift] = item[1]
    return result_text

def write_to_chmid(string):
    print('Writing to file....')
    result_file = open('temp/py_result.txt', 'a')
    result_file.write(str(string))
    result_file.close()
    print('—— Done! ——')
    print('Midi outputed as "py_result.chmid"')

def run(_filename, is_dir=False, k_shift=20, doConvert=True):
    files = list(os.walk('.\midi'))[0][2]
    print(files)
    result_file = open('temp/py_result.txt', 'w+')
    result_file.write('')
    result_file.close()
    for file in files:
        arr = read_from_file(file, doConvert)
        fmt_arr = cvt_to_arr(arr)
        string = cvt_to_string(fmt_arr, k_shift)
        write_to_chmid(string)


run('bwv806f.mid', k_shift=0, is_dir=True)
