#!/usr/bin/env python
# -*-coding:utf-8-*-

import json
import os
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

class CustomizedHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        page_size = self.get_argument('page', default=1, strip=True)
        limit = self.get_argument('limit', default=30, strip=True)
        limit_start = (int(page_size) - 1) * int(limit)
        user_list = []
        with DBContext('r') as session:
            conditions = []
            # conditions.append(Companylist.company_id.like('%{}%'.format("/")))
            # todata = session.query(Companylist).filter(*conditions).order_by(Companylist.ctime.desc()).offset(limit_start).limit(int(limit)).all()
            todata = session.query(Customized).filter(*conditions).order_by(Customized.ctime.desc()).all()
            tocount = session.query(Customized).filter(*conditions).count()

        for msg in todata:
            Customizationlist_dict = {}
            data_dict = model_to_dict(msg)
            Customizationlist_dict["id"] = data_dict["id"]
            Customizationlist_dict["title"] = data_dict["title"]
            Customizationlist_dict["dbid"] = data_dict["dbid"]
            Customizationlist_dict["times"] = data_dict["times"]

            data_list.append(Customizationlist_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        totitle = str(data.get('title', None))
        header = str(data.get('header', None))
        dblinkstr = str(data.get('dblinkstr', None))
        dataname = str(data.get('dataname', None))
        dbid = str(data.get('dbid', None))
        times = data.get('times', None)
        # ins_log.read_log('info',totitle)

        with DBContext('w', None, True) as session:
            session.add(Customized(
                totitle=totitle,
                header=header,
                dbid=dbid,
                times=times,
                dblinkstr=dblinkstr,
                dataname=dataname,
            ))
            session.commit()
        self.write(dict(code=0, msg='成功', count=0, data=[]))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        if not id:
            return self.write(dict(code=-1, msg='ID不能为空'))

        with DBContext('w', None, True) as session:
            session.query(Customized).filter(Customized.id == id).delete(synchronize_session=False)
        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        title = data.get('title', None)
        dbid = data.get('dbid', None)
        times = data.get('times', None)

        try:
            with DBContext('w', None, True) as session:
                session.query(Customized).filter(Customized.id == id).update({
                Customized.title: title,
                Customized.dbid: dbid,
                Customized.times: times,
                })
                session.commit()
        except Exception as e:
            return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))

        self.write(dict(code=0, msg='编辑成功'))

# class StakeholderList(BaseHandler):
#     def get(self, *args, **kwargs):
#         data_list = []
#         value = self.get_argument('value', default=None, strip=True)
#         user_list = []
#         with DBContext('r') as session:
#             todata = session.query(Stakeholder).filter(Stakeholder.company == value).order_by(Stakeholder.ctime.desc()).all()
#             tocount = session.query(Stakeholder).filter(Stakeholder.company == value).count()
#
#         for msg in todata:
#             case_dict = {}
#             data_dict = model_to_dict(msg)
#             case_dict["id"] = data_dict["id"]
#             case_dict["username"] = data_dict["username"]
#             case_dict["company"] = data_dict["company"]
#             case_dict["department"] = data_dict["department"]
#             case_dict["position"] = data_dict["position"]
#             case_dict["duty"] = data_dict["duty"]
#             case_dict["tel"] = data_dict["tel"]
#             case_dict["addr"] = data_dict["addr"]
#             case_dict["email"] = data_dict["email"]
#             case_dict["remarks"] = data_dict["remarks"]
#
#
#             case_dict["ctime"] = str(data_dict["ctime"])
#             data_list.append(case_dict)
#
#         if len(data_list) > 0:
#             self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
#         else:
#             self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))


customized_urls = [
    (r"/v2/accounts/customized/", CustomizedHandler),
]

if __name__ == "__main__":
    pass
