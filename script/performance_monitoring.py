#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
获取主机性能分析
'''
import os
import sys
import json
import re
import datetime

_op = os.path.dirname
cwdir = _op(os.path.abspath(__file__))
project_path = _op(_op(os.path.abspath(__file__)))
app_path = _op(project_path)
sys.path.insert(0, project_path)
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from settings import CUSTOM_DB_INFO
from libs.aes_coder import decrypt
import traceback
from libs.myAnsible import AnsiableAPI
from libs.server.server_common import get_serverObjList

hostsresource = [
    {"ip": "39.108.153.113", "port": "22", "username": "likang", "password": "likang2020"},
]


def get_top_info(hosts, asb):
    res = {}
    asb.run(hosts=hosts, module="shell", args="top -bn 1 -i -c")
    stdout_dict = json.loads(asb.get_result())
    stdout = stdout_dict['success'][hosts]['stdout']
    # %Cpu(s) cpu使用率
    _s = stdout.split('\n')[2]
    # obj = re.findall(r'.*?:(.*?)us.*?(.*?)sy.*?(.*?)ni.*?(.*?)id.*?(.*?)wa.*?(.*?)hi.*?(.*?)si.*?(.*?)st.*?', s, re.S)
    _l = re.findall(r'.*?us,.*?(.*?)sy.*?', _s, re.S)
    cpu_sy = _l[0].replace(' ', '').replace('%', '')
    res['cpu_sy'] = cpu_sy

    # KiB Mem 内存
    _s = stdout.split('\n')[3]
    _l = re.findall(r'.*?Mem :.*?(.*?)total.*?(.*?)free.*?(.*?)used.*?(.*?)buff/cache.*?', _s, re.S)
    if _l:
        res['mem_total'] = _l[0][0].replace(' ', '').replace('k', '').replace(',', '')
        res['mem_free'] = _l[0][1].replace(' ', '').replace('k', '').replace(',', '')
        res['mem_used'] = _l[0][2].replace(' ', '').replace('k', '').replace(',', '')
        res['mem_buff_cache'] = _l[0][3].replace(' ', '').replace('k', '').replace(',', '')
    else:
        _ll = re.findall(r'.*?:.*?(.*?)total.*?(.*?)used.*?(.*?)free.*?(.*?)buffers.*?', _s, re.S)
        res['mem_total'] = _ll[0][0].replace(' ', '').replace('k', '').replace(',', '')
        res['mem_used'] = _ll[0][1].replace(' ', '').replace('k', '').replace(',', '')
        res['mem_free'] = _ll[0][2].replace(' ', '').replace('k', '').replace(',', '')
        res['mem_buff_cache'] = _ll[0][3].replace(' ', '').replace('k', '').replace(',', '')
    return res


def get_tcp(hosts, asb):
    res = {}
    asb.run(hosts=hosts, module="shell", args="netstat -n| awk '/^tcp/ {++S[$NF]} END {for(a in S) print a, S[a]}'")
    stdout_dict = json.loads(asb.get_result())
    stdout_lines = stdout_dict['success'][hosts]['stdout_lines']
    # ['ESTABLISHED 17', 'TIME_WAIT 2']
    for i in stdout_lines:
        _l = i.split(' ')
        if _l[0] == 'ESTABLISHED':
            res['tcp_established'] = _l[1]
        if _l[0] == 'TIME_WAIT':
            res['tcp_time_wait'] = _l[1]

    return res


def get_iostat(hosts, asb):
    res = {}
    asb.run(hosts=hosts, module="shell", args="iostat -c")
    stdout_dict = json.loads(asb.get_result())
    stdout_lines = stdout_dict['success'][hosts]['stdout_lines']
    _s = stdout_lines[3]
    _s = _s.split(' ')
    _s = [i for i in _s if i]
    res['iowait'] = _s[3]

    return res


def intoSql(obj):
    try:
        sql = '''
            INSERT INTO `codo_cmdb`.`asset_server_performance`(`ip`, `cpu_sy`, `mem_total`, `mem_free`, `mem_used`, 
            `mem_buff_cache`, `tcp_established`, `tcp_time_wait`, `iowait`, `create_time`) 
            VALUES ('{ip}', '{cpu_sy}', {mem_total}, {mem_free}, {mem_used}, {mem_buff_cache}, {tcp_established}, 
            {tcp_time_wait}, '{iowait}', '{create_time}');
        '''.format(ip=obj.get('ip', ''), cpu_sy=obj.get('cpu_sy', ''), mem_total=obj.get('mem_total', ''),
                   mem_free=obj.get('mem_free', ''), mem_used=obj.get('mem_used', ''),
                   mem_buff_cache=obj.get('mem_buff_cache', ''), tcp_established=obj.get('tcp_established', 0),
                   tcp_time_wait=obj.get('tcp_time_wait', 0), iowait=obj.get('iowait', ''),
                   create_time=datetime.datetime.now())
        CUSTOM_DB_INFO['db'] = 'codo_cmdb'
        mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
        mysql_conn.change(sql)
    except Exception as e:
        traceback.print_exc(e)
        traceback.print_exc(sql)


def run():
    serverObjList = get_serverObjList()
    if len(serverObjList) > 0:
        asb = AnsiableAPI(connection='smart', hostsresource=serverObjList)
        # asb.run(hosts="test", module="shell", args='df -m')
        for i in serverObjList:
            try:
                obj = {'ip': i['ip']}
                top_obj = get_top_info(i['ip'], asb)
                tcp_obj = get_tcp(i['ip'], asb)
                iostat_obj = get_iostat(i['ip'], asb)
                obj.update(top_obj)
                obj.update(tcp_obj)
                obj.update(iostat_obj)
                intoSql(obj)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    run()
