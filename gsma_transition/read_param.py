import os
import sys
import re
import platform

#check running OS type, return 'Linux' or 'Windows' or 'UNIX'
def check_os():
    return platform.system().upper()

#check if /etc/zabbix/scripts exists, if not, create it
def check_dir():
    os_type = check_os()
    #check zabbix scripts dir exists according to OS type
    zabbix_dir = "/etc/zabbix/scripts/"
    if os_type == 'WINDOWS':
        zabbix_dir = "C:\\zabbix\\scripts\\"
    os.makedirs(zabbix_dir, exist_ok=True)
    return zabbix_dir

#parse log monitor config file
def save_params_to_zabbix(zbx_conf_file, gsma_params):
    scripts_dir = check_dir()
    file_path = scripts_dir + zbx_conf_file
    #check whether the file exists, create it if not
    with open(file_path, 'a') as file:
        file.write(gsma_params)

def read_param_files(directory_path):
    """
    Reads and displays the contents of all .param files in the specified directory.
    
    :param directory_path: Path to the directory where .param files are located.
    """
    # Check if the given directory exists
    if not os.path.isdir(directory_path):
        print("The specified directory does not exist.")
        return
    
    # List all files in the directory
    files = os.listdir(directory_path)
    
    # Filter out files with .param extension
    param_files = [file for file in files if file.endswith('.param')]
    
    if not param_files:
        print("No .param files found in the directory.")
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

    print(file_contents_dict)
    return file_contents_dict

def append_to_zabbix_confition_file(config_file, content):
    scripts_dir = check_dir()
    file_path = os.path.join(scripts_dir, config_file)
    with open(file_path, 'a') as file:
        file.write(content + '\n')

def convert_gsma_param(directory_path):
    file_contents_dict = read_param_files(directory_path)
    #LogMonitor.param and LogMonitor_detail.param processing
    files_dict = {}
    zbx_contents = ""
    logMonitor_contents_lists = file_contents_dict.get("LogMonitor.param")
    LogMonitor_detail_contents_lists = file_contents_dict.get("LogMonitor_detail.param")
    if logMonitor_contents_lists is not None:
        for file_defines in logMonitor_contents_lists:
            elements = file_defines.split(";")
            file_alias = elements[0]
            file_path = elements[1]
            files_dict[file_alias] = file_path
        #replace file alias in LogMonitor_detail.param with file path
        for detail_line in LogMonitor_detail_contents_lists:
            final_result = []
            elements = detail_line.split(";")
            file_tag = elements[0]
            file_alias = elements[1]
            file_keyword = elements[2]
            file_severity = elements[3]
            file_full_path = files_dict.get(file_alias)
            file_dir, file_name = file_full_path.rsplit(os.sep, 1)
            final_result.append(file_tag)
            final_result.append(file_dir)
            final_result.append(file_name)
            final_result.append(file_keyword)
            final_result.append(file_severity)
            zbx_contents = ";".join(final_result)
            
            save_params_to_zabbix("zbx_logMonitor.conf", zbx_contents)
            save_params_to_zabbix("zbx_logMonitor.conf", '\n')

    #process.param processing
    process_contents_lists = file_contents_dict.get("process.param")
    if process_contents_lists is not None:
        for items in process_contents_lists:
            elements = items.split(";")
            final_result = []
            process_tag = elements[0] + "_" + elements[1]
            process_name = elements[2]
            process_user = elements[3]
            process_count = elements[4]
            process_severity = elements[7]
            if process_severity == "W" or process_severity == "M":
                process_severity = "WARNING"
            elif process_severity == "C":
                process_severity = "CRITICAL"
            elif process_severity == "F":
                process_severity = "FATAL"
            final_result.append(process_tag)
            final_result.append(process_name)
            final_result.append(process_user)
            final_result.append(process_count)
            final_result.append(process_severity) 
            zbx_contents = ";".join(final_result)
            save_params_to_zabbix("zbx_processMonitor.conf", zbx_contents)
            save_params_to_zabbix("zbx_processMonitor.conf", '\n')

    #networkport.param processing
    network_contents_lists = file_contents_dict.get("networkport.param")
    if network_contents_lists is not None:
        for items in network_contents_lists:
            elements = items.split(";")
            final_result = []
            network_tag = elements[0] + "_" + elements[1]
            network_hostname = elements[2]
            network_port = elements[3]
            network_severity = elements[4]
            final_result.append(network_tag)
            final_result.append(network_hostname)
            final_result.append(network_port)
            final_result.append(network_severity)
            zbx_contents = ";".join(final_result)
            save_params_to_zabbix("zbx_networkMonitor.conf", zbx_contents)
            save_params_to_zabbix("zbx_networkMonitor.conf", '\n')

    #EventLog.param processing
    #gsma format
    #MonSol; Logfile; Type/Level; Source; EventCode; User; Severity
    eventlog_contents_lists = file_contents_dict.get("EventLog.param")
    if eventlog_contents_lists is not None:
        for item in eventlog_contents_lists:
            elements = item.split(";")
            final_result = []
            eventlog_tag = elements[0]
            eventlog_logfile = elements[1].replace("=", "")
            eventlog_keyword = ""
            eventlog_level = elements[2]
            eventlog_source = elements[3].replace("=","")
            eventlog_id = elements[4].replace("=", "")
            eventlog_severity = elements[6]
            final_result.append(eventlog_tag)
            final_result.append(eventlog_logfile)
            final_result.append(eventlog_keyword)
            final_result.append(eventlog_level)
            final_result.append(eventlog_source)
            final_result.append(eventlog_id)
            final_result.append(eventlog_severity)
            zbx_contents = ";".join(final_result)
            save_params_to_zabbix("zbx_eventLogMonitor.conf", zbx_contents)
            save_params_to_zabbix("zbx_eventLogMonitor.conf", '\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
    else:
        directory_path = sys.argv[1]
        #print(read_param_files(directory_path))
        convert_gsma_param(directory_path)
