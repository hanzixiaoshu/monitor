#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Author:xuanzhong

import requests
import time
import json
import random
import os
import re
import configparser
import math
import socket
import cx_Oracle
import re


#oracle_alive
def Oracle_Status(sec_ip, value_port, keys):
    try:
        conn = cx_Oracle.connect('sys', 'Bus365oracleDB0502', sec_ip + ':' + value_port + '/' + keys, cx_Oracle.SYSDBA)
        cursor = conn.cursor()
        #print(conn)
        sql = 'select status from v$instance'
        result = cursor.execute(sql)
        all_data = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        if str(all_data[0]) == "OPEN":
            print(str(all_data[0]))
            return "1"
        else:
            print("down")
            return "0"
    except:
        return "0"



#Oracl Lock 5s
def Oracle_Lock(sec_ip, value_port, keys):
    try:
        #conn = cx_Oracle.connect('system', 'oracle123', sec_ip + ':1521/' + keys)
        conn = cx_Oracle.connect('system', 'oracle123', sec_ip + ':' + value_port + '/' + keys)
        cursor = conn.cursor()
        sql = 'SELECT COUNT(*) FROM v$sqlarea a, v$session s,v$locked_object l, dba_objects db where s.prev_sql_addr = a.address and l.session_id = s.sid and db.object_id = l.object_id and s.SECONDS_IN_WAIT > 180 order by sid,s.serial#'
        result = cursor.execute(sql)
        all_data = cursor.fetchall()
        cursor.close()
        conn.commit()
        conn.close()
        all_data1 = re.findall("[0-9]", str(all_data))
        all_data2 = "".join(all_data1)
        return all_data2
    except:
        return "-1"

#上传数据
def Push_Data(sec_ip, value_port, data_value,metric_name):
    #time.sleep(1)
    info_list = []
    ts = int(time.time())
    #print(ts)
    endpoint = "OracleCluster-" + sec_ip + ":" + value_port
    value = random.randint(1,100)
    dict_info= {
        "endpoint": endpoint,
        "metric": metric_name,
        "timestamp": ts,
        "step": 60,
        "value":data_value ,
        "counterType": "GAUGE",
        "tags": "Oracle-cluster"
    }
    info_list.append(dict_info)
    requests.post("http://172.200.2.145:1988/v1/push", data=json.dumps(info_list))

#循环执行列表
def RunAll():
    iniconfig = configparser.ConfigParser()
    iniconfig.read('/data/cluster_monitor/oracle_monitor/oracle_list.ini', encoding='utf-8')
    #读取所有sections项
    sections_ip = iniconfig.sections()
    #print(sections_ip)
    #获取所有key、value
    for sec_ip in sections_ip:
        print("--------------------------")
        print(sec_ip)
        for keys in iniconfig.options(sec_ip):
            value_port = iniconfig.get(sec_ip, keys)
            #print(value_port)
            #data_value = Mysql_Run_Connection_Info(User, Pass, value_port, sec_ip)
            #print(data_value)
            Push_Data(sec_ip, value_port, Oracle_Status(sec_ip, value_port, keys),"Oracle_Alive")
            Push_Data(sec_ip, value_port, Oracle_Lock(sec_ip, value_port, keys), "Oracle_Lock")
            #print(Oracle_Lock(sec_ip, value_port, keys))

if __name__ == '__main__':
    RunAll()
