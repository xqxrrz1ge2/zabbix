#!/usr/bin/python3

#####################################
## 09/26/2023, inital
#####################################

import os
import subprocess
import platform

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'zbx_proMonitor.conf')

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--severity', default='INFO', help='severity')
    return parser.parse_args()

# 读取配置文件并解析为字典
def read_config(filename):
    args = parse_args()
    severity_param = args.severity
    config = {}
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            # 忽略以#开头的注释行和空行
            if line.strip() and not line.startswith('#') and (severity_param.lower() in line or severity_param.upper() in line):
                parts = line.strip().split(';')
                if len(parts) == 5:
                    tag, process_name, user, process_count, severity = parts
                    # 如果 process_count 或 user 设置为 "-"，则将其设为 None
                    if process_count == "-":
                        process_count = None
                    else:
                        process_count = int(process_count)
                    if user == "-":
                        user = None
                    config[tag] = {'process_name': process_name, 'user': user, 'process_count': process_count, 'severity': severity}
    return config

# 根据操作系统获取检查进程是否运行的命令
def get_check_command():
    system = platform.system()
    if system in ["Linux", "Unix"]:
        return ['ps', 'aux']
    elif system == "Windows":
        return ['tasklist']
    else:
        raise Exception("Unsupported operating system")

# 检查进程是否运行
def is_process_running(process_name, user, process_count):
    try:
        # 使用不同的命令检查进程是否存在
        command = get_check_command()
        result = subprocess.run(command, stdout=subprocess.PIPE, check=True)
        output = result.stdout.decode('utf-8')  # 将字节流转换为字符串
        lines = output.split('\n')

        matching_processes = [line for line in lines if process_name in line]

        if user:
            matching_processes = [line for line in matching_processes if user in line]

        if process_count is None:
            return len(matching_processes) > 0
        else:
            return len(matching_processes) == process_count
    except subprocess.CalledProcessError:
        return False

def main():
    config = read_config(config_file)
    problem_processes = []
    for tag, info in config.items():
        process_name = info['process_name']
        user = info['user']
        process_count = info['process_count']
        severity = info['severity']
        #convert severity to upper case
        severity = severity.upper()
        if not is_process_running(process_name, user, process_count):
            problem_processes.append(f"{tag} {process_name}")

    if not problem_processes:
        print("OK")
    else:
        print("PROBLEM:"+ severity + ': ' + ','.join(problem_processes) + ", are not running as expected.")

if __name__ == "__main__":
    main()
