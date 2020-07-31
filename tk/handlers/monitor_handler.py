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
        ipstr = self.get_argument('key', default=None)
        cardstr = self.get_argument('value', default=None)
        cardtype = str(cardstr)
        ip_list = [ipstr]
        serverObjList = get_serverObjList(ip_list)
        asb = AnsiableAPI(connection='smart', hostsresource=serverObjList)
        # 获取卡片数据
        cardlist = []
        if cardtype == '0':
            carddict = getcard0(ipstr, asb)  # 主机基本信息
            cardlist.append(carddict)
        if cardtype == '1':
            carddict = getcard1(ipstr, asb)  # 文件分区使用情况
            cardlist.append(carddict)
        # asb.run(hosts=ipstr, module="shell", args='uptime')
        # stdout_dict = json.loads(asb.get_result())
        if len(cardlist) > 0:
            self.write(dict(code=0, msg='获取報告成功', count=1, data=cardlist))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))


def getcard0(ipstr, asb):
    carddict = {"title": "主机基本信息", "flag": "0", "tableData": []}
    data_dict = {"系统IP": ipstr, "主机": ipstr, "CPU频率": "", "物理内存总大小": "", "CPU核数": "", "操作系统版本": "", "系统位数": "",
                 "维护人": "", "维护人联系电话": ""}
    # cpu频率
    asb.run(hosts=ipstr, module="shell", args='lscpu')
    stdout_dict = json.loads(asb.get_result())
    if stdout_dict["success"]:

        data_dict["CPU频率"] = stdout_dict["success"][ipstr]["stdout_lines"][14].split()[2] + "MHz"
        data_dict["CPU核数"] = stdout_dict["success"][ipstr]["stdout_lines"][3].split()[1]
        data_dict["系统位数"] = stdout_dict["success"][ipstr]["stdout_lines"][0].split()[1]

    else:
        data_dict["CPU频率"] = ""
    # 获取物理内存
    asb.run(hosts=ipstr, module="shell", args='free')
    stdout_dict = json.loads(asb.get_result())
    if stdout_dict["success"]:
        data_dict["物理内存总大小"] = stdout_dict["success"][ipstr]["stdout_lines"][1].split()[1]

    else:
        data_dict["物理内存总大小"] = ""

    # 获取操作系统版本
    asb.run(hosts=ipstr, module="shell", args='cat  /etc/*release*')
    stdout_dict = json.loads(asb.get_result())
    data_dict["操作系统版本"] = stdout_dict["failed"][ipstr]["stdout_lines"][0]
    carddict["tableData"].append(data_dict)
    return carddict


def getcard1(ipstr, asb):
    carddict = {"title": "文件分区使用情况", "flag": "1", "tableData": []}
    # 文件分区使用情况
    asb.run(hosts=ipstr, module="shell", args='df -h')
    stdout_dict = json.loads(asb.get_result())
    if stdout_dict["success"]:
        temp_list = stdout_dict["success"][ipstr]["stdout_lines"]
        for i in range(1, len(temp_list)):
            data_dict = {"name": "", "size": "", "utilization_rate": "", "capacity": "", "usedsize": ""}
            data_dict["name"] = temp_list[i].split()[5]
            data_dict["size"] = temp_list[i].split()[3]
            data_dict["utilization_rate"] = temp_list[i].split()[4]
            data_dict["capacity"] = temp_list[i].split()[1]
            data_dict["usedsize"] = temp_list[i].split()[2]
            carddict["tableData"].append(data_dict)
    else:
        # 文件分区使用情况
        asb.run(hosts=ipstr, module="shell", args='df -sg')
        stdout_dict = json.loads(asb.get_result())
        temp_list = stdout_dict["success"][ipstr]["stdout_lines"]
        for i in range(1, len(temp_list)):
            data_dict = {"名称": "", "分区空闲大小": "", "分区使用率": "", "分区总容量(自发现)": "", "分区已使用大小(自发现)": ""}
            data_dict["名称"] = temp_list[i].split()[5]
            data_dict["分区空闲大小"] = temp_list[i].split()[3]
            data_dict["分区使用率"] = temp_list[i].split()[4]
            data_dict["分区总容量(自发现)"] = temp_list[i].split()[1]
            data_dict["分区已使用大小(自发现)"] = temp_list[i].split()[2]
            carddict["tableData"].append(data_dict)

    # ins_log.read_log('info', "1222222222222222222222222222222222222")
    # ins_log.read_log('info', stdout_dict)
    # ins_log.read_log('info', carddict)
    # ins_log.read_log('info', "1111111111111111112222222222222222222")
    return carddict


monitor_urls = [
    (r"/v1/monitor/serInfo/", MonitorHandler),
]

if __name__ == "__main__":
    pass
