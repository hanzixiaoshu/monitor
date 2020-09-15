#!/usr/bin/env python


import requests
import time
import json
import random
import os
import re
import pymysql
import configparser
import math
import socket
import threading
import datetime

#当前连接数
def Mysql_Run_Connection_Info(User, Pass, value_port, sec_ip):
   def Mysql_Run_Connection_Out(User, Pass, value_port, sec_ip):
       return os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show full processlist' 2>/dev/null | wc -l").read()
   return Mysql_Run_Connection_Out(User, Pass, value_port, sec_ip).replace("\n","").lstrip()

#总连接数
def Mysql_Total_Connection_Info(User, Pass, value_port, sec_ip):
    def Mysql_Total_Connection_Out(User, Pass, value_port, sec_ip):
        return os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show variables like \"max_connections\"' 2>/dev/null | grep 'max_connections' | awk -F ' ' '{print $2}'").read()
    return Mysql_Total_Connection_Out(User, Pass, value_port, sec_ip).replace("\n","").lstrip()

#innodb_buffer_pool_size配置大小
def Mysql_Innodb_Buffer_Pool_Size_Info(User, Pass, value_port, sec_ip):
    def Mysql_Innodb_Buffer_Pool_Size_Out(User, Pass, value_port, sec_ip):
        return os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show global variables like \"innodb_buffer_pool_size\"' 2>/dev/null | grep innodb_buffer_pool_size | awk -F ' ' '{print $2}'").read()
    Size = Mysql_Innodb_Buffer_Pool_Size_Out(User, Pass, value_port, sec_ip).replace("\n","").lstrip()
    try:
        Size_num = int(Size)/1024/1024/1024
        return  Size_num
    except:
        return "0"

#innodb_buffer_pool_size建议配置大小
def Mysql_Innodb_Buffer_Pool_Size_Proposal(User, Pass, value_port, sec_ip):
    def Innodb_Buffer_Pool_Pages_Data_Out(User, Pass, value_port, sec_ip):
        return os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show global status like \"Innodb_buffer_pool_pages_data\"' 2>/dev/null | grep Innodb_buffer_pool_pages_data | awk -F ' ' '{print $2}'").read()
    def Innodb_Page_Size_Out(User, Pass, value_port, sec_ip):
        return os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show global status like \"Innodb_page_size\"' 2>/dev/null | grep Innodb_page_size | awk -F ' ' '{print $2}'").read()
    num1 = Innodb_Buffer_Pool_Pages_Data_Out(User, Pass, value_port, sec_ip).replace("\n","").lstrip()
    num2 = Innodb_Page_Size_Out(User, Pass, value_port, sec_ip).replace("\n","").lstrip()
    try:
        numall = int(num1) * int(num2) * 1.05 / (1024 * 1024 * 1024)
        return  math.ceil(numall)
    except:
        return "0"

#主从同步
def Mysql_Sync_Status(User, Pass, value_port, sec_ip):
    Slave_IO_State = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show slave status\G' 2>/dev/null | grep 'Slave_IO_State'").read()
    if Slave_IO_State != '':
        Slave_IO_Running = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show slave status\G' 2>/dev/null | grep -w 'Slave_IO_Running' | awk -F ' ' '{print $2}'").read()
        Slave_SQL_Running = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show slave status\G' 2>/dev/null | grep -w 'Slave_SQL_Running' | awk -F ' ' '{print $2}'").read()
        if Slave_IO_Running.replace("\n","").lstrip() == 'Yes':
            if Slave_SQL_Running.replace("\n","").lstrip() == 'Yes':
                return '1'
            else:
                return '0'
        else:
            return '0'
    else:
        return '-1'

#同步延时
def Mysql_Seconds_Behind(User, Pass, value_port, sec_ip):
    Seconds_Behind_State = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show slave status\G' 2>/dev/null | grep 'Seconds_Behind_Master'").read()
    if Seconds_Behind_State != '':
        Seconds_Behind_Master = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show slave status\G' 2>/dev/null | grep -w 'Seconds_Behind_Master' | awk -F ' ' '{print $2}'").read()
        return Seconds_Behind_Master.replace("\n","").lstrip()
    else:
        return '-1'

#mysql_alive
def Connect_Port(sec_ip, value_port):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((sec_ip, value_port))
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return "1"
    except:
        return "0"

