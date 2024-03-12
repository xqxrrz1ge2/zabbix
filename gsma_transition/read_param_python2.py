import os
import re
import platform
import argparse

# check running OS type, return 'Linux' or 'Windows' or 'UNIX'
def check_os():
    return platform.system().upper()

# check if /etc/zabbix/scripts exists, if not, create it
def check_dir():
    os_type = check_os()
    # check zabbix scripts dir exists according to OS type
    zabbix_dir = "/etc/zabbix/scripts/"
    if os_type == 'WINDOWS':
        zabbix_dir = "C:\\zabbix\\scripts\\"
    if not os.path.exists(zabbix_dir):
        os.makedirs(zabbix_dir)
    return zabbix_dir

def read_param_files(directory_path):
    """
    Reads and displays the contents of all .param files in the specified directory.
    
    :param directory_path: Path to the directory where .param files are located.
    """
    # Check if the given directory exists
    if not os.path.isdir(directory_path):
        print "The specified directory does not exist."
        return
    
    # List all files in the directory
    files = os.listdir(directory_path)
    
    # Filter out files with .param extension
    param_files = [file for file in files if file.endswith('.param')]
    
    if not param_files:
        print "No .param files found in the directory."
        return

    key_name_pattern = re.compile(r'^[Kk]\d{2}_')
    # Initialize an empty dictionary to hold the file contents
    file_contents_dict = {}
    # Read and display the contents of each .param file
    for file_name in param_files:
        key_name = key_name_pattern.sub('', file_name)
        with open(os.path.join(directory_path, file_name), 'r') as file:
            contents = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            if contents:
                file_contents_dict[key_name] = contents

    print file_contents_dict
    return file_contents_dict

def append_to_zabbix_configration_file(config_file, content):
    scripts_dir = check_dir()
    file_path = os.path.join(scripts_dir, config_file)
    with open(file_path, 'a') as file:
        file.write(content + '\n')

def process_log_monitor_params(gsma_params_contents_dict):
    logMonitor_contents_lists = gsma_params_contents_dict.get("LogMonitor.param")
    LogMonitor_detail_contents_lists = gsma_params_contents_dict.get("LogMonitor_detail.param")
    files_dict = {}
    for file_defines in logMonitor_contents_lists:
        elements = file_defines.split(";")
        file_alias, file_path = elements[0], elements[1]
        files_dict[file_alias] = file_path
    # replace file alias in LogMonitor_detail.param with file path
    for detail_line in LogMonitor_detail_contents_lists:
        elements = detail_line.split(";")
        file_tag, file_alias, file_keyword, file_severity = elements[0], elements[1], elements[2], elements[3]
        file_full_path = files_dict.get(file_alias)
        file_dir, file_name = file_full_path.rsplit(os.sep, 1)
        final_result = ";".join([file_tag, file_dir, file_name, file_keyword, file_severity])
        append_to_zabbix_configration_file("zbx_logMonitor.conf", final_result)

def process_process_params(gsma_params_contents_dict):
    process_contents_lists = gsma_params_contents_dict.get("process.param")
    for items in process_contents_lists:
        elements = items.split(";")
        process_tag, process_name, process_user, process_count, process_severity = elements[0] + "_" + elements[1], elements[2], elements[3], elements[4], elements[7]
        if process_severity == "W" or process_severity == "M":
            process_severity = "WARNING"
        elif process_severity == "C":
            process_severity = "CRITICAL"
        elif process_severity == "F":
            process_severity = "FATAL"
        final_result = ";".join([process_tag, process_name, process_user, process_count, process_severity])
        append_to_zabbix_configration_file("zbx_processMonitor.conf", final_result)

def process_network_port_params(gsma_params_contents_dict):
    os_type = check_os()
    param_file_name = "networkport.param"
    if os_type == 'WINDOWS':
        param_file_name = "PortCheck.param"
        network_contents_lists = gsma_params_contents_dict.get(param_file_name)
        for item in network_contents_lists:
            # item format sample: mssql;ESMAPPP1;1433
            elements = item.split(";")
            network_tag, network_hostname, network_port = elements[0], elements[1], elements[2]
    else:
        network_contents_lists = gsma_params_contents_dict.get(param_file_name)
        for item in network_contents_lists:
            #unix-like item format sample: oracle;;10.10.170.52;8020
            elements = item.split(";")
            network_tag, network_hostname, network_port = elements[0] + "_" + elements[1], elements[2], elements[3]
    final_result = ";".join([network_tag, network_hostname, network_port, "CRITICAL"])
    append_to_zabbix_configration_file("zbx_networkMonitor.conf", final_result)

def process_event_log_params(gsma_params_contents_dict):
    eventlog_contents_lists = gsma_params_contents_dict.get("EventLog.param")
    for item in eventlog_contents_lists:
        elements = item.split(";")
        eventlog_tag, eventlog_logfile, eventlog_keyword, eventlog_level, eventlog_source, eventlog_id, eventlog_severity = elements[0], elements[1].replace("=", ""), "", elements[2], elements[3].replace("=",""), elements[4].replace("=", ""), elements[6]
        final_result = ";".join([eventlog_tag, eventlog_logfile, eventlog_keyword, eventlog_level, eventlog_source, eventlog_id, eventlog_severity])
        append_to_zabbix_configration_file("zbx_eventLogMonitor.conf", final_result)

def convert_gsma_param(directory_path):
    gsma_params_contents_dict = read_param_files(directory_path)
    # process each parameter type
    if "LogMonitor.param" in gsma_params_contents_dict and "LogMonitor_detail.param" in gsma_params_contents_dict:
        process_log_monitor_params(gsma_params_contents_dict)
    
    if "process.param" in gsma_params_contents_dict:
        process_process_params(gsma_params_contents_dict)

    if "networkport.param" in gsma_params_contents_dict or "PortCheck.param" in gsma_params_contents_dict:
        process_network_port_params(gsma_params_contents_dict)
    
    if "EventLog.param" in gsma_params_contents_dict:
        process_event_log_params(gsma_params_contents_dict)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process GSMA parameters and save to Zabbix configuration.")
    parser.add_argument("directory_path", help="Path to the directory containing .param files")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()
    directory_path = args.directory_path
    convert_gsma_param(directory_path)
