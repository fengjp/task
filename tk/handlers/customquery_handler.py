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
from models.task import model_to_dict, CustomQuery, CustomTmp, CustomGroup, CustomQuerySub, CustomZdLink, CustomQueryLog
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from settings import CUSTOM_DB_INFO
from libs.aes_coder import encrypt, decrypt
from collections import Counter
import traceback
import datetime, time
import requests
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from websdk.cache_context import cache_conn

# typeObj: [
#     {'id': 0, 'name': '正常'},
#     {'id': 1, 'name': '一般'},
#     {'id': 2, 'name': '严重'},
#     {'id': 3, 'name': '致命'},
# ]

TypeObj = {
    '未知': -1,
    '正常': 0,
    '一般': 1,
    '严重': 2,
    '致命': 3,
}


def getzdlink(lkid):
    zdlink = ''
    with DBContext('r') as session:
        res = session.query(CustomZdLink.link).filter(CustomZdLink.id == int(lkid)).all()
        if len(res) > 0:
            zdlink = res[0][0]
    return zdlink


def set_query_into_redis(met, data, ty='zongdui'):
    # ins_log.read_log('info', data)
    redis_conn = cache_conn()
    if met == 'post':
        data['create_time'] = str(datetime.datetime.now())
        data['update_time'] = ''
        data['status'] = '1'

    if met == 'put':
        data['update_time'] = str(datetime.datetime.now())
        data['status'] = '1'

    query_key = bytes(data['title'] + '__' + ty, encoding='utf-8')

    if met == 'delete':
        redis_conn.delete(query_key)
        redis_conn.srem('query_list', query_key)

    elif met == 'patch':
        new_status = data['new_status']
        redis_conn.hmset(query_key, {'status': new_status})

    else:
        if data['timesTy'] == 'timesTy1':
            data['next_time'] = data['timesTy1Val'] * 60 + int(time.time())

        if data['timesTy'] == 'timesTy2':
            s1 = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            s2 = data['timesTy2Val'] + ':00'
            timeArray = time.strptime('%s %s' % (s1, s2), "%Y-%m-%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray))
            data['next_time'] = timeStamp

        redis_conn.hmset(query_key, data)
        redis_conn.sadd('query_list', query_key)


class QueryConfDoSqlFileHandler(BaseHandler):
    executor = ThreadPoolExecutor(10)

    @gen.coroutine
    def get(self):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []
        errormsg = ''
        # 总队执行
        if key == 'id':
            db_info = []
            try:
                with DBContext('r') as session:
                    query_info = session.query(CustomQuery).filter(CustomQuery.id == value).first()

                if query_info.type == 'sql':
                    dblinkId = query_info.dblinkId
                    CUSTOM_DB_INFO['db'] = 'codo_cmdb'
                    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
                    # 获取数据库源 连接地址
                    select_db = 'select db_type, db_host, db_port, db_user, db_pwd, db_instance from asset_db where id = {}'.format(
                        dblinkId)
                    db_info = mysql_conn.query(select_db)

                elif query_info.type == 'urls':
                    query_key = bytes(query_info.title + '__zongdui_res', encoding='utf-8')
                    res = self.getRedisData(query_key)
                    return self.write(res)

            except:
                errormsg = '获取数据库源连接信息失败'
                return self.write(dict(code=-1, msg='获取失败', errormsg=errormsg, data=[]))

            if len(db_info) > 0:
                query_key = bytes(query_info.title + '__zongdui_res', encoding='utf-8')
                res = self.getRedisData(query_key)
                # res = yield self.getData(query_info, db_info)
                return self.write(res)

        # 支队执行
        if key == 'ip':
            # res = yield self.getSubData(value)
            query_key = bytes(value + '__zhidui_res', encoding='utf-8')
            res = self.getRedisData(query_key)
            return self.write(res)

        return self.write(dict(code=-1, msg='获取失败', errormsg=errormsg, data=[], count={}))

    @run_on_executor
    def getData(self, query_info, db_info):
        dict_list = []
        errormsg = ''
        db = db_info[0]
        db_obj = {}
        db_obj['host'] = db[1]
        db_obj['port'] = int(db[2])
        db_obj['user'] = db[3]
        db_obj['passwd'] = decrypt(db[4])
        if query_info.database:
            db_obj['db'] = query_info.database
        else:
            db_obj['db'] = db[5]
        sql = query_info.sql

        if query_info.user:
            db_obj['user'] = query_info.user

        if query_info.password:
            db_obj['passwd'] = decrypt(query_info.password)

        sql = re.sub('update|drop', '', sql, 0, re.I)
        # ins_log.read_log('info', db_obj)
        res = []
        try:
            if db[0] == 'mysql':
                mysql_conn = MysqlBase(**db_obj)
                res = mysql_conn.query(sql)

            if db[0] == 'oracle':
                oracle_conn = OracleBase(**db_obj)
                res = oracle_conn.query(sql)
        except Exception as e:
            errormsg = '%s 数据库: 查询失败, %s' % (db_obj['host'], e)
            return dict(code=-1, msg='获取失败', errormsg=errormsg, data=[])

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
                        # 判断指标值 (同少取最少，同大取最大)
                        selCol = selColObj['selCol']
                        if selCol in _d:
                            dbval = _d[selCol]
                            if not dbval:
                                dbval = 0
                            subColList = selColObj['subColList']
                            subColList = sorted(subColList, key=lambda x: TypeObj[x['alarmType']], reverse=True)
                            # ins_log.read_log('info', subColList)
                            for alarmObj in subColList:
                                sign = alarmObj['sign']
                                alarmVal = alarmObj['alarmVal']
                                if sign == '>' and float(dbval) > float(alarmVal):
                                    _d['target'] = alarmObj['alarmType']
                                if sign == '<' and float(dbval) < float(alarmVal):
                                    _d['target'] = alarmObj['alarmType']
                                if sign == '>=' and float(dbval) >= float(alarmVal):
                                    _d['target'] = alarmObj['alarmType']
                                    break
                                if sign == '<=' and float(dbval) <= float(alarmVal):
                                    _d['target'] = alarmObj['alarmType']
                                if sign == '=' and float(dbval) == float(alarmVal):
                                    _d['target'] = alarmObj['alarmType']

                                if 'target' not in _d:
                                    _d['target'] = '未知'
                    # ins_log.read_log('info', _d)
                    dict_list.append(_d)

                if len(colalarms) > 0:
                    dict_list.sort(key=lambda x: TypeObj[x['target']], reverse=True)
                    countObj = dict(Counter([i['target'] for i in dict_list]))
                else:
                    countObj = {}

            except Exception as e:
                traceback.print_exc()
                errormsg = '字段格式错误'
                return dict(code=-2, msg='获取失败', errormsg=errormsg, data=[])

            # 转换 时间类型字段
            for _d in dict_list:
                for k, v in _d.items():
                    if isinstance(v, datetime.datetime):
                        _d[k] = v.strftime("%Y-%m-%d %H:%M:%S")

            return dict(code=0, msg='获取成功', errormsg=errormsg, data=dict_list, count=countObj)
        else:
            return dict(code=-1, msg='获取失败', errormsg='没有数据库源', data=[], count={})

    @run_on_executor
    def getSubData(self, value):
        zdlink = value.split('|')[0]
        qid = value.split('|')[-1]
        try:
            url = 'http://' + zdlink + '/doSql/?qid=' + qid
            try:
                res = requests.get(url, timeout=3)
                if res.text:
                    res_data = json.loads(res.text)
                    if res_data['code'] == 0:
                        dict_list = res_data.get('data', [])
                        countObj = res_data.get('count', {})
                        errormsg = res_data.get('errormsg', '')
                        return dict(code=0, msg='获取成功', errormsg=errormsg, data=dict_list, count=countObj)
                    else:
                        errormsg = res_data['errormsg']
                        return dict(code=-1, msg='获取失败', errormsg=errormsg, data=[], count={})
                else:
                    errormsg = '%s' % res
                    return dict(code=-1, msg='获取失败', errormsg=errormsg, data=[], count={})
            except Exception as e:
                # traceback.print_exc(e)
                errormsg = '网络超时'
                return dict(code=-1, msg='获取失败', errormsg=errormsg, data=[], count={})

        except Exception as e:
            errormsg = e
            return dict(code=-1, msg='获取失败', errormsg=errormsg, data=[], count={})

    def getRedisData(self, key):
        try:
            redis_conn = cache_conn()
            data = redis_conn.hgetall(key)
            new_data = {}
            for k, v in data.items():
                new_data[str(k, 'utf8')] = str(v, 'utf8')
            new_data = new_data['res']
        except:
            new_data = {}
        return new_data


class QueryConfForshowFileHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []

        try:
            tids = [d['id'] for d in json.loads(value)]
        except:
            tids = []
        # ins_log.read_log('info', tids)
        # 总队配置
        with DBContext('r') as session:
            if key and value and key != 'tid':
                # count = session.query(CustomQuery).filter_by(**{key: value}).count()
                query_info = session.query(CustomQuery).filter_by(**{key: value}).all()
            elif key == 'tid':
                # count = session.query(CustomQuery).filter(CustomQuery.id.in_(tids)).count()
                query_info = session.query(CustomQuery).filter(CustomQuery.id.in_(tids)).all()
            else:
                # count = session.query(CustomQuery).count()
                query_info = session.query(CustomQuery).all()

        redis_conn = cache_conn()

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
            data_dict['seq'] = msg.seq
            data_dict['groupID'] = json.loads(msg.groupID) if msg.groupID else []
            data_dict['group1stNa'] = self.getGroupInfo(data_dict['groupID'][0])[0]
            data_dict['group1stSeq'] = self.getGroupInfo(data_dict['groupID'][0])[1]
            data_dict['group2ndNa'] = self.getGroupInfo(data_dict['groupID'][1])[0]
            data_dict['group2ndSeq'] = self.getGroupInfo(data_dict['groupID'][1])[1]
            data_dict['next_time'] = self.next_time(redis_conn, data_dict['title'], 'zongdui')
            data_dict['query_ty'] = 0
            dict_list.append(data_dict)

        # 支队配置
        with DBContext('r') as session:
            query_info = session.query(CustomQuerySub).all()

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
            data_dict['seq'] = msg.seq
            data_dict['groupID'] = json.loads(msg.groupID) if msg.groupID else []
            data_dict['group1stNa'] = self.getGroupInfo(data_dict['groupID'][0])[0]
            data_dict['group1stSeq'] = self.getGroupInfo(data_dict['groupID'][0])[1]
            data_dict['group2ndNa'] = msg.groupName
            data_dict['group2ndSeq'] = msg.group2ndSeq
            data_dict['zdlink'] = getzdlink(msg.zdlinkID)
            data_dict['qid'] = msg.qid
            data_dict['next_time'] = self.next_time(redis_conn, data_dict['title'], 'zhidui')
            data_dict['query_ty'] = 1
            dict_list.append(data_dict)

        dict_list.sort(key=lambda x: x['seq'])
        return self.write(dict(code=0, msg='获取成功', data=dict_list))

    def next_time(self, redis_conn, title, ty):
        query_key = bytes(title + '__' + ty, encoding='utf-8')
        next_time = redis_conn.hget(query_key, 'next_time')
        if next_time != None:
            next_time = int(next_time)
        else:
            next_time = 0
        return next_time

    def getGroupInfo(self, gid):
        name = ''
        seq = -1
        try:
            with DBContext('r') as session:
                groupName = session.query(CustomGroup.groupName, CustomGroup.groupSeq).filter(
                    CustomGroup.id == int(gid)).all()
                if len(groupName) > 0:
                    # ins_log.read_log('info', groupName)
                    name = groupName[0][0]
                    seq = groupName[0][1]
        except:
            name = ''
            seq = -1
        return [name, seq]


class QueryConfFileHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []
        with DBContext('r') as session:
            if key and value and key != 'isTmp':
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

        if key == 'isTmp':
            for msg in query_info:
                data_dict = {}
                data_dict['id'] = msg.id
                data_dict['title'] = msg.title
                data_dict['timesTy'] = msg.timesTy
                data_dict['timesTyVal'] = msg.timesTyVal
                if data_dict['timesTy'] == 'timesTy1':
                    data_dict['timesTy1Val'] = data_dict['timesTyVal']
                else:
                    data_dict['timesTy2Val'] = data_dict['timesTyVal']
                dict_list.append(data_dict)

        else:
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
                groupID = json.loads(data_dict['groupID']) if data_dict['groupID'] else ''
                data_dict['group1stID'] = groupID[0] if groupID else -1
                data_dict['group2ndID'] = groupID[1] if groupID else -1
                data_dict['group1stSeq'] = self.getGroupSeq(data_dict['group1stID'])
                data_dict['group2ndSeq'] = self.getGroupSeq(data_dict['group2ndID'])
                data_dict['urls'] = json.loads(data_dict['urls']) if data_dict['urls'] else []
                dict_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', data=dict_list, count=count))

    def getGroupSeq(self, gid):
        seq = -1
        with DBContext('r') as session:
            groupSeq = session.query(CustomGroup.groupSeq).filter(CustomGroup.id == int(gid)).all()
            if len(groupSeq) > 0:
                seq = groupSeq[0][0]
        return seq

    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        title = data.get('title')
        dblinkId = data.get('dblinkId', 0)
        database = data.get('database')
        sql = data.get('sql')
        colnames = data.get('colnames')
        timesTy = data.get('timesTy')
        timesTy1Val = data.get('timesTy1Val')
        timesTy2Val = data.get('timesTy2Val')
        colalarms = data.get('colalarms')
        user = data.get('user')
        password = data.get('password')
        description = data.get('description')
        seq = data.get('seq')
        group1stID = data.get('group1stID', '')
        group2ndID = data.get('group2ndID', '')
        group1stSeq = data.get('group1stSeq', 0)
        group2ndSeq = data.get('group2ndSeq', 0)
        ty = data.get('type', 'sql')
        urls = data.get('urls', [])

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

        if group1stID != '' and group2ndID != '':
            groupID = json.dumps([group1stID, group2ndID])
        else:
            group1stID = group2ndID = group1stSeq = group2ndSeq = 0
            groupID = json.dumps([group1stID, group2ndID])

        if len(urls) > 0:
            urls = json.dumps(urls)
        else:
            urls = ''

        # 加密密码
        password = encrypt(password)

        sql = re.sub('update|drop', '', sql, 0, re.I)

        if not dblinkId:
            dblinkId = 0

        with DBContext('w', None, True) as session:
            new_query = CustomQuery(title=title, dblinkId=int(dblinkId), database=database, sql=sql,
                                    colnames=json.dumps(colnames), timesTy=timesTy, timesTyVal=timesTyVal,
                                    colalarms=json.dumps(colalarms), user=user, password=password,
                                    description=description, seq=seq, groupID=groupID, type=ty, urls=urls,
                                    )
            session.add(new_query)

        # 更新分组排序号
        if group1stID:
            self.updateGroupSeq(group1stID, group1stSeq)
        if group2ndID:
            self.updateGroupSeq(group2ndID, group2ndSeq)

        set_query_into_redis('post', data)
        return self.write(dict(code=0, msg='添加成功'))

    def updateGroupSeq(self, gid, seq):
        with DBContext('w', None, True) as session:
            session.query(CustomGroup).filter(CustomGroup.id == int(gid)).update(
                {
                    CustomGroup.groupSeq: seq,
                }, )

    def put(self):
        data = json.loads(self.request.body.decode("utf-8"))
        title = data.get('title')
        dblinkId = data.get('dblinkId', 0)
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
        description = data.get('description')
        seq = data.get('seq')
        group1stID = data.get('group1stID', '')
        group2ndID = data.get('group2ndID', '')
        group1stSeq = data.get('group1stSeq', 0)
        group2ndSeq = data.get('group2ndSeq', 0)
        ty = data.get('type', 'sql')
        urls = data.get('urls', [])

        if timesTy == 'timesTy1':
            timesTyVal = timesTy1Val
        else:
            timesTyVal = timesTy2Val

        if not title:
            return self.write(dict(code=-1, msg='标题不能为空'))

        with DBContext('r') as session:
            old_password = session.query(CustomQuery.password).filter(CustomQuery.id == int(queryId)).first()[0]
            # ins_log.read_log('info', old_password)

        if group1stID != '' and group2ndID != '':
            groupID = json.dumps([group1stID, group2ndID])
        else:
            group1stID = group2ndID = group1stSeq = group2ndSeq = 0
            groupID = json.dumps([group1stID, group2ndID])

        if old_password != password:
            # 加密密码
            password = encrypt(password)

        if len(urls) > 0:
            urls = json.dumps(urls)
        else:
            urls = ''

        if not dblinkId:
            dblinkId = 0

        with DBContext('w', None, True) as session:
            session.query(CustomQuery).filter(CustomQuery.id == int(queryId)).update(
                {CustomQuery.title: title, CustomQuery.dblinkId: int(dblinkId),
                 CustomQuery.database: database, CustomQuery.sql: sql,
                 CustomQuery.colnames: json.dumps(colnames), CustomQuery.timesTy: timesTy,
                 CustomQuery.timesTyVal: timesTyVal, CustomQuery.colalarms: json.dumps(colalarms),
                 CustomQuery.user: user, CustomQuery.password: password, CustomQuery.description: description,
                 CustomQuery.seq: seq, CustomQuery.groupID: groupID, CustomQuery.type: ty,
                 CustomQuery.urls: urls,
                 }, )

        # 更新分组排序号
        if group1stID:
            self.updateGroupSeq(group1stID, group1stSeq)
        if group2ndID:
            self.updateGroupSeq(group2ndID, group2ndSeq)

        set_query_into_redis('put', data)
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

        set_query_into_redis('delete', data)
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
        data['new_status'] = new_status
        set_query_into_redis('patch', data)
        return self.write(dict(code=0, msg=msg))


class TmpFileHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        tmpList = []
        data_dict = {}
        with DBContext('r') as session:
            tmp_info = session.query(CustomTmp).order_by(CustomTmp.id.desc()).all()

        for msg in tmp_info:
            tmpList_dict = {}
            tmpList_dict['value'] = msg.id
            tmpList_dict['label'] = msg.tmpNa
            tmpList.append(tmpList_dict)

            if msg.username not in data_dict:
                data_dict[msg.username] = []

            _d = {}
            _d['id'] = msg.id
            _d['tmpNa'] = msg.tmpNa
            _d['username'] = msg.username
            _d['selectionAll'] = json.loads(msg.selectionAll)
            data_dict[msg.username].append(_d)

        return self.write(dict(code=0, msg='获取成功', tmpList=tmpList, data=data_dict))

    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        tmpNa = data.get('tmpNa')
        selectionAll = data.get('selectionAll')
        username = data.get('username')

        with DBContext('r') as session:
            exist_id = session.query(CustomTmp.id).filter(CustomTmp.tmpNa == tmpNa).first()

        if exist_id:
            return self.write(dict(code=-1, msg='标题重复'))

        with DBContext('w', None, True) as session:
            new_tmp = CustomTmp(
                tmpNa=tmpNa, selectionAll=json.dumps(selectionAll), username=username
            )
            session.add(new_tmp)

        return self.write(dict(code=0, msg='添加成功'))

    def put(self):
        data = json.loads(self.request.body.decode("utf-8"))
        tid = data.get('id')
        tmpNa = data.get('tmpNa')
        selectionAll = data.get('selectionAll')
        username = data.get('username')

        with DBContext('w', None, True) as session:
            session.query(CustomTmp).filter(CustomTmp.id == int(tid)).update(
                {
                    CustomTmp.tmpNa: tmpNa,
                    CustomTmp.selectionAll: json.dumps(selectionAll),
                    CustomTmp.username: username,
                }, )

        return self.write(dict(code=0, msg='编辑成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id')

        with DBContext('w', None, True) as session:
            if id:
                session.query(CustomTmp).filter(CustomTmp.id == id).delete(synchronize_session=False)
                session.commit()
            else:
                return self.write(dict(code=1, msg='关键参数不能为空'))

        self.write(dict(code=0, msg='删除成功'))


class GroupHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        groupObj = {}
        data_dict = []
        with DBContext('r') as session:
            group_info = session.query(CustomGroup).all()

        for msg in group_info:
            if msg.grouptype not in groupObj:
                groupObj[msg.grouptype] = []

            _d = {}
            _d['id'] = msg.id
            _d['name'] = msg.groupName
            groupObj[msg.grouptype].append(_d)

            _d = {}
            _d['id'] = msg.id
            _d['groupName'] = msg.groupName
            _d['grouptype'] = msg.grouptype
            _d['groupSeq'] = msg.groupSeq
            data_dict.append(_d)

        return self.write(dict(code=0, msg='获取成功', groupObj=groupObj, data=data_dict))

    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        groupName = data.get('groupName')
        grouptype = data.get('grouptype')
        groupSeq = data.get('groupSeq', 0)

        with DBContext('r') as session:
            exist_id = session.query(CustomGroup.id).filter(CustomGroup.groupName == groupName).first()

        if exist_id:
            return self.write(dict(code=-1, msg='组名重复'))

        with DBContext('w', None, True) as session:
            new_g = CustomGroup(
                groupName=groupName, grouptype=grouptype, groupSeq=groupSeq
            )
            session.add(new_g)

        return self.write(dict(code=0, msg='添加成功'))

    def put(self):
        data = json.loads(self.request.body.decode("utf-8"))
        tid = data.get('id')
        groupName = data.get('groupName')
        grouptype = data.get('grouptype')
        groupSeq = data.get('groupSeq')

        with DBContext('w', None, True) as session:
            session.query(CustomGroup).filter(CustomGroup.id == int(tid)).update(
                {
                    CustomGroup.groupName: groupName,
                    CustomGroup.grouptype: grouptype,
                    CustomGroup.groupSeq: groupSeq,
                }, )

        return self.write(dict(code=0, msg='编辑成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id')

        with DBContext('w', None, True) as session:
            if id:
                session.query(CustomGroup).filter(CustomGroup.id == id).delete(synchronize_session=False)
                session.commit()
            else:
                return self.write(dict(code=1, msg='id不能为空'))

        self.write(dict(code=0, msg='删除成功'))


class QuerySubConfHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []
        with DBContext('r') as session:
            if key and value and key != 'isTmp':
                count = session.query(CustomQuerySub).filter_by(**{key: value}).count()
                query_info = session.query(CustomQuerySub).filter_by(**{key: value}).order_by(
                    CustomQuerySub.id.desc()).all()
            else:
                count = session.query(CustomQuerySub).count()
                query_info = session.query(CustomQuerySub).order_by(CustomQuerySub.id.desc()).all()

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

            data_dict['dblinkIdNa'] = ''
            groupID = json.loads(data_dict['groupID']) if data_dict['groupID'] else ''
            data_dict['group1stID'] = groupID[0] if groupID else -1
            data_dict['group2ndID'] = groupID[1] if groupID else -1
            data_dict['group1stSeq'] = self.getGroupSeq(data_dict['group1stID'])
            data_dict['zdlink'] = getzdlink(data_dict['zdlinkID'])
            dict_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', data=dict_list, count=count))

    def getGroupSeq(self, gid):
        seq = -1
        with DBContext('r') as session:
            groupSeq = session.query(CustomGroup.groupSeq).filter(CustomGroup.id == int(gid)).all()
            if len(groupSeq) > 0:
                seq = groupSeq[0][0]
        return seq

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
        description = data.get('description')
        seq = data.get('seq')
        group1stID = data.get('group1stID')
        group2ndID = data.get('group2ndID')
        group1stSeq = data.get('group1stSeq')
        group2ndSeq = data.get('group2ndSeq')
        zdlinkID = data.get('linkId')
        groupName = data.get('groupName')

        if timesTy == 'timesTy1':
            timesTyVal = timesTy1Val
        else:
            timesTyVal = timesTy2Val

        if not dblinkId:
            dblinkId = -1

        if not title:
            return self.write(dict(code=-1, msg='标题不能为空'))

        with DBContext('r') as session:
            exist_id = session.query(CustomQuerySub.id).filter(CustomQuerySub.title == title).first()

        if exist_id:
            return self.write(dict(code=-2, msg='不要重复记录'))

        if group1stID != '' and group2ndID != '':
            groupID = json.dumps([group1stID, group2ndID])
        else:
            groupID = [0, 0]

        # 加密密码
        password = encrypt(password)

        sql = re.sub('update|drop', '', sql, 0, re.I)

        with DBContext('w', None, True) as session:
            new_query = CustomQuerySub(title=title, dblinkId=dblinkId, database=database, sql=sql,
                                       colnames=json.dumps(colnames), timesTy=timesTy, timesTyVal=timesTyVal,
                                       colalarms=json.dumps(colalarms), user=user, password=password,
                                       description=description, seq=seq, groupID=groupID, zdlinkID=zdlinkID,
                                       groupName=groupName, group2ndSeq=group2ndSeq,
                                       )
            session.add(new_query)

        # 更新分组排序号
        self.updateGroupSeq(group1stID, group1stSeq)
        data['zdlink'] = getzdlink(zdlinkID)
        set_query_into_redis('post', data, ty='zhidui')
        return self.write(dict(code=0, msg='添加成功'))

    def updateGroupSeq(self, gid, seq):
        with DBContext('w', None, True) as session:
            session.query(CustomGroup).filter(CustomGroup.id == int(gid)).update(
                {
                    CustomGroup.groupSeq: seq,
                }, )

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
        description = data.get('description')
        seq = data.get('seq')
        group1stID = data.get('group1stID')
        group2ndID = data.get('group2ndID')
        group1stSeq = data.get('group1stSeq')
        group2ndSeq = data.get('group2ndSeq')
        zdlinkID = data.get('linkId')
        groupName = data.get('groupName')

        if timesTy == 'timesTy1':
            timesTyVal = timesTy1Val
        else:
            timesTyVal = timesTy2Val

        if not title:
            return self.write(dict(code=-1, msg='标题不能为空'))

        with DBContext('r') as session:
            old_password = session.query(CustomQuerySub.password).filter(CustomQuerySub.id == int(queryId)).first()[0]
            # ins_log.read_log('info', old_password)

        if group1stID != '' and group2ndID != '':
            groupID = json.dumps([group1stID, group2ndID])
        else:
            groupID = [0, 0]

        if old_password != password:
            # 加密密码
            password = encrypt(password)

        with DBContext('w', None, True) as session:
            session.query(CustomQuerySub).filter(CustomQuerySub.id == int(queryId)).update(
                {CustomQuerySub.title: title, CustomQuerySub.dblinkId: int(dblinkId),
                 CustomQuerySub.database: database, CustomQuerySub.sql: sql,
                 CustomQuerySub.colnames: json.dumps(colnames), CustomQuerySub.timesTy: timesTy,
                 CustomQuerySub.timesTyVal: timesTyVal, CustomQuerySub.colalarms: json.dumps(colalarms),
                 CustomQuerySub.user: user, CustomQuerySub.password: password, CustomQuerySub.description: description,
                 CustomQuerySub.seq: seq, CustomQuerySub.groupID: groupID, CustomQuerySub.zdlinkID: zdlinkID,
                 CustomQuerySub.groupName: groupName, CustomQuerySub.group2ndSeq: group2ndSeq,
                 }, )

        # 更新分组排序号
        self.updateGroupSeq(group1stID, group1stSeq)
        data['zdlink'] = getzdlink(zdlinkID)
        set_query_into_redis('put', data, ty='zhidui')
        return self.write(dict(code=0, msg='编辑成功'))

    def patch(self, *args, **kwargs):
        """禁用、启用"""
        data = json.loads(self.request.body.decode("utf-8"))
        query_id = str(data.get('query_id', None))
        msg = '不存在'

        if not query_id:
            return self.write(dict(code=-1, msg='不能为空'))

        with DBContext('r') as session:
            query_status = session.query(CustomQuerySub.status).filter(CustomQuerySub.id == query_id).first()

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
            session.query(CustomQuerySub).filter(CustomQuerySub.id == query_id).update(
                {CustomQuerySub.status: new_status})
        data['new_status'] = new_status
        set_query_into_redis('patch', data, ty='zhidui')
        return self.write(dict(code=0, msg=msg))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id')

        with DBContext('w', None, True) as session:
            if id:
                session.query(CustomQuerySub).filter(CustomQuerySub.id == id).delete(synchronize_session=False)
                session.commit()
            else:
                return self.write(dict(code=1, msg='关键参数不能为空'))

        set_query_into_redis('delete', data, ty='zhidui')
        self.write(dict(code=0, msg='删除成功'))


class ZdLinkHandler(BaseHandler):
    '''
        支队连接
    '''

    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        linkList = []
        data_dict = []
        with DBContext('r') as session:
            query_info = session.query(CustomZdLink).all()

        for msg in query_info:
            _d = {}
            _d['id'] = msg.id
            _d['name'] = msg.name
            linkList.append(_d)

            _d = {}
            _d['id'] = msg.id
            _d['name'] = msg.name
            _d['link'] = msg.link
            data_dict.append(_d)

        return self.write(dict(code=0, msg='获取成功', linkList=linkList, data=data_dict))

    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        name = data.get('name')
        link = data.get('link')

        with DBContext('r') as session:
            exist_id = session.query(CustomZdLink.id).filter(CustomZdLink.name == name).first()

        if exist_id:
            return self.write(dict(code=-1, msg='名称重复'))

        with DBContext('w', None, True) as session:
            _new = CustomZdLink(
                name=name, link=link,
            )
            session.add(_new)

        return self.write(dict(code=0, msg='添加成功'))

    def put(self):
        data = json.loads(self.request.body.decode("utf-8"))
        tid = data.get('id')
        name = data.get('name')
        link = data.get('link')

        with DBContext('w', None, True) as session:
            session.query(CustomZdLink).filter(CustomZdLink.id == int(tid)).update(
                {
                    CustomZdLink.name: name,
                    CustomZdLink.link: link,
                }, )

        return self.write(dict(code=0, msg='编辑成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id')

        with DBContext('w', None, True) as session:
            if id:
                session.query(CustomZdLink).filter(CustomZdLink.id == id).delete(synchronize_session=False)
                session.commit()
            else:
                return self.write(dict(code=1, msg='id不能为空'))

        self.write(dict(code=0, msg='删除成功'))


class PushConfHandler(BaseHandler):
    '''
        下发配置到支队
    '''

    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        failed_list = []
        redis_conn = cache_conn()
        for payload in data:
            try:
                url = 'http://' + payload['zdlink'] + '/queryPushConf/'
                try:
                    res = requests.post(url, data=json.dumps(payload), timeout=3)
                except:
                    return self.write(dict(code=-1, msg='网络超时'))
                # 更新 qid
                if res.text:
                    res_data = json.loads(res.text)
                    if res_data['data']:
                        for id, qid in res_data['data'].items():
                            with DBContext('w', None, True) as session:
                                session.query(CustomQuerySub).filter(CustomQuerySub.id == int(id)).update(
                                    {CustomQuerySub.qid: qid},
                                )
                            redis_conn.hmset(bytes(payload['title'] + '__zhidui', encoding='utf-8'), {'qid': qid})
                    else:
                        title = payload['title']
                        failed_list.append(title)

            except Exception as e:
                ins_log.read_log('error', e)
        if len(failed_list) > 0:
            return self.write(dict(code=-1, msg=u'失败列表：%s' % failed_list))

        return self.write(dict(code=0, msg='success'))


class PullConfHandler(BaseHandler):
    '''
        从支队拉取配置
    '''

    def post(self):
        req_data = json.loads(self.request.body.decode("utf-8"))
        try:
            linkId = req_data.get('linkId')
            zdlink = getzdlink(linkId)
            url = 'http://' + zdlink + '/queryPullConf/'
            try:
                res = requests.get(url, params='', timeout=3)
            except requests.exceptions.ConnectTimeout:
                return self.write(dict(code=-1, msg='网络超时'))
            if res.text:
                redis_conn = cache_conn()
                res_data = json.loads(res.text)
                res_data = res_data['data']
                for data in res_data:
                    qid = data.get('qid', '')
                    title = data.get('title')
                    dblinkId = data.get('dblinkId')
                    database = data.get('database')
                    user = data.get('user')
                    password = data.get('password')
                    sql = data.get('sql')
                    colnames = data.get('colnames')
                    timesTy = data.get('timesTy')
                    timesTyVal = data.get('timesTyVal')
                    colalarms = data.get('colalarms')
                    status = data.get('status')
                    create_time = data.get('create_time')
                    update_time = data.get('update_time')
                    description = data.get('description')
                    seq = data.get('seq')
                    groupID = data.get('groupID')
                    zdlinkID = linkId
                    groupName = data.get('groupName', '')
                    group2ndSeq = data.get('group2ndSeq', 0)

                    with DBContext('r') as session:
                        exist_id = session.query(CustomQuerySub.id).filter(CustomQuerySub.title == title).first()

                    if exist_id:
                        exist_id = exist_id[0]
                        with DBContext('w', None, True) as session:
                            session.query(CustomQuerySub).filter(CustomQuerySub.id == int(exist_id)).update(
                                {
                                    CustomQuerySub.qid: qid,
                                    CustomQuerySub.title: title,
                                    CustomQuerySub.dblinkId: int(dblinkId),
                                    CustomQuerySub.database: database,
                                    CustomQuerySub.user: user,
                                    CustomQuerySub.password: password,
                                    CustomQuerySub.sql: sql,
                                    CustomQuerySub.colnames: colnames,
                                    CustomQuerySub.timesTy: timesTy,
                                    CustomQuerySub.timesTyVal: timesTyVal,
                                    CustomQuerySub.colalarms: colalarms,
                                    CustomQuerySub.status: status,
                                    CustomQuerySub.create_time: create_time,
                                    CustomQuerySub.update_time: update_time,
                                    CustomQuerySub.description: description,
                                    CustomQuerySub.seq: seq,
                                    CustomQuerySub.groupID: groupID,
                                    CustomQuerySub.groupName: groupName,
                                    CustomQuerySub.group2ndSeq: group2ndSeq,
                                    CustomQuerySub.zdlinkID: zdlinkID,
                                }, )
                    else:
                        with DBContext('w', None, True) as session:
                            new_query = CustomQuerySub(
                                qid=qid, title=title, dblinkId=dblinkId, database=database, user=user,
                                password=password, sql=sql, colnames=colnames, timesTy=timesTy, timesTyVal=timesTyVal,
                                colalarms=colalarms, status=status, create_time=create_time, update_time=update_time,
                                description=description, seq=seq, groupID=groupID, groupName=groupName,
                                group2ndSeq=group2ndSeq, zdlinkID=zdlinkID,
                            )
                            session.add(new_query)

                    redis_conn.hmset(bytes(title + '__zhidui', encoding='utf-8'), {'qid': qid})


        except Exception as e:
            traceback.print_exc(e)
            return self.write(dict(code=-1, msg='拉取失败'))

        return self.write(dict(code=0, msg='拉取完毕'))


class ZdInfoHandler(BaseHandler):
    '''
        获取支队分组信息，数据库源信息
    '''

    def get(self):
        id = self.get_argument('id', default=None, strip=True)
        zdlink = getzdlink(id)
        groupObj = db_list = []
        try:
            url = 'http://' + zdlink + '/getInfo/'
            res = requests.get(url, params='', timeout=3)
            if res.text:
                res_data = json.loads(res.text)
                groupObj = res_data['groupObj']
                db_list = res_data['db_list']

        except Exception as e:
            ins_log.read_log('error', e)
        return self.write(dict(code=0, zdlink=zdlink, groupObj=groupObj, db_list=db_list))


class ZdGroupHandler(BaseHandler):
    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        zdlink = getzdlink(data['linkId'])
        try:
            url = 'http://' + zdlink + '/changeZdGroup/'
            try:
                res = requests.post(url, data=json.dumps(data), timeout=3)
                if res.text:
                    res_data = json.loads(res.text)
                    if res_data['code'] == 0:
                        return self.write(dict(code=0, msg='成功'))
                    else:
                        return self.write(dict(code=0, msg='失败'))
            except:
                return self.write(dict(code=-1, msg='网络超时'))

        except Exception as e:
            ins_log.read_log('error', e)
            return self.write(dict(code=0, msg='失败'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        zdlink = getzdlink(data['linkId'])
        try:
            url = 'http://' + zdlink + '/changeZdGroup/'
            try:
                res = requests.delete(url, data=json.dumps(data), timeout=3)
                if res.text:
                    res_data = json.loads(res.text)
                    if res_data['code'] == 0:
                        return self.write(dict(code=0, msg='成功'))
                    else:
                        return self.write(dict(code=0, msg='失败'))
            except:
                return self.write(dict(code=-1, msg='网络超时'))

        except Exception as e:
            ins_log.read_log('error', e)
            return self.write(dict(code=0, msg='失败'))


class QueryConfLogHandler(BaseHandler):
    '''
        log
    '''

    def get(self, *args, **kwargs):
        qid = self.get_argument('qid', default=None, strip=True)
        qty = self.get_argument('qty', default=None, strip=True)
        ins_log.read_log('info', qid)
        ins_log.read_log('info', qty)
        data_dict = {}
        with DBContext('r') as session:
            cursor = session.execute('''
            select create_time,targeted_val from custom_query_log
            where qid = %s and ty = %s order by id desc limit 0, 10
            ''' % (qid, qty))
            result = cursor.fetchall()
            for create_time, targeted_val in result:
                data_dict[str(create_time)] = targeted_val

        return self.write(dict(code=0, msg='获取成功', data=data_dict))


customquery_urls = [
    (r"/v1/queryConf/", QueryConfFileHandler),
    (r"/v1/queryConfForshow/", QueryConfForshowFileHandler),
    (r"/v1/queryConf/do_sql/", QueryConfDoSqlFileHandler),
    (r"/v1/operationtmp/", TmpFileHandler),
    (r"/v1/gettmp/", TmpFileHandler),
    (r"/v1/operationgroup/", GroupHandler),
    (r"/v1/getgroup/", GroupHandler),
    (r"/v1/querySubConf/", QuerySubConfHandler),
    (r"/v1/queryZd/", ZdLinkHandler),
    (r"/v1/queryPushConf/", PushConfHandler),
    (r"/v1/queryPullConf/", PullConfHandler),
    (r"/v1/getZdInfo/", ZdInfoHandler),
    (r"/v1/changeZdGroup/", ZdGroupHandler),
    (r"/v1/getQueryLog/", QueryConfLogHandler),
]

if __name__ == "__main__":
    pass
