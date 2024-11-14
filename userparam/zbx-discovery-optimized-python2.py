#!/usr/bin/env python
from __future__ import print_function
import os
import json
import re
import argparse
import platform
from collections import defaultdict

class ConfigParser(object):
    """Base class for parsing configuration files."""
    def __init__(self, template, required_fields):
        self.template = template
        self.required_fields = required_fields

    def parse(self, line):
        """Parse a single line of configuration."""
        parts = line.strip().split(';')
        if len(parts) != len(self.required_fields):
            return []
        return [dict(zip(self.required_fields, parts))]

    def initialize(self, file_obj):
        """Initialize configuration file with template."""
        file_obj.write(self.template)
        return []

class LogParser(ConfigParser):
    """Parser for log monitoring configuration."""
    def __init__(self):
        template = "#tag;path;regex_filename;keyword;severity\n"
        fields = ['{#TAG}', '{#PATH}', '{#FILENAME}', '{#KEYWORD}', '{#SEVERITY}']
        super(LogParser, self).__init__(template, fields)

    def parse(self, line):
        parts = line.strip().split(';')
        if len(parts) != 5:
            return []
        
        tag, path, filename, keyword, level = parts
        result = []
        try:
            filePattern = re.compile(filename)
            for root, _, filenames in os.walk(path):
                for fname in filenames:
                    if filePattern.match(fname):
                        result.append({
                            "{#TAG}": tag,
                            "{#PATH}": os.path.join(root, fname),
                            "{#KEYWORD}": keyword,
                            "{#SEVERITY}": level.upper()
                        })
        except re.error:
            return []
        return result

class ProcessParser(ConfigParser):
    def __init__(self):
        template = "#tag;process;user;count;severity\n"
        fields = ['{#TAG}', '{#PROCESS}', '{#USER}', '{#COUNT}', '{#SEVERITY}']
        super(ProcessParser, self).__init__(template, fields)

    def parse(self, line):
        records = super(ProcessParser, self).parse(line)
        if records:
            record = records[0]
            record['{#USER}'] = '' if record['{#USER}'] == '-' else record['{#USER}']
            record['{#SEVERITY}'] = record['{#SEVERITY}'].upper()
        return records

def get_scripts_dir():
    """Get the directory for storing scripts based on the OS."""
    is_windows = platform.system().upper() == 'WINDOWS'
    dir_path = "C:\\zabbix\\scripts\\" if is_windows else "/etc/zabbix/scripts/"
    
    if not os.path.isdir(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError:
            dir_path = os.path.expanduser('~/zabbix/scripts/')
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
    return dir_path

def parse_config(file_name, parser):
    """General function to parse configuration files."""
    scripts_dir = get_scripts_dir()
    result = []
    file_path = os.path.join(scripts_dir, file_name)
    
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            parser.initialize(f)
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            result.extend(parser.parse(line))
    
    print(json.dumps(result), end='')

def main():
    parsers = {
        'log': (LogParser(), 'zbx_logMonitor.conf'),
        'process': (ProcessParser(), 'zbx_processMonitor.conf'),
        # Add other parsers as needed
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--conf_type', required=True, 
                       choices=parsers.keys(),
                       help="Configuration type to parse")
    
    args = parser.parse_args()
    config_parser, file_name = parsers[args.conf_type]
    parse_config(file_name, config_parser)

if __name__ == '__main__':
    main()
