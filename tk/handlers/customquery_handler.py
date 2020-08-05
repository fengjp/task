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
from models.task import model_to_dict, CustomQuery
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from settings import CUSTOM_DB_INFO
from libs.aes_coder import encrypt, decrypt


class QueryConfDoSqlFileHandler(BaseHandler):
    def get(self):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []
        with DBContext('r') as session:
            query_info = session.query(CustomQuery).filter(CustomQuery.id == value).first()

        dblinkId = query_info.dblinkId
        CUSTOM_DB_INFO['db'] = 'codo_cmdb'
        mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
        # 获取数据库源 连接地址
        select_db = 'select db_type, db_host, db_port, db_user, db_pwd from asset_db where id = {}'.format(dblinkId)
        db_info = mysql_conn.query(select_db)

        if len(db_info) > 0:
            db = db_info[0]
            db_obj = {}
            db_obj['host'] = db[1]
            db_obj['port'] = int(db[2])
            db_obj['user'] = db[3]
            db_obj['passwd'] = decrypt(db[4])
            db_obj['db'] = query_info.database
            sql = query_info.sql

            if query_info.user:
                db_obj['user'] = query_info.user

            if query_info.password:
                db_obj['passwd'] = decrypt(query_info.password)

            sql = re.sub('update|drop', '', sql, 0, re.I)
            # ins_log.read_log('info', db_obj)
            res = []
            if db[0] == 'mysql':
                mysql_conn = MysqlBase(**db_obj)
                res = mysql_conn.query(sql)

            if db[0] == 'oracle':
                oracle_conn = OracleBase(**db_obj)
                res = oracle_conn.query(sql)
            ins_log.read_log('info', res)
            if res:
                try:
                    colnames = json.loads(query_info.colnames)
                    colalarms = json.loads(query_info.colalarms)
                    # 增加状态列
                    if len(colalarms) > 0:
                        colnames.append({'col': "target", 'name': "指标"})
                    dict_key = []
                    for i in colnames:
                        dict_key.append(i['col'])

                    for i in res:
                        _d = dict(zip(dict_key, i))
                        for selColObj in colalarms:
                            selCol = selColObj['selCol']
                            if selCol in _d:
                                dbval = _d[selCol]
                                # 判断指标值
                                subColList = selColObj['subColList']
                                subColList = sorted(subColList, key=lambda x: x['alarmVal'], reverse=True)
                                for alarmObj in subColList:
                                    sign = alarmObj['sign']
                                    alarmVal = alarmObj['alarmVal']
                                    if sign == '>' and dbval > alarmVal:
                                        _d['target'] = alarmObj['alarmType']
                                    if sign == '<' and dbval < alarmVal:
                                        _d['target'] = alarmObj['alarmType']
                                    if sign == '>=' and dbval >= alarmVal:
                                        _d['target'] = alarmObj['alarmType']
                                    if sign == '<=' and dbval <= alarmVal:
                                        _d['target'] = alarmObj['alarmType']
                                    if sign == '=' and dbval == alarmVal:
                                        _d['target'] = alarmObj['alarmType']

                        dict_list.append(_d)
                except Exception as e:
                    ins_log.read_log('info', e)
                    dict_list = []

                return self.write(dict(code=0, msg='获取成功', data=dict_list))

        return self.write(dict(code=-1, msg='获取失败', data=[]))


class QueryConfForshowFileHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []
        with DBContext('r') as session:
            if key and value:
                count = session.query(CustomQuery).filter_by(**{key: value}).count()
                query_info = session.query(CustomQuery).filter_by(**{key: value}).all()
            else:
                count = session.query(CustomQuery).count()
                query_info = session.query(CustomQuery).all()

        for msg in query_info:
            if msg.status == '0':
                continue
            data_dict = {}
            data_dict['colnames'] = json.loads(msg.colnames)
            colalarms = json.loads(msg.colalarms)
            if len(colalarms) > 0:
                data_dict['colnames'].append({'col': "target", 'name': "指标"})
            data_dict['id'] = msg.id
            data_dict['title'] = msg.title
            data_dict['timesTy'] = msg.timesTy
            data_dict['timesTyVal'] = msg.timesTyVal
            dict_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', data=dict_list, count=count))


class QueryConfFileHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []
        with DBContext('r') as session:
            if key and value:
                count = session.query(CustomQuery).filter_by(**{key: value}).count()
                query_info = session.query(CustomQuery).filter_by(**{key: value}).order_by(CustomQuery.id.desc()).all()
            else:
                count = session.query(CustomQuery).count()
                query_info = session.query(CustomQuery).order_by(CustomQuery.id.desc()).all()

        db_obj = {}
        if len(query_info) > 0:
            CUSTOM_DB_INFO['db'] = 'codo_cmdb'
            mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
            # 获取数据库源 连接地址
            select_sql = 'select id, db_code from asset_db'
            db_name = mysql_conn.query(select_sql)
            for i in db_name:
                db_obj[i[0]] = i[1]

        for msg in query_info:
            data_dict = model_to_dict(msg)
            data_dict['colnames'] = json.loads((data_dict['colnames']))
            data_dict['colalarms'] = json.loads((data_dict['colalarms']))
            data_dict['create_time'] = str(data_dict['create_time'])
            data_dict['update_time'] = str(data_dict['update_time'])
            if data_dict['timesTy'] == 'timesTy1':
                data_dict['timesTy1Val'] = data_dict['timesTyVal']
            else:
                data_dict['timesTy2Val'] = data_dict['timesTyVal']

            data_dict['dblinkIdNa'] = db_obj.get(data_dict['dblinkId'], '')

            dict_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', data=dict_list, count=count))

    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        title = data.get('title')
        dblinkId = data.get('dblinkId')
        database = data.get('database')
        sql = data.get('sql')
        colnames = data.get('colnames')
        timesTy = data.get('timesTy')
        timesTy1Val = data.get('timesTy1Val')
        timesTy2Val = data.get('timesTy2Val')
        colalarms = data.get('colalarms')
        user = data.get('user')
        password = data.get('password')

        if timesTy == 'timesTy1':
            timesTyVal = timesTy1Val
        else:
            timesTyVal = timesTy2Val

        if not title:
            return self.write(dict(code=-1, msg='标题不能为空'))

        with DBContext('r') as session:
            exist_id = session.query(CustomQuery.id).filter(CustomQuery.title == title).first()

        if exist_id:
            return self.write(dict(code=-2, msg='不要重复记录'))

        # 加密密码
        password = encrypt(password)

        sql = re.sub('update|drop', '', sql, 0, re.I)

        with DBContext('w', None, True) as session:
            new_query = CustomQuery(title=title, dblinkId=int(dblinkId), database=database, sql=sql,
                                    colnames=json.dumps(colnames), timesTy=timesTy, timesTyVal=timesTyVal,
                                    colalarms=json.dumps(colalarms), user=user, password=password
                                    )
            session.add(new_query)

        return self.write(dict(code=0, msg='添加成功'))

    def put(self):
        data = json.loads(self.request.body.decode("utf-8"))
        title = data.get('title')
        dblinkId = data.get('dblinkId')
        database = data.get('database')
        sql = data.get('sql')
        colnames = data.get('colnames')
        timesTy = data.get('timesTy')
        timesTy1Val = data.get('timesTy1Val')
        timesTy2Val = data.get('timesTy2Val')
        queryId = data.get('id')
        colalarms = data.get('colalarms')
        user = data.get('user')
        password = data.get('password')

        if timesTy == 'timesTy1':
            timesTyVal = timesTy1Val
        else:
            timesTyVal = timesTy2Val

        if not title:
            return self.write(dict(code=-1, msg='标题不能为空'))

        # 加密密码
        password = encrypt(password)

        with DBContext('w', None, True) as session:
            session.query(CustomQuery).filter(CustomQuery.id == int(queryId)).update(
                {CustomQuery.title: title, CustomQuery.dblinkId: int(dblinkId),
                 CustomQuery.database: database, CustomQuery.sql: sql,
                 CustomQuery.colnames: json.dumps(colnames), CustomQuery.timesTy: timesTy,
                 CustomQuery.timesTyVal: timesTyVal, CustomQuery.colalarms: json.dumps(colalarms),
                 CustomQuery.user: user, CustomQuery.password: password,
                 }, )

        return self.write(dict(code=0, msg='编辑成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id')

        with DBContext('w', None, True) as session:
            if id:
                session.query(CustomQuery).filter(CustomQuery.id == id).delete(synchronize_session=False)
                session.commit()
            else:
                return self.write(dict(code=1, msg='关键参数不能为空'))

        self.write(dict(code=0, msg='删除成功'))

    def patch(self, *args, **kwargs):
        """禁用、启用"""
        data = json.loads(self.request.body.decode("utf-8"))
        query_id = str(data.get('query_id', None))
        msg = '不存在'

        if not query_id:
            return self.write(dict(code=-1, msg='不能为空'))

        with DBContext('r') as session:
            query_status = session.query(CustomQuery.status).filter(CustomQuery.id == query_id).first()
        if not query_status:
            return self.write(dict(code=-2, msg=msg))

        if query_status[0] == '1':
            msg = '禁用成功'
            new_status = '0'

        elif query_status[0] == '0':
            msg = '启用成功'
            new_status = '1'
        else:
            new_status = '1'

        with DBContext('w', None, True) as session:
            session.query(CustomQuery).filter(CustomQuery.id == query_id).update(
                {CustomQuery.status: new_status})

        return self.write(dict(code=0, msg=msg))


customquery_urls = [
    (r"/v1/queryConf/", QueryConfFileHandler),
    (r"/v1/queryConfForshow/", QueryConfForshowFileHandler),
    (r"/v1/queryConf/do_sql/", QueryConfDoSqlFileHandler),
]

if __name__ == "__main__":
    pass
