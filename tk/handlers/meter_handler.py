#!/usr/bin/env python
# -*-coding:utf-8-*-

import json
import os
import  shutil
import re
from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from websdk.consts import const
from websdk.cache_context import cache_conn
from websdk.web_logs import ins_log
from sqlalchemy import or_, and_
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase
from settings import CUSTOM_DB_INFO
from libs.server.server_common import *
from libs.myAnsible import AnsiableAPI
from models.task import Score,model_to_dict
from models.task import Ranking
from datetime import datetime
import dateutil.relativedelta
from dateutil  import  rrule
import time
import pandas as pd

class MeterHandler(BaseHandler):
    def get(self, *args, **kwargs):
        today = datetime.now().strftime('%Y-%m')  # 当前月份
        # 组装月份数组
        months_list = []
        now = datetime.now()
        for  h in range(11,0,-1):
              date = now + dateutil.relativedelta.relativedelta(months=-h)  # 上个月时间
              # date.strftime('%Y-%m') #上个月份
              months_list.append(date.strftime('%Y-%m'))
        months_list.append(today)
        data_list = []
        data_list2 = []
        sum_list = []

        # value = str(self.get_argument('value',strip=True))
        today = datetime.now().strftime('%Y-%m') #当前月份
        ins_log.read_log('info', today)
        with DBContext('r') as session:
            # conditions = []
            todata = session.query(Score).filter(Score.today == today).all()
            # tocount = session.query(Customized).filter().count()

        for msg in todata:
            meter_list = {}
            data_dict = model_to_dict(msg)
            meter_list["id"] = data_dict["id"]
            meter_list["today"] = data_dict["today"]
            meter_list["fuwu_defen"] = data_dict["fuwu_defen"]
            meter_list["fuwu_remarks"] = data_dict["fuwu_remarks"]
            meter_list["xitong_defen"] = data_dict["xitong_defen"]
            meter_list["xitong_remarks"] = data_dict["xitong_remarks"]
            meter_list["duanxin_defen"] = data_dict["duanxin_defen"]
            meter_list["duanxin_remarks"] = data_dict["duanxin_remarks"]
            meter_list["nwwang_defen"] = data_dict["nwwang_defen"]
            meter_list["nwwang_remarks"] = data_dict["nwwang_remarks"]
            meter_list["yidi_defen"] = data_dict["yidi_defen"]
            meter_list["yidi_remarks"] = data_dict["yidi_remarks"]
            meter_list["renlian_defen"] = data_dict["renlian_defen"]
            meter_list["renlian_remarks"] = data_dict["renlian_remarks"]
            meter_list["yunxing_defen"] = data_dict["yunxing_defen"]
            meter_list["yunxing_remarks"] = data_dict["yunxing_remarks"]
            data_list.append(meter_list)

        for g in months_list:
            ins_log.read_log('info', today)
            temp_sum = 0
            with DBContext('r') as session:
                # conditions = []
                todata = session.query(Score).filter(Score.today == g).all()
                tocount = session.query(Score).filter(Score.today == g).count()
            if tocount < 1:
                temp_sum = 0
            else:
              for msg in todata:
                meter_list = {}
                data_dict = model_to_dict(msg)
                meter_list["id"] = data_dict["id"]
                meter_list["today"] = data_dict["today"]
                temp_sum = int(data_dict["fuwu_defen"]) + int(data_dict["xitong_defen"]) + int(data_dict["duanxin_defen"])+ int(data_dict["nwwang_defen"]) \
                           + int(data_dict["yidi_defen"]) + int(data_dict["renlian_defen"]) + int(data_dict["yunxing_defen"])
            sum_list.append(temp_sum + 39+5) #(39+5)分：固定可以得的分数
        data_list2.append(months_list)
        data_list2.append(sum_list)
        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=data_list,list=data_list2))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))


