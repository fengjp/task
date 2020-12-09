#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : server_common.py
# @Role    : server公用方法

from settings import CUSTOM_DB_INFO
from libs.mysql_conn import MysqlBase
from websdk.web_logs import ins_log
from libs.aes_coder import decrypt


def get_serverObjList(ip_list=[]):
    """
    :return: [{"ip": "39.104.83.140", "port": "22", "username": "root", "password": "asdqwe123."}]
    """
    serverObjList = []

    CUSTOM_DB_INFO['db'] = 'codo_cmdb'
    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
    if len(ip_list) > 0:
        sql = '''
            select a.ip,a.`port`,b.system_user,b.`password` from asset_server a,admin_users b 
            where a.admin_user = b.admin_user and a.ip in ("{}")
        '''.format('","'.join(ip_list))
    else:
        sql = '''
              select a.ip,a.`port`,b.system_user,b.`password` from asset_server a,admin_users b 
              where a.admin_user = b.admin_user
        '''
    server_info = mysql_conn.query(sql)
    for ip, port, username, password in server_info:
        data = {}
        data['ip'] = ip
        data['port'] = port
        data['username'] = username
        data['password'] = decrypt(password)
        serverObjList.append(data)

    return serverObjList


if __name__ == '__main__':
    print(get_serverObjList([]))
