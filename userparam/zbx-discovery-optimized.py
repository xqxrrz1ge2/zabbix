#!/usr/bin/python3

import os
import json
import re
import platform
from abc import ABC, abstractmethod
from typing import List, Dict

class OSHelper:
    @staticmethod
    def get_os_type() -> str:
        return platform.system().upper()
    
    @staticmethod
    def get_scripts_dir() -> str:
        base_dir = "C:/zabbix/scripts" if platform.system().upper() == "WINDOWS" else "/etc/zabbix/scripts"
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

class ConfigParser(ABC):
    def __init__(self, config_file: str, default_content: str):
        self.config_file = config_file
        self.default_content = default_content
    
    def get_config_path(self) -> str:
        return os.path.join(OSHelper.get_scripts_dir(), self.config_file)
    
    def ensure_config_exists(self):
        config_path = self.get_config_path()
        if not os.path.exists(config_path):
            with open(config_path, 'w') as f:
                f.write(self.default_content)
    
    def read_config(self) -> List[Dict]:
        self.ensure_config_exists()
        result = []
        
        with open(self.get_config_path(), 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parsed = self.parse_line(line.strip())
                    if parsed:
                        result.extend(parsed)
        
        return result
    
    @abstractmethod
    def parse_line(self, line: str) -> List[Dict]:
        pass
    
    def output_json(self):
        print(json.dumps(self.read_config()), end="")

class LogParser(ConfigParser):
    def __init__(self):
        super().__init__(
            "zbx_logMonitor.conf",
            "#tag;path;regex_filename;keyword;severity\n"
        )
    
    def parse_line(self, line: str) -> List[Dict]:
        parts = line.split(';')
        if len(parts) != 5:
            return []
            
        tag, path, filename, keyword, level = parts
        result = []
        file_pattern = re.compile(filename)
        
        for root, _, files in os.walk(path):
            for file in files:
                if file_pattern.match(file):
                    result.append({
                        "{#TAG}": tag,
                        "{#PATH}": os.path.join(root, file),
                        "{#KEYWORD}": keyword,
                        "{#SEVERITY}": level.upper()
                    })
                
        return result

class ProcessParser(ConfigParser):
    def __init__(self):
        super().__init__(
            "zbx_processMonitor.conf",
            "#tag;process;user;count;severity\n"
        )
    
    def parse_line(self, line: str) -> List[Dict]:
        tag, process, user, count, level = line.split(';')
        return [{
            '{#TAG}': tag,
            '{#PROCESS}': process,
            '{#USER}': '' if user == '-' else user,
            '{#COUNT}': count,
            '{#SEVERITY}': level.upper()
        }]

class ServiceParser(ConfigParser):
    def __init__(self):
        super().__init__(
            "zbx_serviceMonitor.conf",
            "#tag;service;severity\n"
        )
    
    def parse_line(self, line: str) -> List[Dict]:
        tag, service, level = line.split(';')
        return [{
            '{#TAG}': tag,
            '{#SERVICE}': service,
            '{#SEVERITY}': level.upper()
        }]

class TCPPortParser(ConfigParser):
    def __init__(self):
        super().__init__(
            "zbx_networkMonitor.conf",
            "#tag;hostname;port;severity\n"
        )
    
    def parse_line(self, line: str) -> List[Dict]:
        tag, hostname, port, level = line.split(';')
        return [{
            '{#TAG}': tag,
            '{#HOSTNAME}': hostname,
            '{#PORT}': port,
            '{#SEVERITY}': level.upper()
        }]

class EventLogParser(ConfigParser):
    def __init__(self):
        super().__init__(
            "zbx_eventlogMonitor.conf",
            "#logfile: Application, System, Security\n"
            "#level: Error, Warning, Critical, Information, SuccessAudit, FailureAudit\n"
            "#severity: warning, critical, fatal\n"
            "#tag;logfile;keyword;level;source;eventid;severity\n"
        )
    
    def parse_line(self, line: str) -> List[Dict]:
        tag, logfile, keyword, level, source, eventid, severity = line.split(';')
        return [{
            '{#TAG}': tag,
            '{#LOGFILE}': logfile,
            '{#KEYWORD}': keyword,
            '{#LEVEL}': level.upper(),
            '{#SOURCE}': source,
            '{#EVENTID}': eventid,
            '{#SEVERITY}': severity.upper()
        }]

class CustomScriptParser(ConfigParser):
    def __init__(self):
        super().__init__(
            "zbx_customScriptMonitor.conf",
            "#tag;script;severity\n"
        )
    
    def parse_line(self, line: str) -> List[Dict]:
        tag, command, level = line.split(';')
        return [{
            '{#TAG}': tag,
            '{#SCRIPT}': command,
            '{#SEVERITY}': level.upper()
        }]

class URLParser(ConfigParser):
    def __init__(self):
        super().__init__(
            "zbx_urlMonitor.conf",
            "#tag;url;servername;severity\n"
        )
    
    def parse_line(self, line: str) -> List[Dict]:
        tag, url, servername, level = line.split(';')
        return [{
            '{#TAG}': tag,
            '{#URL}': url,
            '{#SERVERNAME}': servername,
            '{#SEVERITY}': level.upper()
        }]

class FileCountParser(ConfigParser):
    def __init__(self):
        super().__init__(
            "zbx_fileCountMonitor.conf",
            "#tag;path;regex_include;min_threshold;max_threshold;severity\n"
        )
    
    def parse_line(self, line: str) -> List[Dict]:
        tag, path, pattern_include, minthreshold, maxthreshold, level = line.split(';')
        return [{
            '{#TAG}': tag,
            '{#PATH}': path,
            '{#PATTERN}': pattern_include,
            '{#MINTHRESHOLD}': minthreshold,
            '{#MAXTHRESHOLD}': maxthreshold,
            '{#SEVERITY}': level.upper()
        }]

def main():
    import argparse
    
    parsers = {
        'log': LogParser,
        'process': ProcessParser,
        'service': ServiceParser,
        'eventlog': EventLogParser,
        'tcpport': TCPPortParser,
        'customscript': CustomScriptParser,
        'url': URLParser,
        'filecount': FileCountParser
    }
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--conf_type', required=True, 
                       choices=list(parsers.keys()),
                       help="config type: " + "/".join(parsers.keys()))
    
    args = parser.parse_args()
    parser_class = parsers.get(args.conf_type)
    if parser_class:
        parser_class().output_json()
    else:
        parser.print_help()
        exit(1)

if __name__ == '__main__':
    main()
