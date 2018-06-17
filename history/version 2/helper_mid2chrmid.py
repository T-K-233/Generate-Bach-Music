import csv
import os
import re

SAMPLE_RATE = 10

def cvt_midi_2_csv(filepath):
    midi_list = list(os.walk(filepath))[0][2]
    for midi in midi_list:
        csv = midi.replace('.mid', '.csv')
        os.system("tool\Midicsv.exe .\midi\\"+midi+" .\csv\\"+csv)

def cvt_csv_2_chrmid(filename, filename_out):
    csv_arr = []
    with open(filename) as f:
        file = list(csv.reader(f))
    for line in file:
        if len(line) != 6 or not re.search('[N|n]ote', line[2]):
            continue
        if re.search('off', line[2]) or line[5] == ' 0':
            line.append(False)
        else:
            line.append(True)
        line.pop(5)
        line.pop(3)
        line.pop(2)
        line.pop(0)
        line[0], line[1] = int(line[0]), int(line[1])
        csv_arr.append(line)
    csv_arr.sort()
    i = 0
    keys = []
    string = ''
    for t in range(0, csv_arr[-1][0]-SAMPLE_RATE, SAMPLE_RATE):
        while csv_arr[i][0] < t + SAMPLE_RATE:
            if csv_arr[i][2] and csv_arr[i][1] not in keys:
                keys.append(csv_arr[i][1])
            if not csv_arr[i][2] and csv_arr[i][1] in keys:
                keys.remove(csv_arr[i][1])
            if i > len(csv_arr):
                break
            i += 1
        if keys:
            for note in keys:
                string += chr(note)
            string += ' '
        else:
            string += '~ '
    file = open(filename_out, 'a+', encoding='utf-8')
    file.write(string)

def main(midi_path, filename_out):
    cvt_midi_2_csv('midi')
    file = open(filename_out, 'w+', encoding='utf-8')
    file.close()
    csv_list = list(os.walk('csv'))[0][2]
    for csv in csv_list:
        cvt_csv_2_chrmid('csv/'+csv, filename_out)

main('midi', 'input.txt')


