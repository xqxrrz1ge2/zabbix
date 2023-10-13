import json

file_path = "/etc/zabbix/scripts/zbx_logMonitor.conf"

result = []

with open(file_path, 'r') as file:
    for line in file:
        if not line.strip() or line.strip().startswith('#'):
            continue

        parts = line.strip().split(';')
        if len(parts) == 4:
            tag, path, keyword, level = parts
            entry = {
                'tag': tag,
                'path': path,
                'keyword': keyword,
                'level': level
            }
            result.append(entry)

json_data = json.dumps(result, indent=4)

print(json_data)
