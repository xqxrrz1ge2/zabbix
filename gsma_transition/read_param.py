import os
import sys
import re

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
def save_params_to_zabbix(zbx_conf_file, gsma_params):
    scripts_dir = check_dir()
    file_path = scripts_dir + zbx_conf_file
    #check whether the file exists, create it if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("#tag;path;regex_filename;keyword;severity")
            file.write(gsma_params)
    else:
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

    # Initialize an empty dictionary to hold the file contents
    file_contents_dict = {}
    
    # List all files in the directory
    files = os.listdir(directory_path)
    
    # Filter out files with .param extension
    param_files = [file for file in files if file.endswith('.param')]
    
    if not param_files:
        print("No .param files found in the directory.")
        return
    
    # Read and display the contents of each .param file
    for file_name in param_files:
        file_path = os.path.join(directory_path, file_name)
        key_name = re.sub(r'^[Kk]\d{2}_', '', file_name)
        file_contents_list = []
        with open(file_path, 'r') as file:
            #should skip lines start with "#"
            for line in file:
                if not line.startswith("#"):
                    file_contents_list.append(line.strip())
                    file_contents_dict[key_name] = file_contents_list

    return file_contents_dict


def convert_gsma_param(directory_path):
    file_contents_dict = read_param_files(directory_path)
    #LogMonitor.param and LogMonitor_detail.param processing
    files_dict = {}
    logMonitor_contents_lists = file_contents_dict.get("LogMonitor.param")
    LogMonitor_detail_contents_lists = file_contents_dict.get("LogMonitor_detail.param")
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
        zbx_logMonitor_lines = ";".join(final_result)
        save_params_to_zabbix("zbx_logMonitor.conf", zbx_logMonitor_lines)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
    else:
        directory_path = sys.argv[1]
        #print(read_param_files(directory_path))
        convert_gsma_param(directory_path)
