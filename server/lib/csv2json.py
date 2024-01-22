import csv
import json

sheet = []
infile = '/Users/hadley_king/Downloads/new_participants.csv' 
extension = infile.split('.')[-1]
if extension == 'tsv':
    delimiter='\t'
elif extension == 'csv':
    delimiter=','
with open(infile, 'r', encoding='utf-8') as file:
    data = csv.reader(file, delimiter=delimiter)
    header = next(data)
    print(header)
    for datum in data:
        sheet.append(datum)
data_list = []
for row in sheet:
    line = {}
    for count, item in enumerate(header):
        line[item] = row[count]
    data_list.append(line)
json_list = json.dumps(data_list)

print(json_list)
