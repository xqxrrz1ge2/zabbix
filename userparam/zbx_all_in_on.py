#/usr/bin/python

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
    if check_os() == 'LINUX':
        if not os.path.isdir("/etc/zabbix/scripts"):
            os.mkdir("/etc/zabbix/scripts")
        return "/etc/zabbix/scripts/"
    elif check_os() == 'WINDOWS':
        if not os.path.isdir("C:\\zabbix\\scripts"):
            os.mkdir("C:\\zabbix\\scripts")
        return "C:\\zabbix\\scripts\\"
    elif check_os() == 'UNIX':
        if not os.path.isdir("/etc/zabbix/scripts"):
            os.mkdir("/etc/zabbix/scripts")
        return "/etc/zabbix/scripts/"

#parse log monitor config file
def parse_config_log():
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
                entry = {
                    "{#TAG}": tag,
                    "{#PATH}": path,
                    "{#KEYWORD}": keyword,
                    "{#LEVEL}": level.upper()
                }
                result.append(entry)

    json_data = json.dumps(result, indent=4)
    print(json_data, end="")


#parse process monitor config file
def parse_config_process():
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
            entry = {
                '{#TAG}': tag,
                '{#PROCESS}': process,
                '{#USER}': user,
                '{#COUNT}': count,
                '{#SEVERITY}': level.upper()
            }
            result.append(entry)

    json_data = json.dumps(result, indent=5)

    print(json_data, end="")

#add arguments support
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--conf_type', help="config type: log or process")
    args = parser.parse_args()

    if args.conf_type == 'log':
        parse_config_log()
    elif args.conf_type == 'process':
        parse_config_process()
    else:
        print("config type error")


if __name__ == '__main__':
    main()
