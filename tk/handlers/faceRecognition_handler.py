#!/usr/bin/env python
# -*-coding:utf-8-*-
import json
import os
import re
from libs.base_handler import BaseHandler
import traceback
import datetime, time
import requests

TypeObj = {
    '未知': -1,
    '正常': 0,
    '一般': 1,
    '严重': 2,
    '致命': 3,
}


class FaceRecognitionHandler(BaseHandler):
    '''人脸识别检测
    '''

    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []
        obj = {
            "name": "人脸识别检测",
            "seq": 0,
            "child": [],
            "next_time": int(time.time()) + 60,
        }

        url_131 = ""
        url_132 = ""

        payload = ""
        headers = {}

        try:
            # response = requests.request("POST", url_131, data=payload, headers=headers)
            # res_131 = response.json()
            res_131 = {"code": "1", "similarity": 98.123123}
            res_131['id'] = 131
        except:
            res_131 = {"code": "-1"}

        res_d = self.create_obj(res_131)
        res_d['title'] = "人脸识别检测_131"
        obj['child'].append(res_d)

        try:
            # response = requests.request("POST", url_132, data=payload, headers=headers)
            # res_132 = response.json()
            res_132 = {"code": "1", "similarity": 99.112}
            res_132['id'] = 132
        except:
            res_132 = {"code": "-1"}

        res_d = self.create_obj(res_132)
        res_d['title'] = "人脸识别检测_132"
        obj['child'].append(res_d)

        dict_list.append(obj)

        return self.write(dict(code=0, msg='获取成功', data=dict_list))

    def create_obj(self, res):
        d = {
            "id": res["id"],
            "title": "人脸识别检测",
            "seq": 0,
            "columns": [
                {
                    "title": "返回状态",
                    "key": "code",
                    "align": "center",
                    "minWidth": 80,
                },
                {
                    "title": "相似度",
                    "key": "similarity",
                    "align": "center",
                    "minWidth": 80,
                },
                {
                    "title": "指标",
                    "key": "target",
                    "align": "center",
                    "minWidth": 80,
                }
            ],
            "tableData": [],
            "count": {"正常": 1},
            "isShow": False,
            "up_tip": "0时0分00秒后更新",
        }
        tableData_obj = {
            "code": res["code"],
            "similarity": res["similarity"],
            "target": "正常",
            "cellClassName": {"target": "table-success-cell-target"}
        }
        if str(res.get("code", "-1")) != '1':
            tableData_obj['target'] = '致命'
            tableData_obj['cellClassName'] = {"target": "table-error-cell-target"}
            d['count'] = {'致命': 1}

        d["tableData"].append(tableData_obj)
        return d


faceRecognition_urls = [
    (r"/v1/getFaceRecognition/", FaceRecognitionHandler),
]

if __name__ == "__main__":
    pass
