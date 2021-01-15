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
from models.task import Score,model_to_dict
from datetime import datetime
import dateutil.relativedelta

class MeterHandler(BaseHandler):
    def get(self, *args, **kwargs):
        today = datetime.now().strftime('%Y-%m')  # 当前月份
        # 组装月份数组
        months_list = []
        now = datetime.now()
        for  h in range(11,0,-1):
              date = now + dateutil.relativedelta.relativedelta(months=-h)  # 上个月时间
              # date.strftime('%Y-%m') #上个月份
              months_list.append(date.strftime('%Y-%m'))
        months_list.append(today)
        data_list = []
        data_list2 = []
        sum_list = []

        # value = str(self.get_argument('value',strip=True))
        today = datetime.now().strftime('%Y-%m') #当前月份
        ins_log.read_log('info', today)
        with DBContext('r') as session:
            # conditions = []
            todata = session.query(Score).filter(Score.today == today).all()
            # tocount = session.query(Customized).filter().count()

        for msg in todata:
            meter_list = {}
            data_dict = model_to_dict(msg)
            meter_list["id"] = data_dict["id"]
            meter_list["today"] = data_dict["today"]
            meter_list["fuwu_defen"] = data_dict["fuwu_defen"]
            meter_list["fuwu_remarks"] = data_dict["fuwu_remarks"]
            meter_list["xitong_defen"] = data_dict["xitong_defen"]
            meter_list["xitong_remarks"] = data_dict["xitong_remarks"]
            meter_list["duanxin_defen"] = data_dict["duanxin_defen"]
            meter_list["duanxin_remarks"] = data_dict["duanxin_remarks"]
            meter_list["nwwang_defen"] = data_dict["nwwang_defen"]
            meter_list["nwwang_remarks"] = data_dict["nwwang_remarks"]
            meter_list["yidi_defen"] = data_dict["yidi_defen"]
            meter_list["yidi_remarks"] = data_dict["yidi_remarks"]
            meter_list["renlian_defen"] = data_dict["renlian_defen"]
            meter_list["renlian_remarks"] = data_dict["renlian_remarks"]
            meter_list["yunxing_defen"] = data_dict["yunxing_defen"]
            meter_list["yunxing_remarks"] = data_dict["yunxing_remarks"]
            data_list.append(meter_list)

        for g in months_list:
            ins_log.read_log('info', today)
            temp_sum = 0
            with DBContext('r') as session:
                # conditions = []
                todata = session.query(Score).filter(Score.today == g).all()
                tocount = session.query(Score).filter(Score.today == g).count()
            if tocount < 1:
                temp_sum = 0
            else:
              for msg in todata:
                meter_list = {}
                data_dict = model_to_dict(msg)
                meter_list["id"] = data_dict["id"]
                meter_list["today"] = data_dict["today"]
                temp_sum = int(data_dict["fuwu_defen"]) + int(data_dict["xitong_defen"]) + int(data_dict["duanxin_defen"])+ int(data_dict["nwwang_defen"]) \
                           + int(data_dict["yidi_defen"]) + int(data_dict["renlian_defen"]) + int(data_dict["yunxing_defen"])
            sum_list.append(temp_sum + 39+5) #(39+5)分：固定可以得的分数
        data_list2.append(months_list)
        data_list2.append(sum_list)
        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=data_list,list=data_list2))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))



meter_urls = [
    (r"/v2/accounts/meter/", MeterHandler)

]

if __name__ == "__main__":
    pass
