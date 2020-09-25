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
from models.task import Customized,model_to_dict
from datetime import datetime

class CustomizedHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = [{
          "id" : "",
          "totitle" : '每日巡检报告',
          "header" : '',
          "dbid" : '',
          "times" : '',
          "dbname_id" : '',
          "dataname" : '',
          "cycle" : '',
          "download_dir" : 'xunjian',
        },]
        # key = self.get_argument('key', default=None, strip=True)
        # value = self.get_argument('value', default=None, strip=True)
        page_size = self.get_argument('page', default=1, strip=True)
        limit = self.get_argument('limit', default=30, strip=True)
        limit_start = (int(page_size) - 1) * int(limit)
        user_list = []
        with DBContext('r') as session:
            conditions = []
            todata = session.query(Customized).filter().order_by(Customized.create_time.desc()).offset(limit_start).limit(int(limit)).all()
            # todata = session.query(Customized).filter(*conditions).order_by(Customized.ctime.desc()).all()
            tocount = session.query(Customized).filter().count()

        for msg in todata:
            Customizationlist_dict = {}
            data_dict = model_to_dict(msg)
            Customizationlist_dict["id"] = data_dict["id"]
            Customizationlist_dict["totitle"] = data_dict["totitle"]
            Customizationlist_dict["header"] = data_dict["header"]
            Customizationlist_dict["dbname_id"] = data_dict["dbname_id"]
            Customizationlist_dict["dataname"] = data_dict["dataname"]
            Customizationlist_dict["dbid"] = data_dict["dbid"]
            Customizationlist_dict["times"] = data_dict["times"]
            Customizationlist_dict["cycle"] = str(data_dict["cycle"])
            Customizationlist_dict["download_dir"] = data_dict["download_dir"]

            data_list.append(Customizationlist_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        totitle = str(data.get('title', None))
        header = str(data.get('header', None))
        dbname_id = str(data.get('dbname_id', None))
        dataname = str(data.get('dataname', None))
        dbid = str(data.get('dbid', None))
        times = data.get('times', None)
        cycle = str(data.get('cycle', None))
        # ins_log.read_log('info',totitle)
        now_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))
        download_dir = "timing" + now_time


        with DBContext('w', None, True) as session:
            session.add(Customized(
                totitle=totitle,
                header=header,
                dbid=dbid,
                times=times,
                dbname_id=dbname_id,
                dataname=dataname,
                cycle=cycle,
                download_dir=download_dir,
            ))
            session.commit()
        self.write(dict(code=0, msg='成功', count=0, data=[]))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        download_dir = str(data.get('download_dir', None))
        if not id:
            return self.write(dict(code=-1, msg='ID不能为空'))
        # 保存文件
        Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_path = '{}/static/report/'.format(Base_DIR)
        # upload_path = upload_path + download_dir
        ins_log.read_log('info', "11111111111111111111111111111111111111")
        ins_log.read_log('info', upload_path)
        ins_log.read_log('info', "11111111111111111111111111111111111111")
        os.chdir(upload_path)
        shutil.rmtree(download_dir)



        with DBContext('w', None, True) as session:
            session.query(Customized).filter(Customized.id == id).delete(synchronize_session=False)
        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        totitle = str(data.get('title', None))
        header = str(data.get('header', None))
        dbname_id = str(data.get('dbname_id', None))
        dataname = str(data.get('dataname', None))
        dbid = str(data.get('dbid', None))
        times = data.get('times', None)
        cycle = str(data.get('cycle', None))
        download_dir = str(data.get('download_dir', None))
        # ins_log.read_log('info',totitle)

        try:
            with DBContext('w', None, True) as session:
                session.query(Customized).filter(Customized.id == id).update({
                Customized.totitle: totitle,
                Customized.header: header,
                Customized.dbname_id: dbname_id,
                Customized.dataname: dataname,
                Customized.dbid: dbid,
                Customized.times: times,
                Customized.cycle: cycle,
                Customized.download_dir: download_dir,
                })
                session.commit()
        except Exception as e:
            return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))

        self.write(dict(code=0, msg='编辑成功'))

# class Customized_list(BaseHandler):
#     def get(self, *args, **kwargs):
#         data_list = []
#         value = int(self.get_argument('value', default=None, strip=True))
#         with DBContext('r') as session:
#             conditions = []
#             todata = session.query(Customized.id == value).filter().all()
#             #tocount = session.query(Customized).filter().count()
#
#         for msg in todata:
#             Customizationlist_dict = {}
#             data_dict = model_to_dict(msg)
#             Customizationlist_dict["id"] = data_dict["id"]
#             Customizationlist_dict["totitle"] = data_dict["totitle"]
#             Customizationlist_dict["header"] = data_dict["header"]
#             Customizationlist_dict["dbname_id"] = data_dict["dbname_id"]
#             Customizationlist_dict["dataname"] = data_dict["dataname"]
#             Customizationlist_dict["dbid"] = data_dict["dbid"]
#             Customizationlist_dict["times"] = data_dict["times"]
#             Customizationlist_dict["cycle"] = str(data_dict["cycle"])
#             Customizationlist_dict["download_dir"] = data_dict["download_dir"]
#
#             data_list.append(Customizationlist_dict)
#
#         if len(data_list) > 0:
#             self.write(dict(code=0, msg='获取成功', data=data_list))
#         else:
#             self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))


customized_urls = [
    (r"/v2/accounts/customized/", CustomizedHandler),
    (r"/v2/accounts/customizedDelete/", CustomizedHandler),

]

if __name__ == "__main__":
    pass
