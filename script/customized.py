#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import sys
_op = os.path.dirname
cwdir = _op(os.path.abspath(__file__))
project_path = _op(_op(os.path.abspath(__file__)))
app_path = _op(project_path)
sys.path.insert(0, project_path)

from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from websdk.cache_context import cache_conn
from websdk.web_logs import ins_log
from sqlalchemy import or_, and_
from settings import CUSTOM_DB_INFO
from libs.server.server_common import *
from models.task import Customized,model_to_dict
import datetime
from libs.aes_coder import encrypt, decrypt
import pandas as pd
import copy
import traceback
# from multiprocessing import Process
from multiprocessing import Pool

def getdatebase(datebase_name,table_name):
    # CUSTOM_DB_INFO['db'] = 'codo_task'
    CUSTOM_DB_INFO['db'] = datebase_name
    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
    # 获取数据库源 连接地址
    # select_db = 'select * from customizedList'
    select_db = 'select * from  '   +  table_name
    db_info = mysql_conn.query(select_db)
    return db_info
def toexcel(all_customized_list,asset_date,temp_dict):
    for j in all_customized_list:
        for i in asset_date:
            if str(i[0]) == j[2]:  # 数据源id相等
                if len(j[3]) <= 0:  #库名
                    j[3] = i[3]
                CUSTOM_DB_INFO = dict(
                    host=i[6],
                    port=i[8],
                    user=i[9],
                    passwd=decrypt(i[10]),
                    db=j[3]
                )
                try:
                    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
                    toid = int(j[4])
                    db_data = mysql_conn.query(temp_dict[toid])
                except:
                    traceback.print_exc()
                # ins_log.read_log('info', "11111111111111111111111111111111111111")
                # ins_log.read_log('info', db_data)
                # ins_log.read_log('info', "11111111111111111111111111111111111111")
                db_data_list = []
                for g in db_data:
                    db_data_list.append(list(g))

                # 解析excel表头
                j[1].split('|')
                temp_copy = copy.deepcopy(j[1])
                temp_copy2 = temp_copy.split('|')
                # 保存文件
                Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                upload_path = '{}/static/report/'.format(Base_DIR)
                upload_path =  upload_path + j[6]
                # 创建的目录
                if not os.path.exists(upload_path):
                    os.mkdir(upload_path)

                file_path = upload_path + '/' + j[0] + str(
                    datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')) + ".xls"

                writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
                df = pd.DataFrame(db_data_list, index=range(1, len(db_data_list) + 1), columns=temp_copy2)
                df.to_excel(writer, encoding='utf-8', sheet_name='Sheet')
                writer.save()


class Customized_list(BaseHandler):
    def run():
        #定时表数据
        temp_dict = {}
        customizedList_date =getdatebase("codo_task","customizedList")#执行时间表
        AssetSql_date = getdatebase("codo_cmdb", "asset_sql")#sql语句表
        asset_date = getdatebase("codo_cmdb", "asset_db")#数据库源

        if len(AssetSql_date) > 0:
            for ass_id ,ass_name,ass_sqlstr, asse_remarks,ass_username,db_ctime in  AssetSql_date:
                temp_dict[ass_id] = ass_sqlstr

        #获取当前日期星期几
        d = datetime.datetime.today()  # 获取当前日期时间
        today_week = d.isoweekday()  # 获取时间周几
        ins_log.read_log('info', "11111111111111111111111111111111111111")
        ins_log.read_log('info', today_week)
        ins_log.read_log('info', "11111111111111111111111111111111111111")
        now = datetime.datetime.now()
        temp_time = now.strftime('%H:%M')
        #筛选当前要执行的sql
        all_customized_list = []
        if len(customizedList_date) > 0:
            for id ,db_title,db_header,dbname_id,dbname,db_id,db_cycle ,db_time,db_download_dir,db_ctime in  customizedList_date:
                if len(list(db_cycle)) <= 0: #当没有选择执行周期
                    if str(temp_time) ==  str(db_time): #当前需要执行的sql
                        all_customized_list.append([db_title,db_header,dbname_id,dbname,db_id,db_cycle,db_download_dir, db_time])
                elif  str(today_week) in  list(db_cycle):
                    if str(temp_time) ==  str(db_time): #当前需要执行的sql
                        all_customized_list.append([db_title,db_header,dbname_id,dbname,db_id,db_cycle,db_download_dir, db_time])
        #执行sql
        if len(all_customized_list) ==1: #一条数据时
            toexcel(all_customized_list, asset_date,temp_dict)
        if len(all_customized_list) >1:
            p = Pool()#创建进程池
            for c in all_customized_list: #多条数据时（多进程）
                customized_list = [c]
                # target是目标函数，args是位置参数，必须是元组类型，kwargs是关键字参数，必须是字典类型
                p.apply_async(toexcel, args=(customized_list, asset_date,temp_dict))  # 创建第一个进程
                # toexcel(customized_list, asset_date,temp_dict)
            p.close()
            p.join()


if __name__ == "__main__":
    temp  =  Customized_list
    temp.run()
