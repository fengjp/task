#!/usr/bin/env python
# -*-coding:utf-8-*-
import json
import os
import re
from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from websdk.cache_context import cache_conn
from websdk.web_logs import ins_log
from sqlalchemy import func
from models.certdata import model_to_dict, CertDataUpLoadLog, CertDataUpLoadError, CertDataDownLoadError
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from libs.aes_coder import encrypt, decrypt
import traceback
import datetime


class CertDataFileHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        start_date = self.get_argument('start_date', default='', strip=True)
        end_date = self.get_argument('end_date', default='', strip=True)
        dict_list = []
        query_info = []
        count = 0

        start_date_str = start_date + " 00:00:00"
        end_date_str = end_date + " 23:59:59"

        if key == 'dataAll':
            with DBContext('r') as session:
                resdata = {}
                conditions = []
                conditions.append(CertDataUpLoadLog.create_time >= start_date_str)
                conditions.append(CertDataUpLoadLog.create_time <= end_date_str)
                today_send = session.query(func.sum(CertDataUpLoadLog.success)).filter(*conditions).scalar()
                all_send = session.query(func.sum(CertDataUpLoadLog.total)).scalar()
                resdata['sumUpLoad'] = int(all_send) if all_send else 0
                resdata['todayUpLoad'] = int(today_send) if today_send else 0
                resdata['todayDownLoad'] = 0

                try:
                    sql = '''
                    select sum(cnt) from (
                        select count(*) cnt from up_pro_accept_v4_unqbak
                        where recordtime >= to_date('{stime}', 'yyyy-mm-dd hh24:mi:ss')
                        and recordtime <= to_date('{etime}', 'yyyy-mm-dd hh24:mi:ss')
                        union all
                        select count(*) cnt from up_pro_process_v4_unqbak
                        where recordtime >= to_date('{stime}', 'yyyy-mm-dd hh24:mi:ss')
                        and recordtime <= to_date('{etime}', 'yyyy-mm-dd hh24:mi:ss')
                        union all
                        select count(*) cnt from up_pro_result_v4_unqbak
                        where recordtime >= to_date('{stime}', 'yyyy-mm-dd hh24:mi:ss')
                        and recordtime <= to_date('{etime}', 'yyyy-mm-dd hh24:mi:ss')
                    )
                    '''.format(stime=start_date_str, etime=end_date_str)
                    db_obj = {}
                    db_obj['host'] = '10.40.30.98'
                    db_obj['port'] = 1521
                    db_obj['user'] = ''
                    db_obj['passwd'] = ''
                    db_obj['db'] = 'cspt'
                    db_list = ['bj_zhpt', 'bj_sgjj', 'bj_ddzxc']
                    for d in db_list:
                        db_obj['user'] = d
                        db_obj['passwd'] = d
                        oracle_conn = OracleBase(**db_obj)
                        res = oracle_conn.query(sql)
                        resdata['todayDownLoad'] += int(res[0][0])
                except Exception as e:
                    ins_log.read_log('error', e)
                    resdata['todayDownLoad'] = 0

                dict_list.append(resdata)

        if key == 'UpLoadLog':
            with DBContext('r') as session:
                conditions = []
                conditions.append(CertDataUpLoadLog.create_time >= start_date_str)
                conditions.append(CertDataUpLoadLog.create_time <= end_date_str)
                #count = session.query(CertDataUpLoadLog).filter(*conditions).count()
                query_info = session.query(CertDataUpLoadLog).filter(*conditions).order_by(
                    CertDataUpLoadLog.id.desc()).all()

        if key == 'DownLoadLog':
            try:
                sql = '''
                    select recordtime, cd_batch, error_msg from up_pro_accept_v4_unqbak
                    where recordtime >= to_date('{stime}', 'yyyy-mm-dd hh24:mi:ss')
                    and recordtime <= to_date('{etime}', 'yyyy-mm-dd hh24:mi:ss')
                    union all
                    select recordtime, cd_batch, error_msg from up_pro_process_v4_unqbak
                    where recordtime >= to_date('{stime}', 'yyyy-mm-dd hh24:mi:ss')
                    and recordtime <= to_date('{etime}', 'yyyy-mm-dd hh24:mi:ss')
                    union all
                    select recordtime, cd_batch, error_msg from up_pro_result_v4_unqbak
                    where recordtime >= to_date('{stime}', 'yyyy-mm-dd hh24:mi:ss')
                    and recordtime <= to_date('{etime}', 'yyyy-mm-dd hh24:mi:ss')
                    order by 1 desc
                '''.format(stime=start_date_str, etime=end_date_str)
                db_obj = {}
                db_obj['host'] = '10.40.30.98'
                db_obj['port'] = 1521
                db_obj['user'] = ''
                db_obj['passwd'] = ''
                db_obj['db'] = 'cspt'
                db_list = ['bj_zhpt', 'bj_sgjj', 'bj_ddzxc']
                for d in db_list:
                    db_obj['user'] = d
                    db_obj['passwd'] = d
                    oracle_conn = OracleBase(**db_obj)
                    res = oracle_conn.query(sql)
                    query_info.extend(res)
            except Exception as e:
                ins_log.read_log('error', e)

        if key == 'UpLoadError':
            with DBContext('r') as session:
                conditions = []
                conditions.append(CertDataUpLoadError.create_time >= start_date_str)
                conditions.append(CertDataUpLoadError.create_time <= end_date_str)
                #count = session.query(CertDataUpLoadError).filter(*conditions).count()
                query_info = session.query(CertDataUpLoadError).filter(*conditions).order_by(
                    CertDataUpLoadError.id.desc()).offset(0).limit(1000).all()

        if key == 'DownLoadError':
            with DBContext('r') as session:
                conditions = []
                conditions.append(CertDataDownLoadError.create_time >= start_date_str)
                conditions.append(CertDataDownLoadError.create_time <= end_date_str)
                #count = session.query(CertDataDownLoadError).filter(*conditions).count()
                query_info = session.query(CertDataDownLoadError).filter(*conditions).order_by(
                    CertDataDownLoadError.id.desc()).offset(0).limit(1000).all()

        for msg in query_info:
            if key == 'UpLoadLog':
                data_dict = {}
                data_dict['total'] = msg.total
                data_dict['success'] = msg.success
                data_dict['topic'] = msg.topic
                data_dict['failed'] = msg.failed
                data_dict['extra'] = msg.extra if msg.extra else ''
                data_dict['create_time'] = str(msg.create_time)
                dict_list.append(data_dict)

            if key == 'DownLoadLog':
                data_dict = {}
                data_dict['create_time'] = str(msg[0])
                data_dict['cd_batch'] = msg[1]
                data_dict['error_msg'] = msg[2]
                dict_list.append(data_dict)

            if key == 'UpLoadError':
                data_dict = {}
                data_dict['topic'] = msg.topic
                data_dict['data'] = msg.data
                data_dict['create_time'] = str(msg.create_time)
                dict_list.append(data_dict)

            if key == 'DownLoadError':
                data_dict = {}
                data_dict['topic'] = msg.topic
                data_dict['data'] = msg.data
                data_dict['create_time'] = str(msg.create_time)
                dict_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', data=dict_list, count=count))


certdata_urls = [
    (r"/v1/getcertdata/", CertDataFileHandler),
]

if __name__ == "__main__":
    pass
