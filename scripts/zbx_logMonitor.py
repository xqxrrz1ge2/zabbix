#!/usr/bin/python3

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'zbx_logMonitor.conf')
TMP_DIR = os.path.join(SCRIPT_DIR, 'tmp')

def get_last_read_position(log_file):
    position_file = os.path.join(TMP_DIR, f'{os.path.basename(log_file)}.pos')
    if os.path.exists(position_file):
        with open(position_file, 'r') as f:
            return int(f.read())
    else:
        return 0

def set_last_read_position(log_file, position):
    position_file = os.path.join(TMP_DIR, f'{os.path.basename(log_file)}.pos')
    with open(position_file, 'w') as f:
        f.write(str(position))

def monitor_logs(log_file, keyword):
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
    last_read_position = get_last_read_position(log_file)
    keyword_found = False
    with open(log_file, 'r') as f:
        if last_read_position > os.path.getsize(log_file):
            last_read_position = 0
        f.seek(last_read_position)
        for line in f:
            if re.search(keyword, line):
                print(f'Keyword "{keyword}" found in {log_file}: {line}', end='')
                keyword_found = True
        set_last_read_position(log_file, f.tell())
    if not keyword_found:
        print('OK')

def read_config_and_monitor():
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            filetag, file_dir, file_name, keyword = line.strip().split(';')
            log_file = os.path.join(file_dir, file_name)
            monitor_logs(log_file, keyword)

if __name__ == '__main__':
    read_config_and_monitor()