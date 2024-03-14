####
Requirements: 
1. Python 3
2. OS Linux or Windows
3. Runnig agent as root
To override the default user and group for Zabbix agent, run:
    systemctl edit zabbix-agent or systemctl edit zabbix-agent2
Add the following content:
    [Service]
    User=root
    Group=root
Reload daemons and restart the zabbix-agent service:
    systemctl daemon-reload
    systemctl restart zabbix-agent

####
On Windows Platform, use python 3 and zbx_all_in_one.py
Steps:
1. Create C:\zabbix\scripts
2. Download embed python to this folder, link https://www.python.org/ftp/python/3.11.4/python-3.11.4-embed-amd64.zip
3. Exact files to folder: C:\zabbix\scripts\python, you should find python.exe in this folder
4. Get zbx_all_in_one.py into C:\zabbix\scripts
5. Add user params config file in folder C:\zabbix\conf\zabbix_agent2.d:
6. Create userparams.conf
5. Add lines to this file:
    UserParameter=logmondiscover,C:\zabbix\scripts\python\python.exe C:\zabbix\scripts\zbx_all_in_one.py -t log
    UserParameter=processmondiscover,C:\zabbix\scripts\python\python.exe C:\zabbix\scripts\zbx_all_in_one.py -t process
    UserParameter=servicemondiscover,C:\zabbix\scripts\python\python.exe C:\zabbix\scripts\zbx_all_in_one.py -t service
    UserParameter=eventlogmondiscover,C:\zabbix\scripts\python\python.exe C:\zabbix\scripts\zbx_all_in_one.py -t eventlog
7. Restart agent through Windows Service Manager


####
On UNIX or Linux Platform, please use python2 or python3

1. Create directory /etc/zabbix/scripts
2. Get zbx_all_in_one.sh into /etc/zabbix/scripts
3. Add user params config file in dir /etc/zabbix/zabbix_agent2.d or /etc/zabbix/zabbix_agent.d:
4. Create userparams.conf:
    touch userparams.conf
5. Add lines to this file:
    #please use python3 or python3 accordingly
    UserParameter=logmondiscover,python /etc/zabbix/scripts/zbx_all_in_one.py -t log
    UserParameter=processmondiscover,python /etc/zabbix/scripts/zbx_all_in_one.py -t process
    UserParameter=tcpportmondiscover,python /etc/zabbix/scripts/zbx_all_in_one.py -t tcpport
6. Restart agent using systemctl restart zabbix-agent or systemctl restart zabbix-agent2