class MeteraddHandler(BaseHandler):
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        fuwu = str(data.get('fuwu', ""))
        fuwu_remarks = str(data.get('fuwu_remarks', ""))
        xitong = str(data.get('xitong', ""))
        xitong_remarks = str(data.get('xitong_remarks', ""))
        peizhi = data.get('peizhi', "")
        peizhi_remarks = data.get('peizhi_remarks', "")
        shengji = str(data.get('shengji', ""))
        shengji_remarks = str(data.get('shengji_remarks', ""))
        xtpeizhi = data.get('xtpeizhi', "")
        xtpeizhi_remarks = data.get('xtpeizhi_remarks', "")
        zhichi = str(data.get('zhichi', ""))
        zhichi_remarks = str(data.get('zhichi_remarks', ""))
        duanxin = str(data.get('duanxin', ""))
        duanxin_remarks = str(data.get('duanxin_remarks', ""))
        qudao = str(data.get('qudao', ""))
        qudao_remarks = str(data.get('qudao_remarks', ""))
        xiangmu = str(data.get('xiangmu', ""))
        xiangmu_remarks = str(data.get('xiangmu_remarks', ""))
        tuikuan = str(data.get('tuikuan', ""))
        tuikuan_remarks = str(data.get('tuikuan_remarks', ""))
        yunxing = str(data.get('yunxing', ""))
        yunxing_remarks = str(data.get('yunxing_remarks', ""))
        jiaohuan = str(data.get('jiaohuan', ""))
        jiaohuan_remarks = str(data.get('jiaohuan_remarks', ""))
        shengji_jiaohuan = str(data.get('shengji_jiaohuan', ""))
        shengji_jiaohuan_remarks = str(data.get('shengji_jiaohuan_remarks', ""))
        yidi = str(data.get('yidi', ""))
        yidi_remarks = str(data.get('yidi_remarks', ""))
        renlian = str(data.get('renlian', ""))
        renlian_remarks = str(data.get('renlian_remarks', ""))
        riqi = str(data.get('riqi', ""))
        paiming = str(data.get('paiming', ""))
        zongfen = str(data.get('zongfen', ""))

        with DBContext('r') as session:
            tocount = session.query(Ranking).filter(Ranking.riqi == riqi).count()
        if tocount < 1:
          with DBContext('w', None, True) as session:
              session.add(Ranking(
                fuwu=fuwu,
                  fuwu_remarks=fuwu_remarks,
                xitong = xitong,
                  xitong_remarks=xitong_remarks,
                peizhi = peizhi,
                  peizhi_remarks=peizhi_remarks,
                shengji = shengji,
                  shengji_remarks=shengji_remarks,
                xtpeizhi=xtpeizhi,
                  xtpeizhi_remarks=xtpeizhi_remarks,
                zhichi=zhichi,
                  zhichi_remarks=zhichi_remarks,
                duanxin = duanxin,
                  duanxin_remarks=duanxin_remarks,
                qudao = qudao,
                  qudao_remarks=qudao_remarks,
                xiangmu = xiangmu,
                  xiangmu_remarks=xiangmu_remarks,
                tuikuan = tuikuan,
                  tuikuan_remarks=tuikuan_remarks,
                yunxing = yunxing,
                  yunxing_remarks=yunxing_remarks,
                jiaohuan = jiaohuan,
                  jiaohuan_remarks=jiaohuan_remarks,
                shengji_jiaohuan = shengji_jiaohuan,
                  shengji_jiaohuan_remarks=shengji_jiaohuan_remarks,
                yidi = yidi,
                  yidi_remarks=yidi_remarks,
                renlian = renlian,
                  renlian_remarks=renlian_remarks,
                riqi=riqi,
                paiming = paiming,
                zongfen = zongfen,
                ))
              session.commit()
          self.write(dict(code=0, msg='成功', count=0, data=[]))
        else:
            with DBContext('w', None, True) as session:
                session.query(Ranking).filter(Ranking.riqi == riqi).update({
                    Ranking.fuwu: fuwu,
                    Ranking.fuwu_remarks: fuwu_remarks,
                    Ranking.xitong: xitong,
                    Ranking.xitong_remarks: xitong_remarks,
                    Ranking.peizhi: peizhi,
                    Ranking.peizhi_remarks: peizhi_remarks,
                    Ranking.shengji: shengji,
                    Ranking.shengji_remarks: shengji_remarks,
                    Ranking.xtpeizhi: xtpeizhi,
                    Ranking.xtpeizhi_remarks: xtpeizhi_remarks,
                    Ranking.zhichi: zhichi,
                    Ranking.zhichi_remarks: zhichi_remarks,
                    Ranking.duanxin: duanxin,
                    Ranking.duanxin_remarks: duanxin_remarks,
                    Ranking.qudao: qudao,
                    Ranking.qudao_remarks: qudao_remarks,
                    Ranking.xiangmu: xiangmu,
                    Ranking.xiangmu_remarks: xiangmu_remarks,
                    Ranking.tuikuan: tuikuan,
                    Ranking.tuikuan_remarks: tuikuan_remarks,
                    Ranking.yunxing: yunxing,
                    Ranking.yunxing_remarks: yunxing_remarks,
                    Ranking.jiaohuan: jiaohuan,
                    Ranking.jiaohuan_remarks: jiaohuan_remarks,
                    Ranking.shengji_jiaohuan: shengji_jiaohuan,
                    Ranking.shengji_jiaohuan_remarks: shengji_jiaohuan_remarks,
                    Ranking.yidi: yidi,
                    Ranking.yidi_remarks: yidi_remarks,
                    Ranking.renlian: renlian,
                    Ranking.renlian_remarks: renlian_remarks,
                    Ranking.riqi: riqi,
                    Ranking.paiming: paiming,
                    Ranking.zongfen: zongfen,
                })
                session.commit()
            self.write(dict(code=0, msg='成功', count=0, data=[]))

