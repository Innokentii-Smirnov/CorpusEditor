import json
import os
from os import path
import shutil
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from soup_modifier import SoupModifier
import traceback
from os.path import exists
from os import remove

SKIPPED_FILES = 'skipped_files.txt'
LOG_NAME = 'error_log.txt'

def log_file_skipping(fullname: str) -> None:
  with open(SKIPPED_FILES, 'a', encoding='utf-8') as skipped_files:
    print(fullname, file=skipped_files)

def log_error(message: str) -> None:
  with open(LOG_NAME, 'a', encoding='utf-8') as error_log:
    print(message, file=error_log)

if exists(SKIPPED_FILES):
  remove(SKIPPED_FILES)

if exists(LOG_NAME):
  remove(LOG_NAME)

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
os.makedirs(output_directory, exist_ok=True)
with open(changes_file, 'r', encoding='utf-8') as fin:
    changesJson = json.load(fin)
changes = changesJson['changes']
modifier = SoupModifier(changes)
walk = list(os.walk(config['inputDirectory']))
progress_bar = tqdm(walk)
with (open('Modified files.txt', 'w', encoding='utf-8') as modified_files,
      open('Log.txt', 'w', encoding='utf-8') as log):
    for dirpath, dirnames, filenames in progress_bar:
        _, folder = path.split(dirpath)
        if folder != 'Backup':
            progress_bar.set_postfix_str(folder)
            output_subdirectory = dirpath.replace(input_directory, output_directory)
            for filename in filenames:
                text_name, ext = path.splitext(filename)
                if ext == '.xml':
                  try:
                    outfile = path.join(output_subdirectory, filename)
                    if path.exists(outfile):
                        infile = outfile
                    else:
                        infile = path.join(dirpath, filename)
                    with open(infile, 'r', encoding='utf-8') as fin:
                        file_text = fin.read()
                    soup = BeautifulSoup(file_text, 'xml')
                    modified = modifier(soup, log.write)
                    if modified:
                        os.makedirs(output_subdirectory, exist_ok=True)
                        with open(outfile, 'w', encoding='utf-8') as fout:
                            outfile_text = str(soup)
                            fout.write(outfile_text)
                        modified_files.write('{0:8} {1}\n'.format(folder, text_name))
                  except (KeyError, ValueError) as exc:
                    fullname = path.join(dirpath, filename)
                    log_file_skipping(fullname)
                    log_error(fullname)
                    log_error(traceback.format_exc())





















