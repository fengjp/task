#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
Desc   : 检查数据库连接是否正常
"""
import os
import sys

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


def getDBList():
    CUSTOM_DB_INFO['db'] = 'codo_cmdb'
    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
    # 获取数据库源 连接地址
    select_db = 'select id,db_type, db_host, db_port, db_user, db_pwd, db_instance from asset_db'
    db_info = mysql_conn.query(select_db)

    return db_info


def run():
    DB_INFO = getDBList()
    for db in DB_INFO:
        try:
            # 解密密码
            db_pwd = decrypt(db[5])
            db_conf = {
                'host': db[2],
                'port': int(db[3]),
                'user': db[4],
                'passwd': db_pwd,
                'db': db[6]
            }

            if not db[6]:
                if db[1] == 'mysql':
                    db_conf['db'] = 'mysql'

                if db[1] == 'oracle':
                    db_conf['db'] = 'orcl'

            if db[1] == 'mysql':
                db_conn = MysqlBase(**db_conf)

            if db[1] == 'oracle':
                db_conn = OracleBase(**db_conf)

            if db_conn.test():
                state = 'Running'
            else:
                state = 'failed'

            CUSTOM_DB_INFO['db'] = 'codo_cmdb'
            mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
            up_sql = '''update codo_cmdb.asset_db set state = '%s' where id = %s''' % (state, db[0])
            mysql_conn.change(up_sql)

        except:
            traceback.print_exc()
            return 'failed'
    print(state)
    return 'ok'


if __name__ == '__main__':
    run()
