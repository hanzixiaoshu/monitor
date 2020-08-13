#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Author:xuanzhong

import requests
import time
import json
import jsonpath
import random
import os
import re
import configparser
import math

GatewayHost = "http://192.168.3.198:8083"

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
        "step": 10,
        "value":data_value ,
        "counterType": "GAUGE",
        "tags": "Kafka-cluster"
    }
    info_list .append(dict_info)
    requests.post("http://10.10.2.145:1988/v1/push", data=json.dumps(info_list ))

def MmemoryUusedGateWay(sec_ip, value_port):
    Router_requests = "/actuator/metrics/jvm.memory.used"
    headers = {'content-type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    try:
        MmemoryUused_Response = requests.get(url = "http://" + sec_ip + ":" + value_port + Router_requests, headers = headers, timeout = 5)
        MmemoryUused = json.loads(MmemoryUused_Response.text)
        MmemoryUused_Value = jsonpath.jsonpath(MmemoryUused, "$..value")
        MmemoryUused_data = int(float("".join(re.findall("[0-9,.]", str(MmemoryUused_Value))))) / 1024 / 1024
        return MmemoryUused_data
    except:
        return "-1"

def MmemoryMaxGateWay(sec_ip, value_port):
    Router_requests = "/actuator/metrics/jvm.memory.max"
    headers = {'content-type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    try:
        MmemoryMax_Response = requests.get(url = "http://" + sec_ip + ":" + value_port + Router_requests, headers = headers, timeout = 5)
        MmemoryMax = json.loads(MmemoryMax_Response.text)
        MmemoryMax_Value = jsonpath.jsonpath(MmemoryMax, "$..value")
        MmemoryMax_data = int(float("".join(re.findall("[0-9,.]", str(MmemoryMax_Value))))) / 1024 / 1024
        return MmemoryMax_data
    except:
        return "-1"

def SystemCpuUsedGateWay(sec_ip, value_port):
    Router_requests = "/actuator/metrics/system.cpu.usage"
    headers = {'content-type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    try:
        SystemCpuUsed_Response = requests.get(url = "http://" + sec_ip + ":" + value_port + Router_requests, headers = headers, timeout = 5)
        SystemCpuUsed = json.loads(SystemCpuUsed_Response.text)
        SystemCpuUsed_Value = jsonpath.jsonpath(SystemCpuUsed, "$..value")
        SystemCpuUsed_data = "".join(re.findall("[0-9,.]", str(SystemCpuUsed_Value)))
        return SystemCpuUsed_data
    except:
        return "-1"

def QpsGateWay(sec_ip, value_port):
    Router_qps = "/QPS"
    headers = {'content-type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    try:
        response_qps = requests.get(url = "http://" + sec_ip + ":" + value_port + Router_qps, headers = headers, timeout = 5)
        return response_qps.text
    except:
        return "-1"

#循环执行列表
def RunAll():
    iniconfig = configparser.ConfigParser()
    iniconfig.read('/data/cluster_monitor/gateway_monitor/gateway_list.ini', encoding='utf-8')
    #读取所有sections项
    sections_ip = iniconfig.sections()
    #print(sections_ip)
    #获取所有key、value
    for sec_ip in sections_ip:
        print("--------------------------")
        #print(sec_ip)
        for keys in iniconfig.options(sec_ip):
            #value_name = keys
            value_port = iniconfig.get(sec_ip, keys)
            #print(keys)
            #print(value_port)
            #print(data_value)

            #网关jvm内存
            Push_Data(sec_ip, value_port, MmemoryUusedGateWay(sec_ip, value_port), keys + "_MmemoryUused", keys)
            Push_Data(sec_ip, value_port, MmemoryMaxGateWay(sec_ip, value_port), keys + "_MmemoryMax", keys)
            print(MmemoryUusedGateWay(sec_ip, value_port))
            print(MmemoryMaxGateWay(sec_ip, value_port))

            #网关cpu
            Push_Data(sec_ip, value_port, SystemCpuUsedGateWay(sec_ip, value_port), keys + "_SystemCpuUsed", keys)
            print(SystemCpuUsedGateWay(sec_ip, value_port))

            #网关qps
            print(QpsGateWay(sec_ip, value_port))
            Push_Data(sec_ip, value_port, QpsGateWay(sec_ip, value_port), keys + "_Qps", keys)


if __name__ == '__main__':
    RunAll()
