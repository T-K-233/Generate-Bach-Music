import csv
import os
import re
import time

SAMPLE_RATE = 10

def cvt_chrmid_2_csv(filename, filename_out):
    file = open(filename, encoding='utf-8')
    string = file.read()
    file.close()
    string = string.split(' ')
    keys = []
    prev_keys = []
    t = 0
    with open('result\\'+filename_out, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([0, 0, 'Header', 1, 4, 240])
        writer.writerow([1, 0, 'Start_track'])
        for line in string:
            if re.search('~', line):
                t += SAMPLE_RATE
                continue
            for note in line:
                if note not in keys:
                    keys.append(note)
                    if 0 <= ord(note) <= 127:
                        writer.writerow([1, t, 'Note_on_c', 0, ord(note), 107])
            for note in keys:
                if note not in line:
                    keys.remove(note)
                    if 0 <= ord(note) <= 127:
                        writer.writerow([1, t, 'Note_off_c', 0, ord(note), 0])
            t += SAMPLE_RATE
        writer.writerow([1, t, 'End_track'])
        writer.writerow([0, 0, 'End_of_file'])
def cvt_csv_2_midi(filepath):
    time.sleep(4)
    csv_list = list(os.walk(filepath))[0][2]
    for csv in csv_list:
        midi = csv.replace('.csv', '.mid')
        os.system("tool\Csvmidi.exe .\\result\\"+csv+" .\\result\\"+midi)

cvt_chrmid_2_csv('output.txt', 'result.csv')
cvt_csv_2_midi('result')
