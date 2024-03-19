#/usr/bin/python
from __future__ import print_function
import os
import json
import re
import argparse
import platform

def ensure_dir(directory):
    """Ensure that the directory exists, create it if necessary."""
    if not os.path.isdir(directory):
        os.makedirs(directory)

def get_scripts_dir():
    """Get the directory for storing scripts based on the OS."""
    if platform.system().upper() == 'WINDOWS':
        dir_path = "C:\\zabbix\\scripts\\"
    else:
        dir_path = "/etc/zabbix/scripts/"
    
    ensure_dir(dir_path)
    return dir_path

def parse_config(file_name, parser_function):
    """General function to parse configuration files."""
    scripts_dir = get_scripts_dir()
    result = []
    file_path = os.path.join(scripts_dir, file_name)
    
    # Ensure the config file exists
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            parser_function(file, initialize=True)
    
    # Process the config file
    with open(file_path, 'r') as file:
        for line in file:
            if not line.strip() or line.strip().startswith("#"):
                continue
            result.extend(parser_function(file,line=line))
    
    print(json.dumps(result), end="")

def parser_log(file, line=None, initialize=False):
    """Parse log monitor configuration."""
    if initialize:
        file.write("#tag;path;regex_filename;keyword;severity\n")
        return []
    
    parts = line.strip().split(';')
    if len(parts) != 5:
        return []
    
    tag, path, filename, keyword, level = parts
    result = []
    filePattern = re.compile(filename)
    for root, _, filenames in os.walk(path):
        for file in filenames:
            if filePattern.match(file):
                result.append({
                    "{#TAG}": tag,
                    "{#PATH}": os.path.join(root, file),
                    "{#KEYWORD}": keyword,
                    "{#SEVERITY}": level.upper()
                })
    return result

def parser_process(file, line=None, initialize=False):
    """Parse process monitor configuration."""
    if initialize:
        file.write("#tag;process;user;count;severity\n")
        return []
    
    parts = line.strip().split(';')
    if len(parts) != 5:
        return []
    
    tag, process, user, count, level = parts
    user = '' if user == '-' else user
    return [{
        '{#TAG}': tag,
        '{#PROCESS}': process,
        '{#USER}': user,
        '{#COUNT}': count,
        '{#SEVERITY}': level.upper()
    }]

# Define additional parsers for service, eventlog, etc., following the pattern of parser_log and parser_process

def parser_service(file, line=None, initialize=False):
    """Parse service monitor configuration."""
    if initialize:
        file.write("#tag;service;severity\n")
        return []
    
    parts = line.strip().split(';')
    if len(parts) != 3:
        return []
    
    tag, service, level = parts
    return [{
        '{#TAG}': tag,
        '{#SERVICE}': service,
        '{#SEVERITY}': level.upper()
    }]

def parser_eventlog(file, line=None, initialize=False):
    """Parse eventlog monitor configuration."""
    if initialize:
        file.write("#tag;logfile;keyword;level;source;eventid;severity\n")
        return []
    
    parts = line.strip().split(';')
    if len(parts) != 7:
        return []
    
    tag, logfile, keyword, level, source, eventid, severity = parts
    return [{
        '{#TAG}': tag,
        '{#LOGFILE}': logfile,
        '{#KEYWORD}': keyword,
        '{#LEVEL}': level.upper(),
        '{#SOURCE}': source,
        '{#EVENTID}': eventid,
        '{#SEVERITY}': severity.upper()
    }]

def parser_tcpport(file, line=None, initialize=False):
    """Parse TCP port monitor configuration."""
    if initialize:
        file.write("#tag;host;port;severity\n")
        return []
    
    parts = line.strip().split(';')
    if len(parts) != 4:
        return []
    
    tag, host, port, level = parts
    return [{
        '{#TAG}': tag,
        '{#HOST}': host,
        '{#PORT}': port,
        '{#SEVERITY}': level.upper()
    }]

def parser_customscript(file, line=None, initialize=False):
    """Parse custom script monitor configuration."""
    if initialize:
        file.write("#tag;script;severity\n")
        return []
    
    parts = line.strip().split(';')
    if len(parts) != 3:
        return []
    
    tag, script, level = parts
    return [{
        '{#TAG}': tag,
        '{#SCRIPT}': script,
        '{#SEVERITY}': level.upper()
    }]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--conf_type', required=True, help="config type: log/process/tcpport/service(windows)/eventlog(windows)/customscript")
    args = parser.parse_args()

    parsers = {
        'log': ('zbx_logMonitor.conf', parser_log),
        'process': ('zbx_processMonitor.conf', parser_process),
        'service': ('zbx_serviceMonitor.conf', parser_service),
        'eventlog': ('zbx_eventlogMonitor.conf', parser_eventlog),
        'tcpport': ('zbx_networkMonitor.conf', parser_tcpport),
        'customscript': ('zbx_customScriptMonitor.conf', parser_customscript),
    }

    if args.conf_type in parsers:
        file_name, parser_function = parsers[args.conf_type]
        parse_config(file_name, parser_function)
    else:
        parser.print_help()
        exit(1)

if __name__ == '__main__':
    main()