class rankinglistHandler(BaseHandler):
    def get(self, *args, **kwargs):
        tempData = [
                       {"toname": "系统建设运维保障", "name": "服务稳定性", "Symbol": "P1-1", "branch": "10分",
                        "method": "对于互联网平台（网页版）连续服务故障3小时以上的，扣10分；对于互联网平台（网页版）连续服务故障1至3小时的，扣5分;对于“交管12123”APP连续服务故障2小时以上的，扣10分；对于“交管12123”APP连续服务故障1至2小时的，扣5分；对于互联网平台访问失败比率大于20%的，扣10分；对于互联网平台访问失败比率大于10%的，扣5分。因机房搬迁、运营商网络等原因造成服务中断且已上报部局备案的，不扣分。",
                        },
                       {"toname": "系统建设运维保障", "name": "系统运行效率", "Symbol": "P1-2", "branch": "10分",
                        "method": "对于请求服务处理平均时间小于0.1秒的，得10分，请求服务处理平均时间每增加0.1秒，扣1分，直至0分为止。",
                        },
                       {"toname": "系统建设运维保障", "name": "软硬件设备配置", "Symbol": "P1-3", "branch": "10分",
                        "method": "对于应用服务器、数据库服务器、网络设备、互联网网络专线等资源不足，未配置云防护，影响互联网平台正常运行的，扣3分；对于未能及时按照部局系统建设要求，配置软硬件设备,完成系统建设的，扣5分。",
                        },
                       {"toname": "系统建设运维保障", "name": "系统及时升级", "Symbol": "P1-4", "branch": "5分",
                        "method": "对于未能按照部局发文要求及时升级软件的，扣5分；对未能及时升级软件补丁的，每次扣3分，直至0分为止。",
                        },
                       {"toname": "短信平台", "name": "跨省短信发送支持", "Symbol": "P1-5", "branch": "5分",
                        "method": "对于互联网平台对接的电信、移动、联通三大运营商均支持跨省短信发送的，得5分；其余得0分。",
                        },
                       {"toname": "短信平台", "name": "短信发送成功率", "Symbol": "P1-6", "branch": "5分",
                        "method": "对于短信发送成功率在90%以上的，得5分；对于短信发送成功率每减少10%的，扣1分，直至0分为止。",
                        },
                       {"toname": "网上支付平台", "name": "支付渠道", "Symbol": "P1-7", "branch": "5分",
                        "method": "对于支持银联、支付宝和微信中两个支付渠道的，得5分；对于支持支付宝、微信中任一支付渠道的，得3分；对于支持银联支付渠道的，得2分；不支持银联、支付宝、微信，但支持其他网上支付渠道的，得1分；其余得0分。",
                        },
                       {"toname": "网上支付平台", "name": "支付项目", "Symbol": "P1-8", "branch": "5分",
                        "method": "对于支持驾驶人考试费支付项目的，得2分；对于支持机动车、驾驶证牌证工本费支付项目的，得2分；对于支持邮寄费支付项目的，得1分。",
                        },
                       {"toname": "网上支付平台", "name": "退款支持", "Symbol": "P1-9", "branch": "10分",
                        "method": "对于支持交通违法罚款退款的，得5分；对于支持机动车、驾驶证牌证工本费退款的，得3分；对于支持考试费退款的，得2分。",
                        },
                       {"toname": "网上支付平台", "name": "运行情况", "Symbol": "P1-10", "branch": "10分",
                        "method": "监测互联网平台请求网上支付平台的响应成功率，对于请求响应成功率达90%以上的，得3分；监测用户网上支付成功交易的平均操作时长，对于用户平均操作时长小于2分钟的，得5分；监测用户网上支付成功比率，对于成功比率大于90%的，得2分。",
                        },
                       {"toname": "数据交换", "name": "内外网数据交换", "Symbol": "P1-11", "branch": "10分",
                        "method": "计算互联网测试数据包交换到公安网，公安网生成反馈数据再交换到互联网的总时长。对于平均总时长在5分钟以内的，得10分；对于平均总时长每增加1分钟的，扣2分，直至0分为止。对于交通违法证据图片未交换至互联网，用户无法查看的，扣5分。",
                        },
                       {"toname": "数据交换", "name": "省际数据交换", "Symbol": "P1-12", "branch": "5分",
                        "method": "对于部级互联网平台与地方互联网平台通讯异常的总时长小于30分钟的，得5分；对于通讯异常每增加1至10分钟的，扣1分，直至0分为止。",
                        },
                       {"name": "异地业务请求", "Symbol": "P1-13", "branch": "5分",
                        "method": "对于因网络阻断、系统异常导致异地业务请求无法正常返回的失败率低于0.2%的，得5分；对于失败率每增加0.2%，扣1分，直至0分为止。",
                        },
                       {"toname": "人脸识别", "name": "人脸识别通过率", "Symbol": "P1-14", "branch": "5分",
                        "method": "对于人脸识别比对通过率在85%以上的，得5分；对于人脸识别比对通过率每减少5%的，扣1分，直至0分为止。",
                        },
                       {"toname": "", "name": "合计总分", "Symbol": "", "branch": "100", "method": ""},
                   ]
        tempData2 = [
            {"toname": "系统建设运维保障", "name": "服务稳定性", "Symbol": "P1-1", "branch": "10分",
             "method": "对于互联网平台（网页版）连续服务故障3小时以上的，扣10分；对于互联网平台（网页版）连续服务故障1至3小时的，扣5分;对于“交管12123”APP连续服务故障2小时以上的，扣10分；对于“交管12123”APP连续服务故障1至2小时的，扣5分；对于互联网平台访问失败比率大于20%的，扣10分；对于互联网平台访问失败比率大于10%的，扣5分。因机房搬迁、运营商网络等原因造成服务中断且已上报部局备案的，不扣分。",
             },
            {"toname": "系统建设运维保障", "name": "系统运行效率", "Symbol": "P1-2", "branch": "10分",
             "method": "对于请求服务处理平均时间小于0.1秒的，得10分，请求服务处理平均时间每增加0.1秒，扣1分，直至0分为止。",
             },
            {"toname": "系统建设运维保障", "name": "软硬件设备配置", "Symbol": "P1-3", "branch": "5分",
             "method": "对于应用服务器、数据库服务器、网络设备、互联网网络专线等资源不足，影响互联网平台正常运行的，扣3分；对于未能及时按照部局部署的系统建设要求，配置软硬件设备的，扣5分。",
             },
            {"toname": "系统建设运维保障", "name": "系统及时升级", "Symbol": "P1-4", "branch": "5分",
             "method": "对于未能按照部局发文要求及时升级软件的，扣5分；对未能及时升级软件补丁的，每次扣3分，直至0分为止。",
             },
            {"toname": "系统建设运维保障", "name": "系统配置", "Symbol": "P1-5", "branch": "5分",
             "method": "各地应用服务器、数据库服务器、文件系统、短信网关、网络设备等参数配置是否正确。对于每次配置存在问题影响互联网平台功能使用的，扣3分。",
             },
            {"toname": "短信平台", "name": "跨省短信发送支持", "Symbol": "P1-6", "branch": "10分",
             "method": "各地互联网平台是否支持跨省手机号码短信发送。对于互联网平台对接的电信、移动、联通三大运营商均支持跨省短信发送的，得10分；对于两家运营商支持跨省短信发送的，得5分；其余得0分。",
             },
            {"toname": "短信平台", "name": "短信发送成功率", "Symbol": "P1-7", "branch": "5分",
             "method": "对于短信发送成功率在90%以上的，得5分；对于短信发送成功率每减少10%的，扣1分，直至0分为止。",
             },
            {"toname": "网上支付平台", "name": "支付渠道", "Symbol": "P1-8", "branch": "10分",
             "method": "对于支持银联、支付宝和微信中两个支付渠道的，得10分；对于支持支付宝、微信中任一支付渠道的，得7分；对于支持银联支付渠道的，得5分；不支持银联、支付宝、微信，但支持其他网上支付渠道的，得3分；其余得0分。",
             },
            {"toname": "网上支付平台", "name": "收费项目", "Symbol": "P1-9", "branch": "5分",
             "method": "对于支持交通违法罚款支付项目的，加3分；对于支持驾驶人考试费支付项目的，加3分；对于支持机动车、驾驶证牌证工本费支付项目的，加3分；对于支持邮寄费支付项目的，加1分。",
             },
            {"toname": "网上支付平台", "name": "退款支持", "Symbol": "P1-10", "branch": "10分",
             "method": "对于支持并应用交通违法罚款退款的，加3分；对于支持并应用机动车、驾驶证牌证工本费退款的，加2分。",
             },
            {"toname": "网上支付平台", "name": "运行情况", "Symbol": "P1-11", "branch": "10分",
             "method": "监测互联网平台请求网上支付平台的响应成功率，对于请求响应成功率在90%以上的，加3分；监测用户网上支付成功交易的平均操作时长，对于用户平均操作时长小于2分钟的，加2分。",
             },
            {"toname": "数据交换", "name": "内外网数据交换", "Symbol": "P1-12", "branch": "15分",
             "method": "通过运行监控系统监测内外网数据交换的效率。计算互联网测试数据包交换到公安网，公安网生成反馈数据再交换到互联网的总时长。对于平均总时长在30分钟以内的，得15分；对于平均总时长每增加1至5分钟的，扣3分。",
             },
            {"toname": "数据交换", "name": "省际数据交换", "Symbol": "P1-13", "branch": "5分",
             "method": "通过部级互联网平台监控与各地互联网平台数据传输通道的稳定性。对于部级互联网平台与地方互联网平台联通异常每月累计小于30分钟的，得5分；对于联通异常每增加1至10分钟的，扣1分，直至0分为止。",
             },
            {"toname": "", "name": "合计总分", "Symbol": "", "branch": "100", "method": ""},
        ]

        start_date = str(self.get_argument('start_date',strip=True))
        end_date = str(self.get_argument('end_date',strip=True))
        flag = str(self.get_argument('flag', strip=True))
        tableData = []
        if flag == '1':
            tableData = tempData
        elif flag == '2':
            tableData = tempData2

        # 组装月份数组
        months_list = []
        if start_date == '':
            if flag == '1':
               today = datetime.now().strftime('%Y-%m')  # 当前月份
               now = datetime.now()
            elif flag ==  '2':
                format = '%Y-%m'  # 根据此格式来解析时间字符串为datetime.datetime()对象
                now = datetime.strptime("2020-03", format)

            for  h in range(5,0,-1): #默认6个月
                  date = now + dateutil.relativedelta.relativedelta(months=-h)  # 上个月时间
                  # date.strftime('%Y-%m') #上个月份
                  months_list.append(date.strftime('%Y-%m'))
            if flag == '1':
                months_list.append(today)
            elif flag ==  '2':
                months_list.append("2020-03")
        else:
            from datetime import date
            temp_start = date(int(start_date.split('-')[0]),int(start_date.split('-')[1]),1)
            temp_end =   date(int(end_date.split('-')[0]),int(end_date.split('-')[1]),1)
            months_sum = rrule.rrule(rrule.MONTHLY,dtstart=temp_start,until=temp_end).count()

            format = '%Y-%m'  # 根据此格式来解析时间字符串为datetime.datetime()对象

            end_time = datetime.strptime(end_date, format)
            for h in range(months_sum - 1, 0, -1):
                date = end_time + dateutil.relativedelta.relativedelta(months=-h)  # 上个月时间
                # date.strftime('%Y-%m') #上个月份
                months_list.append(date.strftime('%Y-%m'))
            months_list.append(end_date)


        data_list = []
        sum_str ="num"
        num = 0
        for  g  in  months_list:
            with DBContext('r') as session:
                # conditions = []
                todata = session.query(Ranking).filter(Ranking.riqi == g).all()
                # tocount = session.query(Ranking).filter(Score.today == g).count()
            sum_str = "num" + str(num)
            for msg in todata:
                # ranking_list = {}
                data_dict = model_to_dict(msg)

                if flag == '1':
                  tableData[0][sum_str] = data_dict["fuwu"]    + "分           （评分说明：" +  data_dict["fuwu_remarks"] + ")"
                  tableData[1][sum_str] = data_dict["xitong"]  + "分           （评分说明：" + data_dict["xitong_remarks"] + ")"
                  tableData[2][sum_str] = data_dict["peizhi"]  + "分           （评分说明：" + data_dict["peizhi_remarks"] + ")"
                  tableData[3][sum_str] = data_dict["shengji"] + "分           （评分说明：" + data_dict["shengji_remarks"] + ")"
                  tableData[4][sum_str] = data_dict["zhichi"]  + "分           （评分说明：" +  data_dict["zhichi_remarks"] + ")"
                  tableData[5][sum_str] = data_dict["duanxin"] + "分           （评分说明：" +  data_dict["duanxin_remarks"] + ")"
                  tableData[6][sum_str] = data_dict["qudao"]   + "分           （评分说明：" +  data_dict["qudao_remarks"] + ")"
                  tableData[7][sum_str] = data_dict["xiangmu"] + "分           （评分说明：" +  data_dict["xiangmu_remarks"] + ")"
                  tableData[8][sum_str] = data_dict["tuikuan"] + "分           （评分说明：" +  data_dict["tuikuan_remarks"] + ")"
                  tableData[9][sum_str] = data_dict["yunxing"] + "分           （评分说明：" +  data_dict["yunxing_remarks"] + ")"
                  tableData[10][sum_str] = data_dict["jiaohuan"]          + "分           （评分说明：" +  data_dict["jiaohuan_remarks"] + ")"
                  tableData[11][sum_str] = data_dict["shengji_jiaohuan"]  + "分           （评分说明：" +  data_dict["shengji_jiaohuan_remarks"] + ")"
                  tableData[12][sum_str] = data_dict["yidi"]              + "分           （评分说明：" +  data_dict["yidi_remarks"] + ")"
                  tableData[13][sum_str] = data_dict["renlian"]           + "分           （评分说明：" + data_dict["renlian_remarks"] + ")"
                  tableData[14][sum_str] = data_dict["zongfen"]           + '分(第' + data_dict["paiming"] + '名)'
                elif flag == '2':
                  tableData[0][sum_str] = data_dict["fuwu"]    + "分           （评分说明：" +  data_dict["fuwu_remarks"] + ")"
                  tableData[1][sum_str] = data_dict["xitong"]  + "分           （评分说明：" + data_dict["xitong_remarks"] + ")"
                  tableData[2][sum_str] = data_dict["peizhi"]  + "分           （评分说明：" + data_dict["peizhi_remarks"] + ")"
                  tableData[3][sum_str] = data_dict["shengji"] + "分           （评分说明：" + data_dict["shengji_remarks"] + ")"
                  tableData[4][sum_str] = data_dict["xtpeizhi"] + "分           （评分说明：" + data_dict["xtpeizhi_remarks"] + ")"
                  tableData[5][sum_str] = data_dict["zhichi"]  + "分           （评分说明：" +  data_dict["zhichi_remarks"] + ")"
                  tableData[6][sum_str] = data_dict["duanxin"] + "分           （评分说明：" +  data_dict["duanxin_remarks"] + ")"
                  tableData[7][sum_str] = data_dict["qudao"]   + "分           （评分说明：" +  data_dict["qudao_remarks"] + ")"
                  tableData[8][sum_str] = data_dict["xiangmu"] + "分           （评分说明：" +  data_dict["xiangmu_remarks"] + ")"
                  tableData[9][sum_str] = data_dict["tuikuan"] + "分           （评分说明：" +  data_dict["tuikuan_remarks"] + ")"
                  tableData[10][sum_str] = data_dict["yunxing"] + "分           （评分说明：" +  data_dict["yunxing_remarks"] + ")"
                  tableData[11][sum_str] = data_dict["jiaohuan"]          + "分           （评分说明：" +  data_dict["jiaohuan_remarks"] + ")"
                  tableData[12][sum_str] = data_dict["shengji_jiaohuan"]  + "分           （评分说明：" +  data_dict["shengji_jiaohuan_remarks"] + ")"
                  # tableData[13][sum_str] = data_dict["yidi"]              + "分           （评分说明：" +  data_dict["yidi_remarks"] + ")"
                  # tableData[14][sum_str] = d/ata_dict["renlian"]           + "分           （评分说明：" + data_dict["renlian_remarks"] + ")"
                  tableData[13][sum_str] = data_dict["zongfen"]           + '分(第' + data_dict["paiming"] + '名)'
            num += 1
        if len(tableData) > 0:
            self.write(dict(code=0, msg='获取成功', data=tableData,list=months_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

class uploadRankinglist(BaseHandler):
    def post(self, *args, **kwargs):
        ###文件保存到本地
        Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_path = '{}/static/ranking/'.format(Base_DIR)
        file_body = self.request.files["file"][0]["body"]
        temp_file_name = self.request.files["file"][0]["filename"] #2020年12月广东建设运行情况.xls

        file_path = upload_path + "tempfile.xls"
        with open(file_path, 'wb') as up:
            up.write(file_body)
        df = pd.read_excel(file_path)
        allsum = len(df.index)

        if allsum > 0:
            fuwu = str(df.iloc[1, 6]),
            fuwu_remarks = str(df.iloc[1, 5]),
            xitong = str(df.iloc[2, 6]),
            xitong_remarks = str(df.iloc[2, 5]),
            peizhi = str(df.iloc[3, 6]),
            peizhi_remarks = str(df.iloc[3, 5]),
            shengji = str(df.iloc[4, 6]),
            shengji_remarks = str(df.iloc[4, 5]),
            xtpeizhi = "",
            xtpeizhi_remarks = "",
            zhichi = str(df.iloc[5, 6]),
            zhichi_remarks = str(df.iloc[5, 5]),
            duanxin = str(df.iloc[6, 6]),
            duanxin_remarks = str(df.iloc[6, 5]),
            qudao = str(df.iloc[7, 6]),
            qudao_remarks = str(df.iloc[7, 5]),
            xiangmu = str(df.iloc[8, 6]),
            xiangmu_remarks = str(df.iloc[8, 5]),
            tuikuan = str(df.iloc[9, 6]),
            tuikuan_remarks = str(df.iloc[9, 5]),
            yunxing = str(df.iloc[10, 6]),
            yunxing_remarks = str(df.iloc[10, 5]),
            jiaohuan = str(df.iloc[11, 6]),
            jiaohuan_remarks = str(df.iloc[11, 5]),
            shengji_jiaohuan = str(df.iloc[12, 6]),
            shengji_jiaohuan_remarks = str(df.iloc[12, 5]),
            yidi = str(df.iloc[13, 6]),
            yidi_remarks = str(df.iloc[13, 5]),
            renlian = str(df.iloc[14, 6]),
            renlian_remarks = str(df.iloc[14, 5]),
            riqi = temp_file_name[0:4] + '-' + temp_file_name[5:7]

            # ins_log.read_log('info', allsum)
            paiming = str(df.columns[6]).split('：')[1][4:5]
            zongfen = str(df.columns[6]).split('：')[1][0:2]
        with DBContext('r') as session:
                tocount = session.query(Ranking).filter(Ranking.riqi == riqi).count()
        if tocount <= 0:
              try:
                  with DBContext('w', None, True) as session:
                      session.add(Ranking(
                          fuwu=fuwu,
                          fuwu_remarks=fuwu_remarks,
                          xitong=xitong,
                          xitong_remarks=xitong_remarks,
                          peizhi=peizhi,
                          peizhi_remarks=peizhi_remarks,
                          xtpeizhi=xtpeizhi,
                          xtpeizhi_remarks=xtpeizhi_remarks,
                          shengji=shengji,
                          shengji_remarks=shengji_remarks,
                          zhichi=zhichi,
                          zhichi_remarks=zhichi_remarks,
                          duanxin=duanxin,
                          duanxin_remarks=duanxin_remarks,
                          qudao=qudao,
                          qudao_remarks=qudao_remarks,
                          xiangmu=xiangmu,
                          xiangmu_remarks=xiangmu_remarks,
                          tuikuan=tuikuan,
                          tuikuan_remarks=tuikuan_remarks,
                          yunxing=yunxing,
                          yunxing_remarks=yunxing_remarks,
                          jiaohuan=jiaohuan,
                          jiaohuan_remarks=jiaohuan_remarks,
                          shengji_jiaohuan=shengji_jiaohuan,
                          shengji_jiaohuan_remarks=shengji_jiaohuan_remarks,
                          yidi=yidi,
                          yidi_remarks=yidi_remarks,
                          renlian=renlian,
                          renlian_remarks=renlian_remarks,
                          riqi=riqi,
                          paiming=paiming,
                          zongfen=zongfen,
                      ))
                      session.commit()
                      self.write(dict(code=0, msg='成功', count=0, data=[]))
              except:
                  self.write(dict(code=-1, msg='上传失败。', count=0, data=[]))
        else:
            try:
              with DBContext('w', None, True) as session:
                session.query(Ranking).filter(Ranking.riqi == riqi).update({
                    Ranking.fuwu: fuwu,
                    Ranking.fuwu_remarks: fuwu_remarks,
                    Ranking.xitong: xitong,
                    Ranking.xitong_remarks: xitong_remarks,
                    Ranking.peizhi: peizhi,
                    Ranking.peizhi_remarks: peizhi_remarks,
                    Ranking.shengji: shengji,
                    Ranking.shengji_remarks: shengji_remarks,
                    Ranking.xtpeizhi: xtpeizhi,
                    Ranking.xtpeizhi_remarks: xtpeizhi_remarks,
                    Ranking.zhichi: zhichi,
                    Ranking.zhichi_remarks: zhichi_remarks,
                    Ranking.duanxin: duanxin,
                    Ranking.duanxin_remarks: duanxin_remarks,
                    Ranking.qudao: qudao,
                    Ranking.qudao_remarks: qudao_remarks,
                    Ranking.xiangmu: xiangmu,
                    Ranking.xiangmu_remarks: xiangmu_remarks,
                    Ranking.tuikuan: tuikuan,
                    Ranking.tuikuan_remarks: tuikuan_remarks,
                    Ranking.yunxing: yunxing,
                    Ranking.yunxing_remarks: yunxing_remarks,
                    Ranking.jiaohuan: jiaohuan,
                    Ranking.jiaohuan_remarks: jiaohuan_remarks,
                    Ranking.shengji_jiaohuan: shengji_jiaohuan,
                    Ranking.shengji_jiaohuan_remarks: shengji_jiaohuan_remarks,
                    Ranking.yidi: yidi,
                    Ranking.yidi_remarks: yidi_remarks,
                    Ranking.renlian: renlian,
                    Ranking.renlian_remarks: renlian_remarks,
                    Ranking.riqi: riqi,
                    Ranking.paiming: paiming,
                    Ranking.zongfen: zongfen,
                })
                session.commit()
                self.write(dict(code=0, msg='成功', count=0, data=[]))
            except:
                self.write(dict(code=-1, msg='上传失败。', count=0, data=[]))


class linedataHandler(BaseHandler):
    def get(self, *args, **kwargs):
        name = str(self.get_argument('name',strip=True))
        start_date = str(self.get_argument('start_date',strip=True))
        end_date = str(self.get_argument('end_date',strip=True))
        # 组装月份数组
        months_list = []
        if start_date == '':

            today = datetime.now().strftime('%Y-%m')  # 当前月份

            now = datetime.now()
            for  h in range(5,0,-1): #默认6个月
                  date = now + dateutil.relativedelta.relativedelta(months=-h)  # 上个月时间
                  # date.strftime('%Y-%m') #上个月份
                  months_list.append(date.strftime('%Y-%m'))
            months_list.append(today)
        else:
            from datetime import date
            temp_start = date(int(start_date.split('-')[0]),int(start_date.split('-')[1]),1)
            temp_end =   date(int(end_date.split('-')[0]),int(end_date.split('-')[1]),1)
            months_sum = rrule.rrule(rrule.MONTHLY,dtstart=temp_start,until=temp_end).count()

            format = '%Y-%m'  # 根据此格式来解析时间字符串为datetime.datetime()对象

            end_time = datetime.strptime(end_date, format)
            for h in range(months_sum - 1, 0, -1):
                date = end_time + dateutil.relativedelta.relativedelta(months=-h)  # 上个月时间
                # date.strftime('%Y-%m') #上个月份
                months_list.append(date.strftime('%Y-%m'))
            months_list.append(end_date)


        defen_list = []
        defen_remarks = []
        for  g  in  months_list:
            with DBContext('r') as session:
                # conditions = []
                todata = session.query(Ranking).filter(Ranking.riqi == g).all()
                tocount = session.query(Ranking).filter(Ranking.riqi == g).count()
            if tocount <= 0:
                defen_list.append(0)
            for msg in todata:
                data_dict = model_to_dict(msg)
                if name == "服务稳定性":
                    if data_dict["fuwu"]:
                        defen_list.append(data_dict["fuwu"])
                    else:
                        defen_list.append(0)
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["fuwu_remarks"]})
                elif name == "系统运行效率":
                    defen_list.append(data_dict["xitong"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["xitong_remarks"]})
                elif name == "软硬件设备配置":
                    defen_list.append(data_dict["peizhi"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["peizhi_remarks"]})
                elif name == "系统及时升级":
                    defen_list.append(data_dict["shengji"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["shengji_remarks"]})
                elif name == "跨省短信发送支持":
                    defen_list.append(data_dict["zhichi"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["zhichi_remarks"]})
                elif name == "短信发送成功率":
                    defen_list.append(data_dict["duanxin"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["duanxin_remarks"]})
                elif name == "支付渠道":
                    defen_list.append(data_dict["qudao"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["qudao_remarks"]})
                elif name == "支付项目":
                    defen_list.append(data_dict["xiangmu"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["xiangmu_remarks"]})
                elif name == "退款支持":
                    defen_list.append(data_dict["tuikuan"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["tuikuan_remarks"]})
                elif name == "运行情况":
                    defen_list.append(data_dict["yunxing"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["yunxing_remarks"]})
                elif name == "内外网数据交换":
                    defen_list.append(data_dict["jiaohuan"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["jiaohuan_remarks"]})
                elif name == "省际数据交换":
                    defen_list.append(data_dict["shengji_jiaohuan"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["shengji_jiaohuan_remarks"]})
                elif name == "异地业务请求":
                    defen_list.append(data_dict["yidi"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["yidi_remarks"]})
                elif name == "人脸识别通过率":
                    defen_list.append(data_dict["renlian"])
                    defen_remarks.append({"date":data_dict["riqi"],"remarks":data_dict["renlian_remarks"]})

        if len(defen_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=defen_list,list=months_list,remarks=defen_remarks))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

class bjdataHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data = str(self.get_argument('bjdata',strip=True))
        data_list = []
        with DBContext('r') as session:
            # conditions = []
            todata = session.query(Ranking).filter(Ranking.riqi == data).all()
            # tocount = session.query(Ranking).filter(Ranking.riqi == data).count()
            for msg in todata:
                # rankingdict = {}
                data_dict = model_to_dict(msg)
                # rankingdict["id"] = data_dict["id"]
                # rankingdict["fuwu"] = data_dict["fuwu"]
                # rankingdict["fuwu_remarks"] = data_dict["fuwu_remarks"]
                # rankingdict["xitong"] = data_dict["xitong"]
                # rankingdict["xitong_remarks"] = data_dict["xitong_remarks"]
                # rankingdict["peizhi"] = str(data_dict["peizhi"])
                # rankingdict["peizhi_remarks"] = str(data_dict["peizhi_remarks"])
                # rankingdict["shengji"] = str(data_dict["shengji"])
                # rankingdict["shengji_remarks"] = str(data_dict["shengji_remarks"])
                # rankingdict["zhichi"] = data_dict["zhichi"]
                # rankingdict["zhichi_remarks"] = data_dict["zhichi_remarks"]
                # rankingdict["duanxin_remarks"] = data_dict["duanxin_remarks"]
                # rankingdict["qudao"] = data_dict["qudao"]
                # rankingdict["zhqudao_remarksichi"] = data_dict["qudao_remarks"]
                # rankingdict["xiangmu"] = data_dict["xiangmu"]
                # rankingdict["xiangmu_remarks"] = data_dict["xiangmu_remarks"]
                # rankingdict["tuikuan"] = data_dict["tuikuan"]
                # rankingdict["tuikuan_remarks"] = data_dict["tuikuan_remarks"]
                # rankingdict["yunxing"] = data_dict["yunxing"]
                # rankingdict["yunxing_remarks"] = data_dict["yunxing_remarks"]
                # rankingdict["jiaohuan"] = data_dict["jiaohuan"]
                # rankingdict["jiaohuan_remarks"] = data_dict["jiaohuan_remarks"]
                # rankingdict["shengji_jiaohuan"] = data_dict["shengji_jiaohuan"]
                # rankingdict["shengji_jiaohuan_remarks"] = data_dict["shengji_jiaohuan_remarks"]
                # rankingdict["yidi"] = data_dict["yidi"]
                # rankingdict["yidi_remarks"] = data_dict["yidi_remarks"]
                # rankingdict["renlian"] = data_dict["renlian"]
                # rankingdict["renlian_remarks"] = data_dict["renlian_remarks"]
                # rankingdict["riqi"] = data_dict["riqi"]
                # rankingdict["paiming"] = data_dict["paiming"]
                # rankingdict["zongfen"] = data_dict["zongfen"]
                data_dict["create_time"] = ""
                data_list.append(data_dict)


        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

