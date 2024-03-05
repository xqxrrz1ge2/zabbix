import os
import sys
import re

# Check running OS type, return 'Linux' or 'Windows' or 'UNIX'
def check_os():
    import platform
    os_type = platform.system()
    return os_type.upper()

# Check if /etc/zabbix/scripts exists, if not, create it
def check_dir():
    # Check zabbix scripts dir exists according to OS type
    if check_os() == 'LINUX' or check_os() == 'UNIX':
        if not os.path.isdir("/etc/zabbix/scripts"):
            os.mkdir("/etc/zabbix/scripts")
        return "/etc/zabbix/scripts/"
    elif check_os() == 'WINDOWS':
        if not os.path.isdir("C:\\zabbix\\scripts"):
            os.mkdir("C:\\zabbix\\scripts")
        return "C:\\zabbix\\scripts\\"

# Parse log monitor config file
def save_params_to_zabbix(zbx_conf_file, gsma_params):
    scripts_dir = check_dir()
    file_path = scripts_dir + zbx_conf_file
    # Check whether the file exists, create it if not
    with open(file_path, 'a') as file:
        file.write(gsma_params + "\n")

def read_param_files(directory_path):
    """
    Reads and displays the contents of all .param files in the specified directory.
    """
    # Check if the given directory exists
    if not os.path.isdir(directory_path):
        print "The specified directory does not exist."
        return

    # Initialize an empty dictionary to hold the file contents
    file_contents_dict = {}
    
    # List all files in the directory
    files = os.listdir(directory_path)
    
    # Filter out files with .param extension
    param_files = [file for file in files if file.endswith('.param')]
    
    if not param_files:
        print "No .param files found in the directory."
        return
    
    # Read and display the contents of each .param file
    for file_name in param_files:
        file_path = os.path.join(directory_path, file_name)
        key_name = re.sub(r'^[Kk]\d{2}_', '', file_name)
        file_contents_list = []
        with open(file_path, 'r') as file:
            # Should skip lines start with "#"
            for line in file:
                if not line.startswith("#"):
                    file_contents_list.append(line.strip())
                    file_contents_dict[key_name] = file_contents_list

    return file_contents_dict

def convert_gsma_param(directory_path):
    file_contents_dict = read_param_files(directory_path)
    # LogMonitor.param and LogMonitor_detail.param processing
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
        # Replace file alias in LogMonitor_detail.param with file path
        if LogMonitor_detail_contents_lists is not None:
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

    # Process.param processing
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

    # Network.param processing
    network_contents_lists = file_contents_dict.get("network.param")
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

    # EventLog.param processing
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: python script.py <directory_path>"
    else:
        directory_path = sys.argv[1]
        convert_gsma_param(directory_path)
