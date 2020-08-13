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


#oracle_alive
def Connect_Port(sec_ip, value_port):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((sec_ip, value_port))
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return "1"
    except:
        return "0"

#上传数据
def Push_Data(sec_ip, value_port, data_value,metric_name, keys):
    #time.sleep(1)
    info_list = []
    ts = int(time.time())
    #print(ts)
    endpoint = keys + "-" + sec_ip
    value = random.randint(1,100)
    dict_info= {
        "endpoint": endpoint,
        "metric": metric_name,
        "timestamp": ts,
        "step": 60,
        "value":data_value ,
        "counterType": "GAUGE",
        "tags": "Kafka-cluster"
    }
    info_list .append(dict_info)
    requests.post("http://10.10.2.145:1988/v1/push", data=json.dumps(info_list ))

#循环执行列表
def RunAll():
    iniconfig = configparser.ConfigParser()
    iniconfig.read('/data/cluster_monitor/kafka_monitor/kafka_list.ini', encoding='utf-8')
    #读取所有sections项
    sections_ip = iniconfig.sections()
    #print(sections_ip)
    #获取所有key、value
    for sec_ip in sections_ip:
        print("--------------------------")
        print(sec_ip)
        for keys in iniconfig.options(sec_ip):
            #value_name = keys
            value_port = iniconfig.get(sec_ip, keys)
            #print(keys)
            print(value_port)
            #data_value = Mysql_Run_Connection_Info(User, Pass, value_port, sec_ip)
            #print(data_value)
            Push_Data(sec_ip, value_port, Connect_Port(sec_ip, int(value_port)), keys + "_Alive", keys)

if __name__ == '__main__':
    User = "infomn"
    Pass = "infomn"
    RunAll()