class uploadRankinglist2(BaseHandler):
    def post(self, *args, **kwargs):
        ###文件保存到本地
        Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_path = '{}/static/ranking/'.format(Base_DIR)
        file_body = self.request.files["file"][0]["body"]
        temp_file_name = self.request.files["file"][0]["filename"] #2020年12月广东建设运行情况.xls

        file_path = upload_path + "tempfile.xls"
        with open(file_path, 'wb') as up:
            up.write(file_body)
        df = pd.read_excel(file_path)
        allsum = len(df.index)

        if allsum > 0:
            fuwu = str(df.iloc[1, 6]),
            fuwu_remarks = str(df.iloc[1, 5]),
            xitong = str(df.iloc[2, 6]),
            xitong_remarks = str(df.iloc[2, 5]),
            peizhi = str(df.iloc[3, 6]),
            peizhi_remarks = str(df.iloc[3, 5]),
            shengji = str(df.iloc[4, 6]),
            shengji_remarks = str(df.iloc[4, 5]),
            xtpeizhi = str(df.iloc[5, 6]),
            xtpeizhi_remarks = str(df.iloc[5, 5]),
            zhichi = str(df.iloc[6, 6]),
            zhichi_remarks = str(df.iloc[6, 5]),
            duanxin = str(df.iloc[7, 6]),
            duanxin_remarks = str(df.iloc[7, 5]),
            qudao = str(df.iloc[8, 6]),
            qudao_remarks = str(df.iloc[8, 5]),
            xiangmu = str(df.iloc[9, 6]),
            xiangmu_remarks = str(df.iloc[9, 5]),
            tuikuan = str(df.iloc[10, 6]),
            tuikuan_remarks = str(df.iloc[10, 5]),
            yunxing = str(df.iloc[11, 6]),
            yunxing_remarks = str(df.iloc[11, 5]),
            jiaohuan = str(df.iloc[12, 6]),
            jiaohuan_remarks = str(df.iloc[12, 5]),
            shengji_jiaohuan = str(df.iloc[13, 6]),
            shengji_jiaohuan_remarks = str(df.iloc[13, 5]),
            yidi ="",
            yidi_remarks = "",
            renlian = "",
            renlian_remarks = "",
            riqi = temp_file_name[0:4] + '-' + temp_file_name[5:7]
            paiming = str(df.columns[6]).split('：')[1][4:5]
            zongfen = str(df.columns[6]).split('：')[1][0:2]
        with DBContext('r') as session:
                tocount = session.query(Ranking).filter(Ranking.riqi == riqi).count()
        # ins_log.read_log('info', "222222222222222222222")
        # ins_log.read_log('info', tocount)
        # ins_log.read_log('info', "1111111111111111122222222222222222")
        if tocount <= 0:
              ins_log.read_log('info', "1111111111111111122222222222222222")
              try:
                  with DBContext('w', None, True) as session:
                      session.add(Ranking(
                          fuwu=fuwu,
                          fuwu_remarks=fuwu_remarks,
                          xitong=xitong,
                          xitong_remarks=xitong_remarks,
                          peizhi=peizhi,
                          peizhi_remarks=peizhi_remarks,
                          shengji=shengji,
                          shengji_remarks=shengji_remarks,
                          xtpeizhi=xtpeizhi,
                          zhichi=zhichi,
                          xtpeizhi_remarks=xtpeizhi_remarks,
                          zhichi_remarks=zhichi_remarks,
                          duanxin=duanxin,
                          duanxin_remarks=duanxin_remarks,
                          qudao=qudao,
                          qudao_remarks=qudao_remarks,
                          xiangmu=xiangmu,
                          xiangmu_remarks=xiangmu_remarks,
                          tuikuan=tuikuan,
                          tuikuan_remarks=tuikuan_remarks,
                          yunxing=yunxing,
                          yunxing_remarks=yunxing_remarks,
                          jiaohuan=jiaohuan,
                          jiaohuan_remarks=jiaohuan_remarks,
                          shengji_jiaohuan=shengji_jiaohuan,
                          shengji_jiaohuan_remarks=shengji_jiaohuan_remarks,
                          yidi=yidi,
                          yidi_remarks=yidi_remarks,
                          renlian=renlian,
                          renlian_remarks=renlian_remarks,
                          riqi=riqi,
                          paiming=paiming,
                          zongfen=zongfen,
                      ))
                      session.commit()
                  ins_log.read_log('info', "1111111111111111123333333333")
                  self.write(dict(code=0, msg='成功', count=0, data=[]))
              except Exception as e:
                  ins_log.read_log('info', "111111111111111100000000000000")
                  self.write(dict(code=-1, msg='上传失败。', count=0, data=[]))
        else:
            try:
              with DBContext('w', None, True) as session:
                session.query(Ranking).filter(Ranking.riqi == riqi).update({
                    Ranking.fuwu: fuwu,
                    Ranking.fuwu_remarks: fuwu_remarks,
                    Ranking.xitong: xitong,
                    Ranking.xitong_remarks: xitong_remarks,
                    Ranking.peizhi: peizhi,
                    Ranking.peizhi_remarks: peizhi_remarks,
                    Ranking.shengji: shengji,
                    Ranking.shengji_remarks: shengji_remarks,
                    Ranking.xtpeizhi: xtpeizhi,
                    Ranking.xtpeizhi_remarks: xtpeizhi_remarks,
                    Ranking.zhichi: zhichi,
                    Ranking.zhichi_remarks: zhichi_remarks,
                    Ranking.duanxin: duanxin,
                    Ranking.duanxin_remarks: duanxin_remarks,
                    Ranking.qudao: qudao,
                    Ranking.qudao_remarks: qudao_remarks,
                    Ranking.xiangmu: xiangmu,
                    Ranking.xiangmu_remarks: xiangmu_remarks,
                    Ranking.tuikuan: tuikuan,
                    Ranking.tuikuan_remarks: tuikuan_remarks,
                    Ranking.yunxing: yunxing,
                    Ranking.yunxing_remarks: yunxing_remarks,
                    Ranking.jiaohuan: jiaohuan,
                    Ranking.jiaohuan_remarks: jiaohuan_remarks,
                    Ranking.shengji_jiaohuan: shengji_jiaohuan,
                    Ranking.shengji_jiaohuan_remarks: shengji_jiaohuan_remarks,
                    Ranking.riqi: riqi,
                    Ranking.yidi: yidi,
                    Ranking.yidi_remarks: yidi_remarks,
                    Ranking.renlian: renlian,
                    Ranking.renlian_remarks: renlian_remarks,
                    Ranking.paiming: paiming,
                    Ranking.zongfen: zongfen,
                })
                session.commit()
              self.write(dict(code=0, msg='成功', count=0, data=[]))
            except Exception as e:
              return self.write(dict(code=-1, msg=e))