#mysql TRX num , run time > 30s
def Mysql_TRX_Num(User, Pass, value_port, sec_ip):
    def Mysql_TRX_Num_Out(User, Pass, value_port, sec_ip):
        return os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'select now() as nowtime, (UNIX_TIMESTAMP(now()) - UNIX_TIMESTAMP(a.trx_started)) as sqlruntime, b.id, b.user, b.host, b.db, d.SQL_TEXT from information_schema.innodb_trx a inner join information_schema.PROCESSLIST b on a.TRX_MYSQL_THREAD_ID=b.id and b.COMMAND<>\"Binlog Dump\" inner join performance_schema.threads c ON b.id = c.PROCESSLIST_ID inner join performance_schema.events_statements_current d ON d.THREAD_ID = c.THREAD_ID where (UNIX_TIMESTAMP(now()) - UNIX_TIMESTAMP(a.trx_started)) > 30 \G' 2>/dev/null | grep 'sqlruntime' | wc -l").read()
    return Mysql_TRX_Num_Out(User, Pass, value_port, sec_ip).replace("\n","").lstrip()

#Mysql_Locks
def Mysql_Locks_Info(User, Pass, value_port, sec_ip):
    def Mysql_Locks_Out(User, Pass, value_port, sec_ip):
        return os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'select * from information_schema.INNODB_LOCKS' 2>/dev/null | wc -l").read()
    return Mysql_Locks_Out(User, Pass, value_port, sec_ip).replace("\n","").lstrip()

#Mysql_Lock_Waits
def Mysql_Locks_Waits_Info(User, Pass, value_port, sec_ip):
    def Mysql_Locks_Waits_Out(User, Pass, value_port, sec_ip):
        return os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'select * from information_schema.INNODB_LOCK_WAITS' 2>/dev/null | wc -l").read()
    return Mysql_Locks_Waits_Out(User, Pass, value_port, sec_ip).replace("\n","").lstrip()

#mysql sync lock
def Mysql_SyncLock(User, Pass, value_port, sec_ip):
   def Mysql_SyncLock_Out(User, Pass, value_port, sec_ip):
       return os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show full processlist' 2>/dev/null | grep 'Waiting for commit lock' | wc -l").read()
   return Mysql_SyncLock_Out(User, Pass, value_port, sec_ip).replace("\n","").lstrip()

#mysql qps
def Mysql_QPS(User, Pass, value_port, sec_ip):
    Start_Time = datetime.datetime.now()
    First_Query = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show global status like \"Question%\"' 2>/dev/null | sed -n 2p | awk '{print $2}'").read().replace("\n","").lstrip()
    Second_Query = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show global status like \"Question%\"' 2>/dev/null | sed -n 2p | awk '{print $2}'").read().replace("\n","").lstrip()
    time.sleep(1)
    End_Time = datetime.datetime.now()
    difftime = (End_Time - Start_Time).seconds
    return (int(Second_Query) - int(First_Query))/int(difftime)
#mysql tps
def Mysql_TPS(User, Pass, value_port, sec_ip):
    Start_Time = datetime.datetime.now()
    First_Commit = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show global status like \"Com_commit\"' 2>/dev/null | sed -n 2p | awk '{print $2}'").read().replace("\n","").lstrip()
    Second_Commit = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show global status like \"Com_commit\"' 2>/dev/null | sed -n 2p | awk '{print $2}'").read().replace("\n","").lstrip()
    First_Rollback = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show global status like \"Com_rollback\"' 2>/dev/null | sed -n 2p | awk '{print $2}'").read().replace("\n","").lstrip()
    Second_Rollback = os.popen("mysql -u" + User + " -p" + Pass + " -P" + value_port + " -h" + sec_ip + " -e 'show global status like \"Com_rollback\"' 2>/dev/null | sed -n 2p | awk '{print $2}'").read().replace("\n","").lstrip()
    time.sleep(1)
    End_Time = datetime.datetime.now()
    difftime = (End_Time - Start_Time).seconds
    Com_commit = int(Second_Commit) - int(First_Commit)
    Com_rollback = int(Second_Rollback) - int(First_Rollback)
    return (int(Com_commit) + int(Com_rollback))/int(difftime)



