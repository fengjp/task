#!/usr/bin/env python
# -*-coding:utf-8-*-
import os
import sys
_op = os.path.dirname
cwdir = _op(os.path.abspath(__file__))
project_path = _op(_op(os.path.abspath(__file__)))
app_path = _op(project_path)
sys.path.insert(0, project_path)

from datetime import datetime
import requests
from settings import CUSTOM_DB_INFO
from multiprocessing import Pool
from libs.mysql_conn import MysqlBase



def getdatebase(datebase_name, select_str):
    CUSTOM_DB_INFO['db'] = datebase_name
    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
    db_info = mysql_conn.query(select_str)
    return db_info
def change_datebase(datebase_name, select_str):
    CUSTOM_DB_INFO['db'] = datebase_name
    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
    db_info = mysql_conn.change(select_str)
    return db_info
#互联网平台网页服务监控（网页） https://gd.122.gov.cn/
def run():
    while 1:
      print("请求https://gd.122.gov.cn/开始")
      toSeconds = 0
      req = requests.get("https://gd.122.gov.cn/")
      if req.status_code != 200:
            toSeconds = req.elapsed.microseconds/1000000   #1秒=1000000微妙
            print(toSeconds)
      else:
          pass
      #获取当前时间
      set_day = "'" + datetime.now().strftime('%Y-%m-%d') + "'"
      set_seconds = "'" + datetime.now().strftime('%H:') + "00" + "'"
      sql_str = "select id,remarks,longtime from  meter where totitle='web12123'  and today = " + set_day  + " and times = " + set_seconds
      meter_date = getdatebase("codo_task", sql_str)  # 执行时间表
      if len(meter_date):
          if toSeconds > 0:
                get_id, get_remarks , get_longtime = meter_date[0]
                to_longtime = int(get_longtime) + toSeconds
                remarkslist = eval(get_remarks)
                remarks = {}
                remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                remarks["getlongtime"] = toSeconds
                remarkslist.append(remarks)
                toremark = '"' + str(remarkslist) + '"'
                sql_str3 = 'update  meter set longtime = '  + str(to_longtime) +','+  '  remarks=' + toremark +  '  where id=' + str(get_id)
                # print(sql_str3)
                get_num = change_datebase("codo_task", sql_str3)

      else:
          remarkslist = []
          remarks = {}  # {"gettime":"","getlongtime":""}
          remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          remarks["getlongtime"] = toSeconds
          remarkslist.append(remarks)
          toremark  =  '"' + str(remarkslist) + '"'
          set_creattime = '"' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '"'
          toSeconds2 = '"' + str(toSeconds) + '"'
          sql_str2 = 'insert into meter(totitle,today,times,longtime,remarks,create_time)  values("web12123",'  + set_day + ','\
                     + set_seconds +','+ toSeconds2 + ',' + str(toremark) + ','+ set_creattime + ')'
          get_num = change_datebase("codo_task", sql_str2)


if __name__ == "__main__":
    run()
