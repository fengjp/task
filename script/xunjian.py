#!/usr/bin/env python
# -*-coding:utf-8-*-
import os
import sys
import json

_op = os.path.dirname
cwdir = _op(os.path.abspath(__file__))
project_path = _op(_op(os.path.abspath(__file__)))
app_path = _op(project_path)
sys.path.insert(0, project_path)
import re
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from settings import CUSTOM_DB_INFO
from libs.server.server_common import *
from libs.myAnsible import AnsiableAPI
import pandas as pd
import xlrd
import requests
import datetime
from ftplib import FTP
import cx_Oracle
from libs.aes_coder import encrypt, decrypt

DB_list = {}
# 读取报告模板
# requese请求url,判断是否异常
# ftp请求测试，判断是否异常
# 数据库
ftpdict = {
    "ftp://10.40.30.16": {"username": "hlw", "password": "hlw"},#
    "ftp://173.173.10.23": {"username": "jiankong", "password": "123"},
    "ftp://10.40.30.253": {"username": "jiankong", "password": "123"},
    "ftp://10.40.30.33": {"username": "jiankong", "password": "123"},#
}


def gethttp(urlstr):
    print("requests请求开始")
    r = requests.get(urlstr, timeout=3)
    return r.status_code


def getftp(ftpstr):
    ftpflg = 0
    ftp = FTP()
    ftp.set_debuglevel(2)
    ftp.encoding = 'utf-8'
    print(ftpstr.split(':')[1][2:])
    print(ftpdict[ftpstr]["username"])
    print(ftpdict[ftpstr]["password"])

    try:
        ftp.connect(ftpstr.split(':')[1][2:], 21, timeout=3)
        ftp.login(ftpdict[ftpstr]["username"], ftpdict[ftpstr]["password"])
        tocode = ftp.getwelcome()  # 打印出欢迎信息
        if "welcome" in tocode:
            ftpflg = 1
        else:
            ftpflg = 0
    except:
        ftpflg = 0

    ftp.set_debuglevel(0)  # 关闭调试模式
    ftp.quit  # 退出ftp
    return ftpflg


def getdatebase(ipstr):
    tempdata = []
    flag = []
    print(ipstr[0][0], ipstr[0][1])
    toname = ipstr[0][0]
    toip = ipstr[0][1]

    if toip not in DB_list:
        CUSTOM_DB_INFO['db'] = 'codo_cmdb'
        mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
        # 获取数据库源 连接地址
        select_db = 'select db_type, db_host, db_port, db_user, db_pwd from asset_db'
        db_info = mysql_conn.query(select_db)
        if len(db_info) > 0:
            for db_type, db_host, db_port, db_user, db_pwd in db_info:
                DB_list[db_host] = [db_port, db_user, db_pwd]

    # for toname, toip in ipstr:
    # 解密
    # 连接数据库
    # print(DB_list)
    try:
        # uri = '{0}/{1}@{2}:{3}/{4}'.format(DB_list[toip][1], decrypt(DB_list[toip][2]), toip, DB_list[toip][0], toname)
        # conn = cx_Oracle.connect(uri)
        # cur = conn.cursor()
        # 获取表空间数据
        # sqlstr = ""
        # curlist = cur.execute(sqlstr)
        # datadict = curlist.fetchall()
        datalist = [("system", 3.39, 98.06), ("rm_stat", 260.45, 87.63), ("PASS_20170201", 0.04, 99.67)]
        for name, sumsize, uselv in datalist:
            if float(sumsize) < 50 and float(uselv) > 99:
                flag.append(0)
            else:
                flag.append(1)
            if float(uselv) > 90:
                name = name + ':' + str(uselv) + "%"
                tempdata.append(name)
        # 关闭光标
        # cur.close()
        # 关闭数据库连接
        # conn.close()

    except:
        flag.append(0)

    return flag, tempdata


def timeflag():
    nowTime = datetime.datetime.now().strftime('%H:%M:%S')  # 现在
    if int(nowTime.split(':')[0]) < 19:
        return 1
    else:
        return 0


def run():
    # 读取报告模板
    if timeflag():
        Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_path = '{}/static/report/系统巡检报告_模板.xls'.format(Base_DIR)
        df = pd.read_excel(upload_path)
    else:
        Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_path = '{}/static/report/xunjian/系统巡检报告'.format(Base_DIR)
        file_path = upload_path + str(datetime.datetime.now().strftime('%Y%m%d')) + ".xls"
        df = pd.read_excel(file_path)
    sumint = len(df.index)
    print(sumint)
    df.rename(columns={'Unnamed: 0': '', 'Unnamed: 2': '', 'Unnamed: 3': '', 'Unnamed: 4': '', 'Unnamed: 5': '',
                       'Unnamed: 6': ''}, inplace=True)
    for i in range(3, 30):
        data = df.iloc[i, 3]
        if data.split(':')[0] == "http" or data.split(':')[0] == "https":
            # requese请求url,判断是否异常
            try:
                code = gethttp(data)
                if code == 200:
                    if timeflag():
                        df.iloc[i, 4] = "正常"
                    else:
                        df.iloc[i, 5] = "正常"
                else:
                    if timeflag():
                        df.iloc[i, 4] = "异常"
                    else:
                        df.iloc[i, 5] = "异常"
            except:
                if timeflag():
                    df.iloc[i, 4] = "异常"
                else:
                    df.iloc[i, 5] = "异常"
                continue
        elif data.split(':')[0] == "ftp":
            # ftp请求测试，判断是否异常
            if getftp(data):
                if timeflag():
                    df.iloc[i, 4] = "正常"
                else:
                    df.iloc[i, 5] = "正常"
            else:
                if timeflag():
                    df.iloc[i, 4] = "异常"
                else:
                    df.iloc[i, 5] = "异常"
                continue
    # 数据库
    for j in range(34, 44):
        ipdict = []
        toname = df.iloc[j, 1]
        toip = df.iloc[j, 2]
        ipdict.append((toname, toip))
        flag, tempdata = getdatebase(ipdict)
        print(flag)
        tempstr = ",".join(tempdata)
        print(tempstr)
        if 0 in flag:
            if timeflag():
                df.iloc[j, 4] = "异常"
            else:
                df.iloc[j, 5] = "异常"
            df.iloc[j, 6] = tempstr
        else:
            if timeflag():
                df.iloc[j, 4] = "正常"
            else:
                df.iloc[j, 5] = "正常"
            df.iloc[j, 6] = tempstr
    # 保存文件
    Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_path = '{}/static/report/xunjian/系统巡检报告'.format(Base_DIR)
    file_path = upload_path + str(datetime.datetime.now().strftime('%Y%m%d')) + ".xls"
    # file_path = "./files/系统巡检报告" + str(datetime.datetime.now().strftime('%Y%m%d')) + ".xls"
    print(file_path)
    writer = pd.ExcelWriter(file_path, engine="xlsxwriter")
    df.to_excel(writer, index=False)  # index=False不写入序号
    writer.save()


if __name__ == "__main__":
    run()
