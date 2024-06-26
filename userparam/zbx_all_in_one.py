#!/usr/bin/python3

import os
import json
import re

#check running OS type, return 'Linux' or 'Windows' or 'UNIX'
def check_os():
    import platform
    os_type = platform.system()
    return os_type.upper()

#check if /etc/zabbix/scripts exists, if not, create it
def check_dir():
    os_type = check_os()
    #check zabbix scripts dir exists according to OS type
    if check_os() == 'WINDOWS':
        if not os.path.isdir("C:\\zabbix\\scripts"):
            os.mkdir("C:\\zabbix\\scripts")
        return "C:\\zabbix\\scripts\\"
    else:
        return "/etc/zabbix/scripts/"

#parse log monitor config file
def parse_config_log():
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_logMonitor.conf"
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;path;regex_filename;keyword;severity\n")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            if len(parts) == 5:
                tag, path, filename, keyword, level = parts
                #find all files which matches filename regex pattern in the path
                files = []
                filePattern = re.compile(filename)
                for root, dirs, filenames in os.walk(path):
                    for file in filenames:
                        if filePattern.match(file):
                            files.append(os.path.join(root, file))
                for file in files:
                    entry = {
                        "{#TAG}": tag,
                        "{#PATH}": file,
                        "{#KEYWORD}": keyword,
                        "{#SEVERITY}": level.upper()
                    }
                    result.append(entry)

    json_data = json.dumps(result)
    print(json_data, end="")


#parse process monitor config file
def parse_config_process():
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_processMonitor.conf"
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;process;user;count;severity\n")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, process, user, count, level = parts
            if user == '-':
                user = ''
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
def parse_config_service():
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_serviceMonitor.conf"
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;service;severity\n")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, service, level = parts
            entry = {
                '{#TAG}': tag,
                '{#SERVICE}': service,
                '{#SEVERITY}': level.upper()
            }
            result.append(entry)

    json_data = json.dumps(result)

    print(json_data, end="")

#parse windows tcp port monitor config file
def parse_config_tcpport():
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_networkMonitor.conf"
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;hostname;port;severity\n")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, hostname, port, level = parts
            entry = {
                '{#TAG}': tag,
                '{#HOSTNAME}': hostname,
                '{#PORT}': port,
                '{#SEVERITY}': level.upper()
            }
            result.append(entry)

    json_data = json.dumps(result)

    print(json_data, end="")

#parse windows eventlog monitor config file
def parse_config_eventlog():
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_eventlogMonitor.conf"
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#logfile: Application, System, Security\n")
            file.write("#level: Error, Warning, Critical, Information, SuccessAudit, FailureAudit\n")
            file.write("#severity: warning, critical, fatal\n")
            file.write("#tag;logfile;keyword;level;source;eventid;severity\n")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, logfile, keyword, level, source, eventid, severity = parts
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

def parse_config_customscript():
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_customScriptMonitor.conf"
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;script;severity\n")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, command, level = parts
            entry = {
                '{#TAG}': tag,
                '{#SCRIPT}': command,
                '{#SEVERITY}': level.upper()
            }
            result.append(entry)

    json_data = json.dumps(result)

    print(json_data, end="")

def parse_config_url():
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_urlMonitor.conf"
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;url;servername;severity\n")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, url, servername, level = parts
            entry = {
                '{#TAG}': tag,
                '{#URL}': url,
                '{#SERVERNAME}': servername,
                '{#SEVERITY}': level.upper()
            }
            result.append(entry)

    json_data = json.dumps(result)

    print(json_data, end="")

##add directory files count monitor support
##2024-04-29
def parse_config_fileCount():
    scripts_dir = check_dir()
    result = []
    file_path = scripts_dir + "zbx_fileCountMonitor.conf"
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;path;regex_include;min_threshold;max_threshold;severity\n")
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue

            parts = line.strip().split(';')
            tag, path, pattern_include, minthreshold, maxthreshold, level = parts
            entry = {
                '{#TAG}': tag,
                '{#PATH}': path,
                '{#PATTERN}': pattern_include,
                '{#MINTHRESHOLD}': minthreshold,
                '{#MAXTHRESHOLD}': maxthreshold,
                '{#SEVERITY}': level.upper()
            }
            result.append(entry)

    json_data = json.dumps(result)

    print(json_data, end="")

#add arguments support
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--conf_type', required=True, help="config type: log/process/tcpport/service(windows)/eventlog(windows)/customscript/url/filecount")
    args = parser.parse_args()

    if args.conf_type == 'log':
        parse_config_log()
    elif args.conf_type == 'process':
        parse_config_process()
    elif args.conf_type == 'service':
        parse_config_service()
    elif args.conf_type == 'eventlog':
        parse_config_eventlog()
    elif args.conf_type == 'tcpport':
        parse_config_tcpport()
    elif args.conf_type == 'customscript':
        parse_config_customscript()
    elif args.conf_type == 'url':
        parse_config_url()
    elif args.conf_type == 'filecount':
        parse_config_fileCount()
    else:
        parser.print_help()
        exit(1)

if __name__ == '__main__':
    main()
