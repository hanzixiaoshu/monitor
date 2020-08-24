
#!/usr/bin/env python
#--*--encoding:utf8--*--

from prettytable import PrettyTable
from PIL import Image, ImageDraw, ImageFont
import os
import time
import paramiko
import json
import requests
import time
import json
import random
import re
import configparser
import cx_Oracle
from datetime import date, datetime

def OracleTableSpace(tab, sec_ip, value_port, keys):
    #try:
    conn = cx_Oracle.connect('sys', 'Bus365oracleDB0502', sec_ip + ':' + value_port + '/' + keys, cx_Oracle.SYSDBA)
    cursor = conn.cursor()
    sql = 'select al.tablespace_name "TableSpaceName", round(al.maxsizemb) "MaxSize MB", round(al.currsizemb) "CurrentSize MB", round(nvl(free.freesizemb, 0)) "FreeSize MB", round((1 - (nvl(free.freesizemb, 0) + al.maxsizemb - al.currsizemb) / al.maxsizemb) * 100, 2) "UsedPercent %" from (select t.tablespace_name, sum(f.bytes) / 1024 / 1024 currsizemb, sum(case when f.autoextensible = \'YES\' and f.bytes > f.maxbytes then f.bytes when f.autoextensible = \'YES\' and f.bytes <= f.maxbytes then f.maxbytes else f.bytes end) / 1024 / 1024 maxsizemb from dba_tablespaces t, dba_data_files f where t.tablespace_name = f.tablespace_name and t.contents = \'PERMANENT\' group by t.tablespace_name) al, (select tablespace_name, sum(bytes) / 1024 / 1024 freesizemb from dba_free_space group by tablespace_name) free where al.tablespace_name = free.tablespace_name(+)'
    result = cursor.execute(sql)

    #tab = PrettyTable()
    # 设置表头
    tab.field_names = ["表空间名称", "表空间最大值（MB）", "前使用大小（MB）", "剩余空间大小（MB）", "使用百分比（%）"]
    tab.add_row(["", "", "", "", ""])
    tab.add_row(["TableSpaceName(" + sec_ip + ")", "MaxSize MB", "CurrentSize MB", "FreeSize MB", "UsedPercent %"])
    # 表格内容插入
    for re in cursor:
        tab.add_row(re)
        #print(re)
    cursor.close()
    conn.close()

    """
    tab_info = str(tab)
    space = 5

    # PIL模块中，确定写入到图片中的文本字体
    # font = ImageFont.truetype('/home/doge/YaHeiConsolas.ttf', 15, encoding='utf-8')
    font = ImageFont.truetype('C:\\Windows\\Fonts\\simhei.ttf', 15, encoding='utf-8')
    # Image模块创建一个图片对象
    im = Image.new('RGB', (10, 10), (0, 0, 0, 0))
    # ImageDraw向图片中进行操作，写入文字或者插入线条都可以
    draw = ImageDraw.Draw(im, "RGB")
    # 根据插入图片中的文字内容和字体信息，来确定图片的最终大小
    img_size = draw.multiline_textsize(tab_info, font=font)

    # 图片初始化的大小为10-10，现在根据图片内容要重新设置图片的大小
    im_new = im.resize((img_size[0] + space * 2, img_size[1] + space * 2))
    del draw
    del im
    draw = ImageDraw.Draw(im_new, 'RGB')
    # 批量写入到图片中，这里的multiline_text会自动识别换行符
    # python2
    # draw.multiline_text((space,space), unicode(tab_info, 'utf-8'), fill=(255,255,255), font=font)
    # python3
    draw.multiline_text((space, space), tab_info, fill=(255, 255, 255), font=font)

    im_new.save('/app/pic/12345.PNG', "PNG")
    del draw
    """
    #return "ok"

def RunAll():
    iniconfig = configparser.ConfigParser()
    iniconfig.read('/app/monitor/oracle_list.ini', encoding='utf-8')
    tab = PrettyTable()
    #读取所有sections项
    sections_ip = iniconfig.sections()
    #print(sections_ip)
    #获取所有key、value
    for sec_ip in sections_ip:
        #print("--------------------------")
        #print(sec_ip)
        for keys in iniconfig.options(sec_ip):
            value_port = iniconfig.get(sec_ip, keys)
            #print(keys)
            OracleTableSpace(tab, sec_ip, value_port, keys)

    tab_info = str(tab)
    space = 5
    # PIL模块中，确定写入到图片中的文本字体
    font = ImageFont.truetype('/usr/share/fonts/simhei.ttf', 15, encoding='utf-8')
    # Image模块创建一个图片对象
    im = Image.new('RGB', (10, 10), (0, 0, 0, 0))
    # ImageDraw向图片中进行操作，写入文字或者插入线条都可以
    draw = ImageDraw.Draw(im, "RGB")
    # 根据插入图片中的文字内容和字体信息，来确定图片的最终大小
    img_size = draw.multiline_textsize(tab_info, font=font)

    # 图片初始化的大小为10-10，现在根据图片内容要重新设置图片的大小
    im_new = im.resize((img_size[0] + space * 2, img_size[1] + space * 2))
    del draw
    del im
    draw = ImageDraw.Draw(im_new, 'RGB')
    # 批量写入到图片中，这里的multiline_text会自动识别换行符
    # python2
    # draw.multiline_text((space,space), unicode(tab_info, 'utf-8'), fill=(255,255,255), font=font)
    # python3
    draw.multiline_text((space, space), tab_info, fill=(255, 255, 255), font=font)

    im_new.save(today + ".PNG", "PNG")
    del draw
    Up_Oss()
    DingSend()

def Up_Oss():
    command_up = "/usr/bin/ossutil64 --maxupspeed 9000 --config-file=/etc/ossconfig cp -f  /app/monitor/" + today + ".PNG  oss://oracle-monitor/monitor/"
    os.system(command_up)

#def DingSend(oracle_tablespace):
def DingSend():
    webhook = dingdingwebhook
    header = {"Content-Type": "application/json", "charset": "utf-8"}
    data = {
       "msgtype": "markdown",
        "markdown": {
            "title": "Oracle表空间使用状态",
            "text": "#### Oracle表空间使用状态 @18000000000 @15000000000 \n> 服务器ip：100.200.3.32、100.200.2.22，Oracle表空间使用情况，请查看。\n> ![screenshot](https://oracle-monitor.oss-cn-tianjin.aliyuncs.com/monitor/" + today + ".PNG)\n> ###### 今日天气情况 [天气](http://www.weather.com.cn/weather/101010100.shtml) \n"
        },
        "at": {
          "atMobiles": [
              "18000000000",
              "15000000000"
          ],
        }
    }
    #send_data = json.dumps(data).encode('utf-8')
    send_data = json.dumps(data)
    return requests.post(url=webhook, data=send_data, headers=header)



if __name__ == '__main__':
    today = (datetime.now()).strftime("%Y-%m-%d-%H%M%S")
    RunAll()