class shangyueHandler(BaseHandler):
    def get(self, *args, **kwargs):
        now = datetime.now()
        date = now + dateutil.relativedelta.relativedelta(months=-1)  # 上个月时间
        # date.strftime('%Y-%m') #上个月份
        shangyuedate = date.strftime('%Y-%m')

        data_list = []
        ins_log.read_log('info', shangyuedate)
        with DBContext('r') as session:
            # conditions = []
            todata = session.query(Ranking).filter(Ranking.riqi == shangyuedate).all()
            # tocount = session.query(Customized).filter().count()

        for msg in todata:
            ranking_list = {}
            data_dict = model_to_dict(msg)
            ranking_list["id"] = data_dict["id"]
            ranking_list["zongfen"] = data_dict["zongfen"]
            data_list.append(ranking_list)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

meter_urls = [
    (r"/v2/accounts/meter/", MeterHandler),
    (r"/v2/accounts/meteradd/", MeteraddHandler),
    (r"/v2/accounts/ranking/", rankinglistHandler),
    (r"/v2/accounts/ranking/upload/", uploadRankinglist),
    (r"/v2/accounts/ranking/upload2/", uploadRankinglist2),
    (r"/v2/accounts/ranking/shangyue/", shangyueHandler),
    (r"/v2/accounts/linedata/", linedataHandler),
    (r"/v2/accounts/bjdata/", bjdataHandler),
]

if __name__ == "__main__":
    pass
