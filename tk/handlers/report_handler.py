#!/usr/bin/env python
# -*-coding:utf-8-*-
import json
import os
from libs.base_handler import BaseHandler
from websdk.web_logs import ins_log
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from settings import CUSTOM_DB_INFO
from script.pbToxls import saveExce
import traceback
from libs.file_conn import *
from script.sql_obj import *


def getFileNa(na, st, et):
    return '{0}{1}-{2}.xls'.format(na, st.replace('-', ''), et.replace('-', ''))


class ReportHandler(BaseHandler):
    def get(self, *args, **kwargs):
        report_na = self.get_argument('report_na', default=None, strip=True)
        report_val = self.get_argument('report_val', default=None, strip=True)
        dict_list = []
        Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dir_path = '{}/static/report/{}/'.format(Base_DIR, report_val)
        try:
            root, dirs, files = os.walk(dir_path).__next__()
            for f in files:
                obj = {
                    'file_na': f,
                    'file_size': '{}{}'.format(get_FileSize(os.path.join(root, f)), 'KB'),
                    'ctime': get_FileCreateTime(os.path.join(root, f)),
                    'url': 'http://{}/static/report/{}/{}'.format(self.request.host, report_val, f),
                }
                dict_list.append(obj)
            dict_list.sort(key=lambda x: x['ctime'], reverse=True)
        except:
            traceback.print_exc()
            return self.write(dict(code=-1, msg='获取失败', data=dict_list))

        if len(dict_list) == 0:
            return self.write(dict(code=-2, msg='没有文件', data=dict_list))

        return self.write(dict(code=0, msg='获取成功', data=dict_list))

    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        searchValue = data.get('searchValue')
        stime = data.get('stime')
        etime = data.get('etime')
        Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dir_path = '{}/static/report/'.format(Base_DIR)
        filedir_path = '%s/%s/' % (dir_path, searchValue)
        if not os.path.exists(filedir_path):
            os.mkdir(filedir_path)

        try:
            if searchValue == 'kcjctj':
                _obj = report_Obj[searchValue]
                file_na = getFileNa(_obj["file_na"], stime, etime)
                file_path = os.path.join(filedir_path, file_na)
                columns = _obj["columns"]
                sql = _obj["sql"].format(stime, etime)
                oracle_conn = OracleBase(**ordb_obj)
                res = oracle_conn.query(sql)
                # res = (('4401', 904, 904, 0, 547, 56, 0),
                #        ('4402', 123, 123, 4, 324, 657, 0),
                #        ('4403', 677, 454, 0, 789, 567, 0),
                #        ('4404', 345, 998, 0, 566, 133, 0),
                #        ('4405', 677, 454, 0, 456, 134, 0),
                #        ('4406', 345, 795, 0, 678, 345, 0))
                data = []
                for d in res:
                    _l = []
                    if d[0] in flag:
                        _l.append('粤' + flag[d[0]][0])
                        _l.append(flag[d[0]][1])
                    else:
                        _l.append(d[0])
                        _l.append(d[0])
                    _l = _l + list(d[1:])
                    data.append(_l)

                saveExce(columns, data, file_path)


        except:
            traceback.print_exc()
            return self.write(dict(code=-1, msg='执行错误'))

        return self.write(dict(code=0, msg='执行成功'))


report_urls = [
    (r"/v1/createFile/", ReportHandler),
    (r"/v1/getFileList/", ReportHandler),
]

if __name__ == "__main__":
    pass
