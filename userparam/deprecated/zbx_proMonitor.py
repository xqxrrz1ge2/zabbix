#!/usr/bin/python

import json

file_path = "/etc/zabbix/scripts/zbx_proMonitor.conf"

result = []

with open(file_path, 'r') as file:
    for line in file:
        if not line.strip() or line.strip().startswith('#'):
            continue

        parts = line.strip().split(';')
        if len(parts) == 5:
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

print(json_data)