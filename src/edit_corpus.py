import json
import os
from os import path
import shutil
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from soup_modifier import SoupModifier
from os.path import exists
from os import remove
from formatter import CustomFormatter
from bs4.dammit import EntitySubstitution
custom_formatter = CustomFormatter(entity_substitution=EntitySubstitution.substitute_xml)

from logging import getLogger, INFO, FileHandler
logger = getLogger(__name__)
logger.setLevel(INFO)
handler = FileHandler('Modified files.txt', 'w', encoding='utf-8')
logger.addHandler(handler)

SKIPPED_FILES = 'skipped_files.txt'
LOG_NAME = 'error_log.txt'

file_skipping_logger = getLogger('file_skipping_logger')
logger.addHandler(FileHandler(SKIPPED_FILES, 'w', encoding='utf-8'))

error_logger = getLogger('error_logger')
logger.addHandler(FileHandler(LOG_NAME, 'w', encoding='utf-8'))

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
for dirpath, dirnames, filenames in progress_bar:
    _, folder = path.split(dirpath)
    if folder != 'Backup':
        progress_bar.set_postfix_str(folder)
        rel_path = path.relpath(dirpath, input_directory)
        output_subdirectory = path.join(output_directory, rel_path)
        for filename in filenames:
            text_name, ext = path.splitext(filename)
            rel_name = path.join(rel_path, text_name)
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
                modified = modifier(soup, rel_name)
                if modified:
                    os.makedirs(output_subdirectory, exist_ok=True)
                    with open(outfile, 'w', encoding='utf-8') as fout:
                        outfile_text = soup.decode(formatter=custom_formatter)
                        fout.write(outfile_text)
                    logger.info('{0:8} {1}'.format(folder, text_name))
              except (KeyError, ValueError):
                fullname = path.join(dirpath, filename)
                file_skipping_logger.error(fullname)
                error_logger.exception(fullname)





















