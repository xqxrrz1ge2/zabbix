#####python scripts for converting ITM GSMA AGENTS configurations

########
1. can now process log/network port/process/windows event log


2. Usage:

On windows:
1. open terminal as administrator
2. run C:\zabbix\scripts\python\python.exe read_param.py C:\IBM\ITM\smitools\config
3. Check converted configurations in this directory: C:\zabbix\scripts\

On Linux:
1. run: python3 read_param.py /opt/IBM/ITM/smitools/config
2. Check converted configurations in this directory: /etc/zabbix/scripts/
3. Platforms with no python 3, please use read_param_python2.py instead.
