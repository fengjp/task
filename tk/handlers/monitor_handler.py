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

class MonitorHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None)
        value = self.get_argument('value', default=None)
        dict_list = []
        ip_list = ['127.0.0.1', '39.104.83.140']
        serverObjList = get_serverObjList(ip_list)
        asb = AnsiableAPI(connection='smart', hostsresource=serverObjList)
        asb.run(hosts="39.104.83.140", module="shell", args='uptime')
        stdout_dict = json.loads(asb.get_result())
        print(stdout_dict)

customquery_urls = [
    (r"/v1/monitor/serInfo", MonitorHandler),
]

if __name__ == "__main__":
    pass
