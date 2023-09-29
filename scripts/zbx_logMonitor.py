#!/usr/bin/python3

#####################################
## 09/26/2023, inital
#####################################

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'zbx_logMonitor.conf')
TMP_DIR = os.path.join(SCRIPT_DIR, 'tmp')

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--severity', default='INFO', help='severity')
    return parser.parse_args()

def get_last_read_position(log_file):
    args = parse_args()
    severity_param = args.severity
    position_file = os.path.join(TMP_DIR, f'{os.path.basename(log_file)}.{severity_param}.pos')
    if os.path.exists(position_file):
        with open(position_file, 'r') as f:
            return int(f.read())
    else:
        return 0

def set_last_read_position(log_file, position):
    args = parse_args()
    severity_param = args.severity
    position_file = os.path.join(TMP_DIR, f'{os.path.basename(log_file)}.{severity_param}.pos')
    with open(position_file, 'w') as f:
        f.write(str(position))

def monitor_logs(filetag, log_file, keyword, severity):
    # convert severity to upper case
    severity = severity.upper()
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
                print(f'PROBLEM:{severity}:{filetag}:Keyword "{keyword}" found in {log_file}: {line}', end='')
                keyword_found = True
        set_last_read_position(log_file, f.tell())
    if not keyword_found:
        print('OK')

def read_config_and_monitor():
    args = parse_args()
    severity_param = args.severity
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            filetag, file_dir, file_name, keyword, severity = line.strip().split(';')
            #check severity_param with severity, convert them to lower case first
            if severity_param.lower() == severity.lower():
                log_file = os.path.join(file_dir, file_name)
                monitor_logs(filetag, log_file, keyword, severity)

if __name__ == '__main__':
    read_config_and_monitor()
