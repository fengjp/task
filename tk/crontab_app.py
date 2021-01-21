#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Role    : 一些定时执行的程序


import tornado
from websdk.application import Application as myApplication
from websdk.cache_context import cache_conn
import time
import datetime
from websdk.db_context import DBContext
from settings import CUSTOM_DB_INFO
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from models.task import model_to_dict, CustomQuery, CustomQueryLog
from collections import Counter
import traceback
import re
import json
from libs.aes_coder import encrypt, decrypt
import requests
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop

TypeObj = {
    '未知': -1,
    '正常': 0,
    '一般': 1,
    '严重': 2,
    '致命': 3,
}


class Application(myApplication):
    def __init__(self, **settings):
        urls = []
        cron_callback = tornado.ioloop.PeriodicCallback(run, 1000)
        cron_callback.start()
        super(Application, self).__init__(urls, **settings)


def next_time(data):
    next_time = 0
    if data['timesTy'] == 'timesTy1':
        next_time = int(data['timesTy1Val']) * 60 + int(time.time())

    if data['timesTy'] == 'timesTy2':
        s1 = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        s2 = data['timesTy2Val'] + ':00'
        timeArray = time.strptime('%s %s' % (s1, s2), "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        next_time = timeStamp

    return next_time


def run():
    redis_conn = cache_conn()
    query_keys = redis_conn.smembers('query_list')
    for key in query_keys:
        data = redis_conn.hgetall(key)
        new_data = {}
        for k, v in data.items():
            new_data[str(k, 'utf8')] = str(v, 'utf8')
        if not new_data:
            redis_conn.srem('query_list', key)
        if new_data['status'] == '1':
            now = int(time.time())
            if now >= int(new_data['next_time']):
                do_sql(redis_conn, key, new_data)


def do_sql(redis_conn, key, new_data):
    db_info = []
    query_info = {}
    res = {}
    ty = 0
    if 'zongdui' in str(key, 'utf8'):
        ty = 0
        try:
            with DBContext('r') as session:
                query_info = session.query(CustomQuery).filter(CustomQuery.id == new_data['id']).first()

            if query_info.type == 'sql':
                dblinkId = query_info.dblinkId
                CUSTOM_DB_INFO['db'] = 'codo_cmdb'
                mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
                # 获取数据库源 连接地址
                select_db = 'select db_type, db_host, db_port, db_user, db_pwd, db_instance from asset_db where id = {}'.format(
                    dblinkId)
                db_info = mysql_conn.query(select_db)

            elif query_info.type == 'urls':
                data_list = []
                for url in json.loads(query_info.urls):
                    url = 'http://' + url
                    status_code, resp_time = getHttpCode(url)
                    _d = {}
                    _d['get_time'] = str(datetime.datetime.now()).split('.')[0]
                    _d['url'] = url
                    _d['httpcode'] = status_code
                    _d['resp_time'] = resp_time
                    colalarms = json.loads(query_info.colalarms)
                    # 判断指标值 （排序后，同大取最大，同少取最少）
                    subColList = colalarms[0]['subColList']
                    subColList = sorted(subColList, key=lambda x: TypeObj[x['alarmType']], reverse=True)
                    for alarmObj in subColList:
                        sign = alarmObj['sign']
                        alarmVal = alarmObj['alarmVal']
                        if sign == '>' and float(resp_time) > float(alarmVal):
                            _d['target'] = alarmObj['alarmType']
                            break
                        if sign == '>=' and float(resp_time) >= float(alarmVal):
                            _d['target'] = alarmObj['alarmType']
                            break
                        if sign == '<' and float(resp_time) < float(alarmVal):
                            _d['target'] = alarmObj['alarmType']
                        if sign == '<=' and float(resp_time) <= float(alarmVal):
                            _d['target'] = alarmObj['alarmType']
                        if sign == '=' and float(resp_time) == float(alarmVal):
                            _d['target'] = alarmObj['alarmType']
                    data_list.append(_d)
                data_list.sort(key=lambda x: TypeObj[x['target']], reverse=True)
                countObj = dict(Counter([i['target'] for i in data_list]))
                res = dict(code=0, msg='获取成功', errormsg='', data=data_list, count=countObj)
                # 将结果存入redis，设置过期时间.
                saveRedis(redis_conn, key, new_data, res)
        except:
            traceback.print_exc()

        if len(db_info) > 0:
            res = getData(query_info, db_info)
            # 将结果存入redis，设置过期时间.
            saveRedis(redis_conn, key, new_data, res)

    if 'zhidui' in str(key, 'utf8'):
        ty = 1
        zdlink = new_data['zdlink']
        qid = new_data.get('qid', 0)
        if int(qid) > 0:
            res = getSubData(zdlink, qid)
            # 将结果存入redis，设置过期时间.
            saveRedis(redis_conn, key, new_data, res)

    # 记录历史 只记录最高指标的一条数据
    if res and ty >= 0:
        saveLog(new_data, res, ty)


def saveRedis(redis_conn, key, new_data, res):
    # 将结果存入redis，设置过期时间.
    res_key = str(key, 'utf8') + '_res'
    redis_conn.hmset(res_key, {'res': json.dumps(res)})
    nt = next_time(new_data)
    expire = nt - int(time.time())
    redis_conn.expire(res_key, time=expire)
    redis_conn.hmset(key, {'next_time': nt})


def getData(query_info, db_info):
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
                                break
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


def getSubData(zdlink, qid):
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
                return dict(code=-2, msg='获取失败', errormsg=errormsg, data=[], count={})
        except Exception as e:
            traceback.print_exc(e)
            errormsg = '网络超时'
            return dict(code=-3, msg='获取失败', errormsg=errormsg, data=[], count={})

    except Exception as e:
        errormsg = e
        return dict(code=-4, msg='获取失败', errormsg=errormsg, data=[], count={})


def saveLog(data, res, ty):
    colalarms = json.loads(data['colalarms'].replace("'", '"'))
    if len(colalarms) > 0:
        selCol = colalarms[0]['selCol']
        title = data['title']
        qid = int(data['id'])
        res_data = res['data']
        if selCol:
            targeted_val = res_data[0][selCol]
            with DBContext('w', None, True) as session:
                new_query = CustomQueryLog(
                    targeted_val=targeted_val, title=title, qid=qid, ty=ty
                )
                session.add(new_query)


def getHttpCode(url):
    try:
        r = requests.get(url, timeout=5)
        status_code = r.status_code
        resp_time = r.elapsed.microseconds / 1000000
    except:
        status_code = 500
        resp_time = 5

    return status_code, resp_time


if __name__ == '__main__':
    pass
