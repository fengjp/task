#!/usr/bin/env python
# -*-coding:utf-8-*-
import json
import os
import re
from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from websdk.cache_context import cache_conn
from websdk.web_logs import ins_log
from sqlalchemy import or_, and_
from models.certdata import model_to_dict, CertDataUpLoadLog, CertDataUpLoadError, CertDataDownLoadError
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from libs.aes_coder import encrypt, decrypt
from collections import Counter
import traceback
import datetime


class CertDataFileHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []
        query_info = []
        count = 0

        if key == 'UpLoadLog':
            with DBContext('r') as session:
                count = session.query(CertDataUpLoadLog).count()
                query_info = session.query(CertDataUpLoadLog).all()

        if key == 'UpLoadError':
            with DBContext('r') as session:
                count = session.query(CertDataUpLoadError).count()
                query_info = session.query(CertDataUpLoadError).all()

        if key == 'DownLoadError':
            with DBContext('r') as session:
                count = session.query(CertDataDownLoadError).count()
                query_info = session.query(CertDataDownLoadError).all()

        for msg in query_info:
            if key == 'UpLoadLog':
                data_dict = {}
                data_dict['total'] = msg.total
                data_dict['success'] = msg.success
                data_dict['failed'] = msg.failed
                data_dict['create_time'] = str(msg.create_time)
                dict_list.append(data_dict)

            if key == 'UpLoadError':
                data_dict = {}
                data_dict['data'] = msg.data
                data_dict['create_time'] = str(msg.create_time)
                dict_list.append(data_dict)

            if key == 'DownLoadError':
                data_dict = {}
                data_dict['data'] = msg.data
                data_dict['create_time'] = str(msg.create_time)
                dict_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', data=dict_list, count=count))


certdata_urls = [
    (r"/v1/getcertdata/", CertDataFileHandler),
]

if __name__ == "__main__":
    pass
