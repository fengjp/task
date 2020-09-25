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
import pandas as pd


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
                filename = dir_path + f
                df = pd.read_excel(filename)
                columns = []
                num = 1
                for k in  list(df.columns.values[1:]):
                    columns_temp = {"title": '', "key": '', "align": 'center'}
                    columns_temp["title"] = str(k)
                    columns_temp["key"] = "number" + str(num)
                    columns.append(columns_temp)
                    num = num  + 1
                ins_log.read_log('info', "11111111111111111111111111111111111111")
                ins_log.read_log('info', columns)
                all_list = []
                for  d in  df.values:
                    temp_dict = {}
                    num = 1
                    for k in list(d[1:]):
                        tokey  = "number" + str(num)
                        temp_dict[tokey] = str(k)
                        num = num + 1
                    all_list.append(temp_dict)


                obj = {
                    'file_na': f,
                    'file_size': '{}{}'.format(get_FileSize(os.path.join(root, f)), 'KB'),
                    'ctime': get_FileCreateTime(os.path.join(root, f)),
                    'url': 'http://{}/static/report/{}/{}'.format(self.request.host, report_val, f),
                    'columns':str(columns),
                    'file_data': str(all_list),
                }
                # ins_log.read_log('info', "22222222222222222222222222222222222")
                # ins_log.read_log('info', obj)
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
                sql = _obj["sql"].format(stime=stime, etime=etime)
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


class ReportListHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        report_list = []
        try:
            # 每日巡检报告
            obj = {}
            obj['report_val'] = 'xunjian'
            obj['report_na'] = '每日巡检报告'
            obj['report_sql'] = ''
            data_list.append(obj)
            obj = {}
            obj['report_val'] = 'timing'
            obj['report_na'] = '定时报告'
            obj['report_sql'] = ''
            data_list.append(obj)

            obj = {}
            obj['value'] = 'xunjian'
            obj['label'] = '每日巡检报告'
            report_list.append(obj)
            obj = {}
            obj['value'] = 'timing'
            obj['label'] = '定时报告'
            report_list.append(obj)

            # 其它脚步报表
            for key in report_Obj:
                obj = {}
                obj['report_val'] = key
                obj['report_na'] = report_Obj[key]['file_na']
                obj['report_sql'] = report_Obj[key]['sql']
                data_list.append(obj)

                obj = {}
                obj['value'] = key
                obj['label'] = report_Obj[key]['file_na']
                report_list.append(obj)

        except:
            traceback.print_exc()
            return self.write(dict(code=-1, msg='获取失败', reportdata=data_list, reportList=report_list))

        if len(data_list) == 0:
            return self.write(dict(code=-2, msg='没有文件', reportdata=data_list, reportList=report_list))

        return self.write(dict(code=0, msg='获取成功', reportdata=data_list, reportList=report_list))


report_urls = [
    (r"/v1/createFile/", ReportHandler),
    (r"/v1/getFileList/", ReportHandler),
    (r"/v1/getReportList/", ReportListHandler),
]

if __name__ == "__main__":
    pass
