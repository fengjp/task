#!/usr/bin/env python
# -*-coding:utf-8-*-

import json
import os
import  shutil
import re
from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from websdk.consts import const
from websdk.cache_context import cache_conn
from websdk.web_logs import ins_log
from sqlalchemy import or_, and_
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from settings import CUSTOM_DB_INFO
from libs.server.server_common import *
from libs.myAnsible import AnsiableAPI
from models.task import Meter,model_to_dict
from datetime import datetime

# class MeterHandler(BaseHandler):
#     def get(self, *args, **kwargs):
#         data_list = [{
#           "id" : "",
#           "totitle" : '每日巡检报告',
#           "dbid" : '',
#           "times" : '',
#           "cycle" : '',
#           "flag":'',
#           "todate":'',
#           "start_end": '',
#           "download_dir" : 'xunjian',
#         },]
#         # key = self.get_argument('key', default=None, strip=True)
#         # value = self.get_argument('value', default=None, strip=True)
#         page_size = self.get_argument('page', default=1, strip=True)
#         limit = self.get_argument('limit', default=30, strip=True)
#         limit_start = (int(page_size) - 1) * int(limit)
#         user_list = []
#         with DBContext('r') as session:
#             conditions = []
#             todata = session.query(Customized).filter().order_by(Customized.create_time.desc()).offset(limit_start).limit(int(limit)).all()
#             # todata = session.query(Customized).filter(*conditions).order_by(Customized.ctime.desc()).all()
#             tocount = session.query(Customized).filter().count()
#
#         for msg in todata:
#             Customizationlist_dict = {}
#             data_dict = model_to_dict(msg)
#             Customizationlist_dict["id"] = data_dict["id"]
#             Customizationlist_dict["totitle"] = data_dict["totitle"]
#             Customizationlist_dict["dbid"] = data_dict["dbid"]
#             Customizationlist_dict["times"] = data_dict["times"]
#             Customizationlist_dict["cycle"] = str(data_dict["cycle"])
#             Customizationlist_dict["flag"] = str(data_dict["flag"])
#             Customizationlist_dict["todate"] = str(data_dict["todate"])
#             Customizationlist_dict["start_end"] = str(data_dict["start_end"])
#             Customizationlist_dict["download_dir"] = data_dict["download_dir"]
#
#             data_list.append(Customizationlist_dict)
#
#         if len(data_list) > 0:
#             self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
#         else:
#             self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))
#
#     def post(self, *args, **kwargs):
#         data = json.loads(self.request.body.decode("utf-8"))
#         totitle = str(data.get('title', None))
#         dbid = str(data.get('dbid', None))
#         times = data.get('times', None)
#         cycle = str(data.get('cycle', '[]'))
#         flag = str(data.get('flag', None))
#         todate = str(data.get('todate', None))
#         start_end = str(data.get('start_end', None))
#         now_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
#         download_dir = "timing" + now_time
#
#
#         with DBContext('w', None, True) as session:
#             session.add(Customized(
#                 totitle=totitle,
#                 dbid=dbid,
#                 times=times,
#                 cycle=cycle,
#                 flag=flag,
#                 todate=todate,
#                 start_end=start_end,
#                 download_dir=download_dir,
#             ))
#             session.commit()
#         self.write(dict(code=0, msg='成功', count=0, data=[]))
#
#     def delete(self, *args, **kwargs):
#         data = json.loads(self.request.body.decode("utf-8"))
#         id = data.get('id', None)
#         download_dir = str(data.get('download_dir', None))
#         if not id:
#             return self.write(dict(code=-1, msg='ID不能为空'))
#         # 保存文件
#         Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#         upload_path = '{}/static/report/'.format(Base_DIR)
#         # upload_path = upload_path + download_dir
#         ins_log.read_log('info', "11111111111111111111111111111111111111")
#         ins_log.read_log('info', upload_path)
#         ins_log.read_log('info', "11111111111111111111111111111111111111")
#         os.chdir(upload_path)
#         if os.path.exists(download_dir):
#              shutil.rmtree(download_dir)
#
#
#
#         with DBContext('w', None, True) as session:
#             session.query(Customized).filter(Customized.id == id).delete(synchronize_session=False)
#         self.write(dict(code=0, msg='删除成功'))
#
#     def put(self, *args, **kwargs):
#         data = json.loads(self.request.body.decode("utf-8"))
#         id = data.get('id', None)
#         totitle = str(data.get('title', None))
#         dbid = str(data.get('dbid', None))
#         times = data.get('times', None)
#         cycle = str(data.get('cycle', None))
#         flag = str(data.get('flag', None))
#         todate = str(data.get('todate', None))
#         start_end  =  str(data.get('start_end', None))
#         download_dir = str(data.get('download_dir', None))
#         ins_log.read_log('info',flag)
#         ins_log.read_log('info', todate)
#
#         try:
#             with DBContext('w', None, True) as session:
#                 session.query(Customized).filter(Customized.id == id).update({
#                 Customized.totitle: totitle,
#                 Customized.dbid: dbid,
#                 Customized.times: times,
#                 Customized.cycle: cycle,
#                 Customized.flag: flag,
#                 Customized.todate: todate,
#                 Customized.start_end: start_end,
#                 Customized.download_dir: download_dir,
#                 })
#                 session.commit()
#         except Exception as e:
#             return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))
#
#         self.write(dict(code=0, msg='编辑成功'))

class MeterHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        data_list2 = []
        web_list = []
        app_list = []
        time_list = ["00:00","01:00","02:00","03:00","04:00","05:00","06:00","07:00","08:00","09:00","10:00",
                     "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
                     "21:00", "22:00", "23:00", "24:00"]
        value = str(self.get_argument('value',strip=True))
        # ins_log.read_log('info', value)
        with DBContext('r') as session:
            # conditions = []
            todata = session.query(Meter).filter(Meter.today == value).all()
            # tocount = session.query(Customized).filter().count()

        for msg in todata:
            meter_list = {}
            data_dict = model_to_dict(msg)
            meter_list["id"] = data_dict["id"]
            meter_list["totitle"] = data_dict["totitle"]
            meter_list["today"] = data_dict["today"]
            meter_list["times"] = data_dict["times"]
            meter_list["longtime"] = data_dict["longtime"]
            meter_list["remarks"] = data_dict["remarks"]
            meter_list["create_time"] = data_dict["create_time"]
            if  data_dict["totitle"] == "web12123":
                data_list.append(meter_list)
            if  data_dict["totitle"] == "app12123":
                data_list2.append(meter_list)

        for m in time_list:
            for  h in  data_list:
                if m == h["times"]:
                    temp_dict = {}
                    temp_dict["totitle"] = h["totitle"]
                    temp_dict["times"] = m
                    temp_dict["longtimes"] = h["longtime"]
                    temp_dict["remarks"] = h["remarks"]
                    web_list.append(temp_dict)
        for m in time_list:
            for  h in  data_list2:
                if m == h["times"]:
                    temp_dict = {}
                    temp_dict["totitle"] = h["totitle"]
                    temp_dict["times"] = m
                    temp_dict["longtimes"] = h["longtime"]
                    temp_dict["remarks"] = h["remarks"]
                    app_list.append(temp_dict)
        ins_log.read_log('info', "22222222222222222222222222222222222222")
        ins_log.read_log('info', web_list)
        ins_log.read_log('info', app_list)
        ins_log.read_log('info', "22222222222222222222222222222222222222")
        if len(web_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=web_list,list=app_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))



meter_urls = [
    (r"/v2/accounts/meter/", MeterHandler)

]

if __name__ == "__main__":
    pass
