import json
import os
from os import path
import shutil
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from soup_modifier import modify_soup

with open('config.json', 'r', encoding='utf-8') as fin:
    config = json.load(fin)
for key, value in config.items():
    config[key] = path.expanduser(value)
changes_file = config['changesFile']
input_directory = config['inputDirectory']
output_directory = config['outputDirectory']
if not path.exists(changes_file):
    print('Changes file not found: ' + changes_file)
    exit()
if not path.exists(input_directory):
    print('Input directory not found: ' + input_directory)
    exit()
if output_directory != input_directory:
    shutil.rmtree(output_directory)
    os.makedirs(output_directory)
with open(config['changesFile'], 'r', encoding='utf-8') as fin:
    changesJson = json.load(fin)
    changes = changesJson['changes']
walk = list(os.walk(config['inputDirectory']))
progress_bar = tqdm(walk)
with open('Modified files.txt', 'w', encoding='utf-8') as log:
    for dirpath, dirnames, filenames in progress_bar:
        _, folder = path.split(dirpath)
        if folder != 'Backup':
            progress_bar.set_postfix_str(folder)
            output_subdirectory = dirpath.replace(input_directory, output_directory)
            for filename in filenames:
                text_name, ext = path.splitext(filename)
                if ext == '.xml':
                    fullname = path.join(dirpath, filename)
                    with open(fullname, 'r', encoding='utf-8') as fin:
                        file_text = fin.read()
                    if any(key in file_text for key in changes):
                        soup = BeautifulSoup(file_text, 'lxml')
                        modify_soup(soup, changes)
                        outfile = path.join(output_subdirectory, filename)
                        if not path.exists(output_subdirectory):
                            os.makedirs(output_subdirectory)
                        with open(outfile, 'w', encoding='utf-8') as fout:
                            outfile_text = str(soup)
                            fout.write(outfile_text)
                        log.write(outfile + '\n')






















