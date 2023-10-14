#!/bin/bash

function check_os {
    uname | tr '[:lower:]' '[:upper:]'
}

function check_dir {
    local os_type=$(check_os)
    local dir
    if [[ $os_type == 'LINUX' ]] || [[ $os_type == 'UNIX' ]]; then
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
        if [[ -n $tag ]] && [[ $tag != \#* ]]; then
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
        if [[ -n $tag ]] && [[ $tag != \#* ]]; then
            [[ $user == '-' ]] && user=''
            result+=("{\"{#TAG}\":\"$tag\",\"{#PROCESS}\":\"$process\",\"{#USER}\":\"$user\",\"{#COUNT}\":\"$count\",\"{#SEVERITY}\":\"${level^^}\"}")
        fi
    done < $file_path
    IFS=','; echo -n "[${result[*]}]"
}

function main {
    if [[ $1 == 'log' ]]; then
        parse_config_log
    elif [[ $1 == 'process' ]]; then
        parse_config_process
    else
        echo "Usage: $0 log|process"
        exit 1
    fi
}

main $1
