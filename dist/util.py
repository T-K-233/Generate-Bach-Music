import shutil
import csv
import re
import os

temp_path = ".\\temp\\"
data_path = "..\\data\\midi\\"


class Params:
    sample_rate = 12
    offset = 300
    num_of_notes = 130
    output_name = 'sample'

# make a temp folder to store csv files
def make_temp_folder():
    try:
        os.makedirs(temp_path)
    except:
        shutil.rmtree(temp_path)
        os.makedirs(temp_path)

# convert csv string into compressed character-level string
def encode(csv_string, params):
    score = []

    # reformat csv array
    for row in csv_string:
        if len(row) < 6 or not re.search('[N|n]ote', row[2]):
            continue
        tick = int(int(row[1]) / params.sample_rate)
        note = int(row[4])
        on_off = not(re.search('[O|o]ff', row[2]) or int(row[5]) is 0)
        score.append([tick, note, on_off])
    
    # sort the array by midi tick
    score.sort()
    
    keys = []
    result_str = ''
    for t in range(0, tick+1):
        for note in score:
            if note[0] == t:
                note_chr = chr(note[1] + params.offset)
                if note[2] and note_chr not in keys:
                    keys.append(note_chr)
                if not note[2]:
                    if note_chr in keys:
                        keys.remove(note_chr)
        for key in keys:
            result_str += key
        if not keys:
            result_str += '~'
        result_str += ' '
    return result_str


# convert compressed character-level string into midi file
def decode(string, params):
    make_temp_folder()
    if re.search('.data', string):
        with open(string, encoding='utf-8') as f:
            string = f.read()
    content = string.split(' ')

    if not re.search('.mid', params.output_name):
        params.output_name += '.mid'
    csv_name = os.path.join(temp_path, params.output_name.replace('.mid', '.csv'))
    with open(csv_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        # write the headers required for the midi file
        writer.writerow([0, 0, 'Header', 1, 4, 240])
        writer.writerow([1, 0, 'Start_track'])
        writer.writerow([1, 0, 'Title_t', '"Piano Improvisation - NAI"'])
        
        keys = []
        for t, chap in enumerate(content):        
            if chap is '~':
                continue
            for note in chap:
                if note not in keys:
                    keys.append(note)
                    writer.writerow([1, t * params.sample_rate, 'Note_on_c', 0, ord(note)-params.offset, 107])
            for key in keys:
                if key not in chap:
                    keys.remove(key)
                    writer.writerow([1, t * params.sample_rate, 'Note_off_c', 0, ord(key)-params.offset, 0])
            
        writer.writerow([1, t * params.sample_rate, 'End_track'])
        writer.writerow([0, 0, 'End_of_file'])
    os.system(".\\dependencies\\Csvmidi.exe " + csv_name + " .\\" + params.output_name)
    shutil.rmtree(temp_path)

# prepare the data, convert into compressed character-level string
def preprocess_data():
    make_temp_folder()
    string = ''
    midi_list = list(os.walk(data_path))[0][2]
    for midi in midi_list:
        csv_file = os.path.join(temp_path, midi.replace('.mid', '.csv'))
        os.system(".\\dependencies\\Midicsv.exe "+ os.path.join(data_path, midi) + " .\\" + csv_file)
        with open(csv_file) as f:
            content = list(csv.reader(f, delimiter=','))
        string += encode(content, Params())
    
    with open('.\\train.data', 'w', encoding='utf-8') as f:
        f.write(string)
    shutil.rmtree(temp_path)