#上传数据
def Mysql_Push_Data(sec_ip, value_port, data_value,metric_name):
    #time.sleep(1)
    info_list = []
    ts = int(time.time())
    #print(ts)
    endpoint = "MysqlCluster-" + sec_ip + ":" + value_port
    value = random.randint(1,100)
    dict_info= {
        "endpoint": endpoint,
        "metric": metric_name,
        "timestamp": ts,
        "step": 60,
        "value":data_value ,
        "counterType": "GAUGE",
        "tags": "Mysql-cluster",
    }
    info_list.append(dict_info)
    requests.post("http://192.168.2.145:1988/v1/push", data=json.dumps(info_list ))

#循环执行列表
def RunAll(sec_ip):
    iniconfig = configparser.ConfigParser()
    iniconfig.read('/data/cluster_monitor/mysql_monitor/mysql_list.ini', encoding='utf-8')
#    #读取所有sections项
#    sections_ip = iniconfig.sections()
    #获取所有key、value
    #for sec_ip in sections_ip:
    #    print("--------------------------")
    #    print(sec_ip)
    for keys in iniconfig.options(sec_ip):
        value_port = iniconfig.get(sec_ip, keys)
        print(value_port)
        #data_value = Mysql_Run_Connection_Info(User, Pass, value_port, sec_ip)
        #print(data_value)
        Mysql_Push_Data(sec_ip, value_port, Connect_Port(sec_ip, int(value_port)),"Mysql_Alive")
        Mysql_Push_Data(sec_ip, value_port, Mysql_SyncLock(User, Pass, value_port, sec_ip), "Mysql_SyncLock")
        Mysql_Push_Data(sec_ip, value_port, Mysql_Run_Connection_Info(User, Pass, value_port, sec_ip),"Mysql_Run_Connection")
        Mysql_Push_Data(sec_ip, value_port, Mysql_Total_Connection_Info(User, Pass, value_port, sec_ip),"Mysql_Total_Connection")
        Mysql_Push_Data(sec_ip, value_port, Mysql_Innodb_Buffer_Pool_Size_Info(User, Pass, value_port, sec_ip),"Mysql_Innodb_Buffer_Pool_Size")
        Mysql_Push_Data(sec_ip, value_port, Mysql_Innodb_Buffer_Pool_Size_Proposal(User, Pass, value_port, sec_ip),"Mysql_Innodb_Buffer_Pool_Size_Proposal")
        Mysql_Push_Data(sec_ip, value_port, Mysql_Sync_Status(User, Pass, value_port, sec_ip),"Mysql_Sync_Status")
        Mysql_Push_Data(sec_ip, value_port, Mysql_Seconds_Behind(User, Pass, value_port, sec_ip), "Mysql_Seconds_Behind")
        Mysql_Push_Data(sec_ip, value_port, Mysql_TRX_Num(User, Pass, value_port, sec_ip),"Mysql_TRX_Num")
        Mysql_Push_Data(sec_ip, value_port, Mysql_Locks_Info(User, Pass, value_port, sec_ip), "Mysql_Locks")
        Mysql_Push_Data(sec_ip, value_port, Mysql_Locks_Waits_Info(User, Pass, value_port, sec_ip), "Mysql_Locks_Waits")
        Mysql_Push_Data(sec_ip, value_port, Mysql_QPS(User, Pass, value_port, sec_ip), "Mysql_QPS")
        Mysql_Push_Data(sec_ip, value_port, Mysql_TPS(User, Pass, value_port, sec_ip), "Mysql_TPS")

if __name__ == '__main__':
    User = "user"
    Pass = "pass"
    #RunAll("192.168.1.17")
    thread1 = threading.Thread(target=RunAll, args=("192.168.1.17",))
    thread2 = threading.Thread(target=RunAll, args=("192.168.1.20",))
    thread3 = threading.Thread(target=RunAll, args=("192.168.1.21",))
    thread4 = threading.Thread(target=RunAll, args=("192.168.1.19",))
    thread5 = threading.Thread(target=RunAll, args=("192.168.2.18",))
    thread6 = threading.Thread(target=RunAll, args=("192.168.2.19",))
    thread7 = threading.Thread(target=RunAll, args=("192.168.2.29",))
    thread8 = threading.Thread(target=RunAll, args=("192.168.2.31",))
    thread9 = threading.Thread(target=RunAll, args=("192.168.2.35",))
    thread10 = threading.Thread(target=RunAll, args=("192.168.2.36",))
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()
    thread7.start()
    thread8.start()
    thread9.start()
    thread10.start()
