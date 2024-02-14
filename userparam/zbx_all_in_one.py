#!/usr/bin/python

import os
import json

#check running OS type, return 'Linux' or 'Windows' or 'UNIX'
def check_os():
    import platform
    os_type = platform.system()
    return os_type.upper()

#check if /etc/zabbix/scripts exists, if not, create it
def check_dir():
    #check zabbix scripts dir exists according to OS type
    if check_os() == 'LINUX' or check_os() == 'UNIX':
        if not os.path.isdir("/etc/zabbix/scripts"):
            os.mkdir("/etc/zabbix/scripts")
        return "/etc/zabbix/scripts/"
    elif check_os() == 'WINDOWS':
        if not os.path.isdir("C:\\zabbix\\scripts"):
            os.mkdir("C:\\zabbix\\scripts")
        return "C:\\zabbix\\scripts\\"

#parse log monitor config file
def parse_config_log(severityparam):
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_logMonitor.conf"
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;path;keyword;severity")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            if len(parts) == 4:
                tag, path, keyword, level = parts
                if level.upper() == severityparam.upper():
                    entry = {
                        "{#TAG}": tag,
                        "{#PATH}": path,
                        "{#KEYWORD}": keyword,
                        "{#SEVERITY}": level.upper()
                    }
                    result.append(entry)
    json_data = json.dumps(result)
    print(json_data, end="")


#parse process monitor config file
def parse_config_process(severityparam):
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_processMonitor.conf"
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;process;user;count;severity")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, process, user, count, level = parts
            if user == '-':
                user = ''
            if level.upper() == severityparam.upper():                
                entry = {
                    '{#TAG}': tag,
                    '{#PROCESS}': process,
                    '{#USER}': user,
                    '{#COUNT}': count,
                    '{#SEVERITY}': level.upper()
                }
                result.append(entry)
    json_data = json.dumps(result)
    print(json_data, end="")

#parse windows service monitor config file
def parse_config_service(severityparam):
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_serviceMonitor.conf"
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;service;severity")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, service, level = parts
            if level.upper() == severityparam.upper():
                entry = {
                    '{#TAG}': tag,
                    '{#SERVICE}': service,
                    '{#SEVERITY}': level.upper()
                }
                result.append(entry)
    json_data = json.dumps(result)
    print(json_data, end="")

#parse windows eventlog monitor config file
def parse_config_eventlog(severityparam):
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_eventlogMonitor.conf"
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#logfile: Application, System, Security")
            file.write("#level: Error, Warning, Critical, Information, SuccessAudit, FailureAudit")
            file.write("#severity: warning, critical, fatal")
            file.write("#tag;logfile;keyword;level;source;eventid;severity")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, logfile, keyword, level, source, eventid, severity = parts
            if severity.upper() == severityparam.upper():
                entry = {
                    '{#TAG}': tag,
                    '{#LOGFILE}': logfile, #Application, System, Security
                    '{#KEYWORD}': keyword,
                    '{#LEVEL}': level.upper(), #Error, Warning, Critical, Information, SuccessAudit, FailureAudit
                    '{#SOURCE}': source, #source of eventlog, found in xml
                    '{#EVENTID}': eventid,
                    '{#SEVERITY}': severity.upper() #warning, critical, fatal
                }
                result.append(entry)
    json_data = json.dumps(result)
    print(json_data, end="")

#add arguments support
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--conf_type', required=True, help="config type: log or process or service(windows) or eventlog(windows)")
    parser.add_argument('-s', '--severity', required=True, help="severity level")
    args = parser.parse_args()

    if args.conf_type == 'log':
        parse_config_log(args.severity)
    elif args.conf_type == 'process':
        parse_config_process(args.severity)
    elif args.conf_type == 'service':
        parse_config_service(args.severity)
    elif args.conf_type == 'eventlog':
        parse_config_eventlog(args.severity)
    else:
        parser.print_help()
        exit(1)

if __name__ == '__main__':
    main()
