#!/usr/bin/env python
#--*--encoding:utf8--*--

import os
import sys
import time
import random
import requests
import json
import socket

"""
jstat -gccapacity pid
jstat -gc pid

NGC：当前新生代容量
OGC：当前老年代大小
YGC：年轻代gc次数
FGC：老年代GC次数
EC：伊甸园区的大小
EU：伊甸园区的使用大小
OC：老年代大小
OU：老年代使用大小
OGCMN：老年代最小容量
OGCMX：老年代最大容量
NGCMN：新生代最小容量
NGCMX：新生代最大容量
S0U：第一个幸存区的使用大小
S1U：第二个幸存区的使用大小
S0C：第一个幸存区大小
S1C：第二个幸存区的大小
"""
#os.getenv('PYTH')

class Jstat_Monitor_Indexes(object):
    def __init__(self, jstat_re_values):
        self.jstat_re_values = jstat_re_values
    #jstat -gccapacity
    def Jvm_NGC(self):
        return float(os.popen("echo %s | awk '{print $3}'" % (self.jstat_re_values)).read().replace("\n",""))/1024

    def Jvm_OGC(self):
        return float(os.popen("echo %s | awk '{print $9}'" % (self.jstat_re_values)).read().replace("\n",""))/1024

    def Jvm_Max_Total_memory(self):
        Jvm_NGCMX = os.popen("echo %s | awk '{print $2}'" % (self.jstat_re_values)).read().replace("\n","")
        Jvm_OGCMX = os.popen("echo %s | awk '{print $8}'" % (self.jstat_re_values)).read().replace("\n","")
        return float(float(Jvm_NGCMX) + float(Jvm_OGCMX))/1024

    #jstat -gc
    def Jvm_YGC(self):
        return os.popen("echo %s | awk '{print $17}'" % (self.jstat_re_values)).read().replace("\n","")

    def Jvm_FGC(self):
        return os.popen("echo %s | awk '{print $18}'" % (self.jstat_re_values)).read().replace("\n","")

    def Jvm_Total_memory(self):
        Jvm_S0C = os.popen("echo %s | awk '{print $4}'" % (self.jstat_re_values)).read().replace("\n","")
        Jvm_S1C = os.popen("echo %s | awk '{print $5}'" % (self.jstat_re_values)).read().replace("\n","")
        Jvm_EC = os.popen("echo %s | awk '{print $23}'" % (self.jstat_re_values)).read().replace("\n","")
        Jvm_OC = os.popen("echo %s | awk '{print $25}'" % (self.jstat_re_values)).read().replace("\n","")
        return float(float(Jvm_S0C) + float(Jvm_S1C) + float(Jvm_EC) + float(Jvm_OC))/1024

#    def Jvm_Free_memory(self):
#        return os.popen("echo %s | awk '{print $18}'" % (self.jstat_re_values)).read().replace("\n","")
#        pass

    def Jvm_Use_memory(self):
        Jvm_S0U = os.popen("echo %s | awk '{print $21}'" % (self.jstat_re_values)).read().replace("\n","")
        Jvm_S1U = os.popen("echo %s | awk '{print $22}'" % (self.jstat_re_values)).read().replace("\n","")
        Jvm_EU = os.popen("echo %s | awk '{print $24}'" % (self.jstat_re_values)).read().replace("\n","")
        Jvm_OU = os.popen("echo %s | awk '{print $26}'" % (self.jstat_re_values)).read().replace("\n","")
        return float(float(Jvm_S0U) + float(Jvm_S1U) + float(Jvm_EU) + float(Jvm_OU))/1024
 

def Push_Data(endpoint, metric_name, PushData):
    #endpoint = socket.gethostname()
    print endpoint
    print metric_name
    print PushData
    info_list = []
    ts = int(time.time())
    #print(ts)
    value = random.randint(1,100)
    dict_info= {
        "endpoint": endpoint,
        "metric": metric_name,
        "timestamp": ts,
        "step": 60,
        "value":PushData ,
        "counterType": "GAUGE",
        "tags": "JvmMon",
    }
    info_list.append(dict_info)
    requests.post("http://127.0.0.1:1988/v1/push", data=json.dumps(info_list ))




if __name__ == '__main__':
    #ProjectPath = "/data/server/www/bus365order"
    endpoint = socket.gethostname()
    #jstat_path = os.popen("which jstat").read().replace("\n","")
    ProjectPath = sys.argv[1]
    if os.path.exists(ProjectPath + "/server.pid"):
        ServerPid = os.popen("cat " + ProjectPath + "/server.pid").read().replace("\n","")
        try:
            jstat_re_values = os.popen("/usr/jdk1.8.0_181/bin/jstat -gccapacity " + ServerPid + " | sed -n 2p && /usr/jdk1.8.0_181/bin/jstat -gc " + ServerPid + " | sed -n 2p").read().replace("\n"," ")
            print jstat_re_values
            A = Jstat_Monitor_Indexes(jstat_re_values)
            Push_Data(endpoint, "Jvm_NGC", A.Jvm_NGC())
            Push_Data(endpoint, "Jvm_OGC", A.Jvm_OGC())
            Push_Data(endpoint, "Jvm_YGC", A.Jvm_YGC())
            Push_Data(endpoint, "Jvm_FGC", A.Jvm_FGC())
            Push_Data(endpoint, "Jvm_Total_memory", A.Jvm_Total_memory())
            Push_Data(endpoint, "Jvm_Use_memory", A.Jvm_Use_memory())
            Push_Data(endpoint, "Jvm_Max_Total_memory", A.Jvm_Max_Total_memory())
 
        except:
            #无法执行jstat时，返回-1
            #os.system("echo 11111 >> /var/log/jstat.log")
            Push_Data(endpoint, "Jvm_NGC", "-1")
            Push_Data(endpoint, "Jvm_OGC", "-1")
            Push_Data(endpoint, "Jvm_YGC", "-1")
            Push_Data(endpoint, "Jvm_FGC", "-1")
            Push_Data(endpoint, "Jvm_Total_memory", "-1")
            Push_Data(endpoint, "Jvm_Use_memory", "-1")
            Push_Data(endpoint, "Jvm_Max_Total_memory", "-1")

    else:
        #工程停止时，返回-2
        #os.system("echo 22222 >> /var/log/jstat.log")
        Push_Data(endpoint, "Jvm_NGC", "-2")
        Push_Data(endpoint, "Jvm_OGC", "-2")
        Push_Data(endpoint, "Jvm_YGC", "-2")
        Push_Data(endpoint, "Jvm_FGC", "-2")
        Push_Data(endpoint, "Jvm_Total_memory", "-2")
        Push_Data(endpoint, "Jvm_Use_memory", "-2")
        Push_Data(endpoint, "Jvm_Max_Total_memory", "-2")

