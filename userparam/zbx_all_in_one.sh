#!/bin/bash

#check $2 is empty or not
if [ -z $2 ]; then
    severity_param="INFO"; else
    severity_param=$2
fi

function check_os {
    uname | tr '[:lower:]' '[:upper:]'
}

function check_dir {
    local os_type=$(check_os)
    local dir
    if [[ $os_type == 'LINUX' ]] || [[ $os_type == 'AIX' ]] || [[ $os_type == 'SUNOS' ]]; then
        dir="/etc/zabbix/scripts"
    else
        echo "Unsupported OS type: $os_type"
        exit 1
    fi
    if [[ ! -d $dir ]]; then
        mkdir -p $dir
    fi
    echo $dir
}

function parse_config_log {
    local scripts_dir=$(check_dir)
    local file_path="$scripts_dir/zbx_logMonitor.conf"
    if [[ ! -f $file_path ]]; then
        echo "#tag;path;keyword;severity" > $file_path
    fi
    local result=()
    while IFS=';' read -r tag path keyword level; do
        #check severity_param match with severity in config file
        if [[ -n $tag ]] && [[ $tag != \#* ]] && [[ "${severity_param^^}" == "${level^^}" ]]; then
            result+=("{\"{#TAG}\":\"$tag\",\"{#PATH}\":\"$path\",\"{#KEYWORD}\":\"$keyword\",\"{#SEVERITY}\":\"${level^^}\"}")
        fi
    done < $file_path
    IFS=','; echo -n "[${result[*]}]"
}

function parse_config_process {
    local scripts_dir=$(check_dir)
    local file_path="$scripts_dir/zbx_processMonitor.conf"
    if [[ ! -f $file_path ]]; then
        echo "#tag;process;user;count;severity" > $file_path
    fi
    local result=()
    while IFS=';' read -r tag process user count level; do
        if [[ -n $tag ]] && [[ $tag != \#* ]] && [[ "${severity_param^^}" == "${level^^}" ]]; then
            [[ $user == '-' ]] && user=''
            #need to simplify process name, remove path and args
            #temporarily disable this
            #process=$(echo $process | awk -F'/' '{print $NF}' | awk -F' ' '{print $1}')
            result+=("{\"{#TAG}\":\"$tag\",\"{#PROCESS}\":\"$process\",\"{#USER}\":\"$user\",\"{#COUNT}\":\"$count\",\"{#SEVERITY}\":\"${level^^}\"}")
        fi
    done < $file_path
    IFS=','; echo -n "[${result[*]}]"
}

#add function for parse tcp port config
function parse_config_tcpport {
    local scripts_dir=$(check_dir)
    local file_path="$scripts_dir/zbx_tcpportMonitor.conf"
    if [[ ! -f $file_path ]]; then
        echo "#tag;hostname;port;severity" > $file_path
    fi
    local result=()
    while IFS=';' read -r tag hostname port level; do
        if [[ -n $tag ]] && [[ $tag != \#* ]] && [[ "${severity_param^^}" == "${level^^}" ]]; then
            result+=("{\"{#TAG}\":\"$tag\",\"{#HOSTNAME}\":\"$hostname\",\"{#PORT}\":\"$port\",\"{#SEVERITY}\":\"${level^^}\"}")
        fi
    done < $file_path
    IFS=','; echo -n "[${result[*]}]"
}

function main {
    if [[ $1 == 'log' ]]; then
        parse_config_log
    elif [[ $1 == 'process' ]]; then
        parse_config_process
    elif [[ $1 == 'tcpport' ]]; then
        parse_config_tcpport
    else
        echo "Usage: $0 log|process|tcpport"
        exit 1
    fi
}

main $1
