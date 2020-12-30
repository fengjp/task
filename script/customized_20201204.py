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
from models.task import Customized, model_to_dict
import datetime
from libs.aes_coder import encrypt, decrypt
import pandas as pd
import copy
import traceback
# from multiprocessing import Process
from multiprocessing import Pool
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase


def getdatebase(datebase_name, select_str):
    CUSTOM_DB_INFO['db'] = datebase_name
    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
    db_info = mysql_conn.query(select_str)
    return db_info


def toexcel(all_customized_list, asset_date, AssetSql_date):
    for j in all_customized_list: # 执行时间表
        for q_id, q_header, q_dbname_id, q_totype, q_sqlstr in AssetSql_date:  # sql语句表
            if q_id == int(j[1]): # 脚本id相等
                    for s_id,s_db_host,s_db_port,s_db_user,s_db_pwd,s_db_type,s_db_instance in asset_date: # 数据库源
                        if str(s_id) == q_dbname_id:  # 数据源id相等
                            CUSTOM_DB_INFO = dict(
                                host=s_db_host,
                                port=s_db_port,
                                user=s_db_user,
                                passwd=decrypt(s_db_pwd),
                                db=s_db_instance # 库名
                            )
                            try:
                                if s_db_type == "mysql":
                                    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
                                    db_data = mysql_conn.query(q_sqlstr)
                                if s_db_type == "oracle":
                                    oracle_conn = OracleBase(**CUSTOM_DB_INFO)
                                    db_data = oracle_conn.query(q_sqlstr)
                            except:
                                traceback.print_exc()

                            db_data_list = []
                            for g in db_data:
                                db_data_list.append(list(g))

                            # 解析excel表头
                            # q_header.split('|')
                            temp_copy = copy.deepcopy(q_header)
                            temp_copy2 = temp_copy.split('|')

                            ins_log.read_log('info', "11111111111111111111111111111111111111")
                            ins_log.read_log('info', temp_copy2)
                            ins_log.read_log('info', "11111111111111111111111111111111111111")
                            # 保存文件
                            Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                            upload_path = '{}/static/report/'.format(Base_DIR)
                            upload_path = upload_path + j[3]
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
        # 定时表数据
        temp_dict = {}
        sql_str = ""
        sql_str = "select totitle,dbid,cycle,times,download_dir,start_end  from  customizedList"
        customizedList_date = getdatebase("codo_task", sql_str)  # 执行时间表
        sql_str = ""
        sql_str = "select id,header,dbname_id,totype,sqlstr  from  asset_sql   where   totype='sql'"
        AssetSql_date = getdatebase("codo_cmdb", sql_str)  # sql语句表
        sql_str = ""
        sql_str = "select id,db_host,db_port,db_user,db_pwd,db_type,db_instance  from  asset_db"
        asset_date = getdatebase("codo_cmdb",sql_str)  # 数据库源

        # 获取当前日期星期几
        d = datetime.datetime.today()  # 获取当前日期时间
        today_week = d.isoweekday()  # 获取时间周几

        now = datetime.datetime.now()
        temp_time = now.strftime('%H:%M')
        temp_time_date = now.strftime('%Y%m%d')
        # 筛选当前要执行的sql
        all_customized_list = []
        if len(customizedList_date) > 0:
            for db_title,db_id, db_cycle, db_time, db_download_dir,start_end in customizedList_date:
                if len(str(start_end)) == 8 or len(str(start_end)) == 2:
                    if str(db_cycle) == '[]' or len(str(db_cycle)) == 0:  # 当没有选择执行周期
                        if str(temp_time) == str(db_time):  # 当前需要执行的sql
                            all_customized_list.append(
                                [db_title,  db_id, db_cycle, db_download_dir, db_time])
                    elif str(today_week) in list(db_cycle):
                        if str(temp_time) == str(db_time):  # 当前需要执行的sql
                            all_customized_list.append(
                                [db_title, db_id, db_cycle, db_download_dir, db_time])
                else:
                    if int(start_end[2:12].replace('-', '')) <= int(temp_time_date) and int(temp_time_date) <= int(start_end[16:26].replace('-', '')):
                        if str(db_cycle) == '[]' or len(str(db_cycle)) == 0:  # 当没有选择执行周期
                            if str(temp_time) == str(db_time):  # 当前需要执行的sql
                                all_customized_list.append(
                                    [db_title,  db_id, db_cycle, db_download_dir, db_time])
                        elif str(today_week) in list(db_cycle):
                            if str(temp_time) == str(db_time):  # 当前需要执行的sql
                                all_customized_list.append(
                                    [db_title,  db_id, db_cycle, db_download_dir, db_time])
        # 执行sql
        if len(all_customized_list) == 1:  # 一条数据时
            toexcel(all_customized_list, asset_date, AssetSql_date)
        if len(all_customized_list) > 1:
            p = Pool()  # 创建进程池
            for c in all_customized_list:  # 多条数据时（多进程）
                customized_list = [c]
                # target是目标函数，args是位置参数，必须是元组类型，kwargs是关键字参数，必须是字典类型
                p.apply_async(toexcel, args=(customized_list, asset_date, AssetSql_date))  # 创建第一个进程
                # toexcel(customized_list, asset_date,AssetSql_date)
            p.close()
            p.join()


if __name__ == "__main__":
    temp = Customized_list
    temp.run()
