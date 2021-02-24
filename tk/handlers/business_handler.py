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
from models.task import Business,model_to_dict
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

class businessHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data = str(self.get_argument('start_date',strip=True))
        ins_log.read_log('info', data)
        data_list = []
        temp_list3 = []

        city_list = ["广州市","韶关市","深圳市","珠海市","佛山市","汕头市","江门市","湛江市","茂名市","肇庆市","惠州市",
                     "梅州市","汕尾市","河源市","阳江市","清远市","东莞市","中山市","潮州市","揭阳市","云浮市"]
        with DBContext('r') as session:
            # conditions = []
            todata = session.query(Business).filter(Business.riqi == data).all()
            # tocount = session.query(Business).filter(Business.riqi == data).count()
            for msg in todata:
                businessdict = {}
                data_dict = model_to_dict(msg)
                businessdict["id"] = data_dict["id"]
                businessdict["广州市"] = data_dict["guangzhou"]
                businessdict["韶关市"] = data_dict["shaoguan"]
                businessdict["深圳市"] = data_dict["shenzhen"]
                businessdict["珠海市"] = data_dict["zhuhai"]
                businessdict["佛山市"] = str(data_dict["foshan"])
                businessdict["汕头市"] = str(data_dict["shantou"])
                businessdict["江门市"] = str(data_dict["jiangmen"])
                businessdict["湛江市"] = str(data_dict["zhanjiang"])
                businessdict["茂名市"] = str(data_dict["maoming"])
                businessdict["肇庆市"] = data_dict["zhaoqing"]
                businessdict["惠州市"] = data_dict["huizhou"]
                businessdict["梅州市"] = data_dict["meizhou"]
                businessdict["汕尾市"] = data_dict["shanwei"]
                businessdict["河源市"] = data_dict["heyuan"]
                businessdict["阳江市"] = data_dict["yangjiang"]
                businessdict["清远市"] = data_dict["qingyuan"]
                businessdict["东莞市"] = data_dict["dongguan"]
                businessdict["中山市"] = data_dict["zhongshan"]
                businessdict["潮州市"] = data_dict["chaozhou"]
                businessdict["揭阳市"] = data_dict["jieyang"]
                businessdict["云浮市"] = data_dict["yunfu"]
                data_list.append(businessdict)

        for g in data_list:
              for k in city_list:
                  temp_list3.append({eval(g[k])["city"]:int(eval(g[k])["defen"])})


        #按得分排序  字典的value排序
        temp_list3.sort(key=lambda x: list(x.values()))
        velue_list = []
        key_list = []
        for d in temp_list3:
          velue_list.append(list(d.values())[0])
          key_list.append(list(d.keys())[0])
        ins_log.read_log('info', velue_list)
        ins_log.read_log('info', key_list)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=data_list,key=key_list,velue=velue_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

class uploadRankinglist3(BaseHandler):
    def post(self, *args, **kwargs):
        ###文件保存到本地
        Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_path = '{}/static/business/'.format(Base_DIR)
        file_body = self.request.files["file"][0]["body"]
        temp_file_name = self.request.files["file"][0]["filename"] #2020年12月广东业务应用情况.xls
        file_path = upload_path + "tempfile.xls"
        riqi = temp_file_name[0:4] + '-' + temp_file_name[5:7]
        with open(file_path, 'wb') as up:
            up.write(file_body)
        df = pd.read_excel(file_path)
        allsum = len(df.index)
        temp_list = []

        if allsum > 0:
            for i in  range(5,26):
                temp_dict = {
                    "city":str(df.iloc[i, 0]),
                    "bhlpz": str(df.iloc[i, 1]),
                    "slmjbz": str(df.iloc[i, 2]),
                    "dzjkcl": str(df.iloc[i, 3]),
                    "jtsgkc": str(df.iloc[i, 4]),
                    "yxjdchp": str(df.iloc[i, 5]),
                    "mfsyjy": str(df.iloc[i, 6]),
                    "pzywjscl": str(df.iloc[i, 7]),
                    "yxhpzljsshl": str(df.iloc[i, 8]),
                    "tfsqjschl": str(df.iloc[i, 9]),
                    "mfsyjyjsshl": str(df.iloc[i, 10]),
                    "yhxxjsshl": str(df.iloc[i, 11]),
                    "wbywmyd": str(df.iloc[i, 12]),
                    "yhfkmyd": str(df.iloc[i, 13]),
                    "yzsfwjcxxwh": str(df.iloc[i, 14]),
                    "jtaqxc": str(df.iloc[i, 15]),
                    "defen": str(df.iloc[i, 16]),
                }
                temp_list.append(temp_dict)

        with DBContext('r') as session:
                tocount = session.query(Business).filter(Business.riqi == riqi).count()

        if tocount <= 0:

              try:
                  with DBContext('w', None, True) as session:
                      session.add(Business(
                          riqi=riqi,
                          guangzhou=str(temp_list[0]),
                          shaoguan =str(temp_list[1]),
                          shenzhen =str(temp_list[2]),
                          zhuhai =str(temp_list[3]),
                          shantou =str(temp_list[4]),
                          foshan =str(temp_list[5]),
                          jiangmen =str(temp_list[6]),
                          zhanjiang =str(temp_list[7]),
                          maoming =str(temp_list[8]),
                          zhaoqing =str(temp_list[9]),
                          huizhou =str(temp_list[10]),
                          meizhou =str(temp_list[11]),
                          shanwei =str(temp_list[12]),
                          heyuan =str(temp_list[13]),
                          yangjiang =str(temp_list[14]),
                          qingyuan =str(temp_list[15]),
                          dongguan =str(temp_list[16]),
                          zhongshan =str(temp_list[17]),
                          chaozhou =str(temp_list[18]),
                          jieyang =str(temp_list[19]),
                          yunfu =str(temp_list[20]),
                      ))
                      session.commit()
                  self.write(dict(code=0, msg='成功', count=0, data=[]))
              except Exception as e:
                  self.write(dict(code=-1, msg='上传失败。', count=0, data=[]))
        else:
            try:
              with DBContext('w', None, True) as session:
                session.query(Business).filter(Business.riqi == riqi).update({
                    Business.riqi : riqi,
                    Business.guangzhou : str(temp_list[0]),
                    Business.shaoguan : str(temp_list[1]),
                    Business.shenzhen : str(temp_list[2]),
                    Business.zhuhai : str(temp_list[3]),
                    Business.shantou : str(temp_list[4]),
                    Business.foshan : str(temp_list[5]),
                    Business.jiangmen : str(temp_list[6]),
                    Business.zhanjiang : str(temp_list[7]),
                    Business.maoming : str(temp_list[8]),
                    Business.zhaoqing : str(temp_list[9]),
                    Business.huizhou : str(temp_list[10]),
                    Business.meizhou : str(temp_list[11]),
                    Business.shanwei : str(temp_list[12]),
                    Business.heyuan : str(temp_list[13]),
                    Business.yangjiang : str(temp_list[14]),
                    Business.qingyuan : str(temp_list[15]),
                    Business.dongguan : str(temp_list[16]),
                    Business.zhongshan :  str(temp_list[17]),
                    Business.chaozhou : str(temp_list[18]),
                    Business.jieyang : str(temp_list[19]),
                    Business.yunfu : str(temp_list[20]),
                })
                session.commit()
              self.write(dict(code=0, msg='成功', count=0, data=[]))
            except Exception as e:
              return self.write(dict(code=-1, msg=e))


class getcityHandler(BaseHandler):
    def get(self, *args, **kwargs):
        bjriqi = str(self.get_argument('bjriqi',strip=True))
        city = str(self.get_argument('city', strip=True))
        ins_log.read_log('info', bjriqi)
        ins_log.read_log('info', city)
        data_list = []
        temp_list3 = []


        with DBContext('r') as session:
            # conditions = []
            todata = session.query(Business).filter(Business.riqi == bjriqi).all()
            # tocount = session.query(Business).filter(Business.riqi == data).count()
            for msg in todata:
                businessdict = {}
                data_dict = model_to_dict(msg)
                businessdict["id"] = data_dict["id"]
                businessdict[city] = data_dict[city]
                data_list.append(businessdict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

class businesspostHandler(BaseHandler):
    def post(self, *args, **kwargs):
        #{"riqi":this.bjriqi,"city":this.city,"datalist":this.formValidate}
        data = json.loads(self.request.body.decode("utf-8"))
        riqi = str(data.get('riqi', ""))
        city = str(data.get('city', ""))
        datalist = str(data.get('datalist', ""))
        temp_dict6 = "{ Business." + city  +  ": datalist}"
        # ins_log.read_log('info', "1111111111111111122222222222222222")
        # ins_log.read_log('info', temp_dict6)
        # ins_log.read_log('info', "1111111111111111122222222222222222")
        tempdict  = {}
        tempdict  = eval(temp_dict6)
        with DBContext('w', None, True) as session:
                session.query(Business).filter(Business.riqi == riqi).update(tempdict)
                session.commit()
        self.write(dict(code=0, msg='成功', count=0, data=[]))


class getzhibiaoHandler(BaseHandler):
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        startdate = str(data.get('startdate', ""))
        enddate = str(data.get('enddate', ""))
        zhibiao = str(data.get('zhibiao', ""))
        city = str(data.get('city', ""))

        data_list = []
        temp_list3 = []
        months_list = []
        allzhibiaoList = {"bhlpz": '补换领牌证',"slmjbz": '申领免检标志',"dzjkcl": '电子监控处理',"jtsgkc": '交通事故快处',
                          "yxjdchp": '预选机动车号牌',"mfsyjy": '满分审验教育',"pzywjscl": '牌证业务及时受理率',"yxhpzljsshl": '预选号牌资料及时审核率',
                          "tfsqjschl": '退费申请及时受理率',"mfsyjyjsshl": '满分审验教育及时审核率',"yhxxjsshl": '用户信息及时审核率',"wbywmyd": '网办业务满意度',
                           "yhfkmyd": '用户反馈满意度',"yzsfwjcxxwh": '一站式服务基础信息维护',"jtaqxc": '交通安全宣传'}

        from datetime import date
        temp_start = date(int(startdate.split('-')[0]), int(startdate.split('-')[1]), 1)
        temp_end = date(int(enddate.split('-')[0]), int(enddate.split('-')[1]), 1)
        months_sum = rrule.rrule(rrule.MONTHLY, dtstart=temp_start, until=temp_end).count()

        format = '%Y-%m'  # 根据此格式来解析时间字符串为datetime.datetime()对象

        end_time = datetime.strptime(enddate, format)
        for h in range(months_sum - 1, 0, -1):
            date = end_time + dateutil.relativedelta.relativedelta(months=-h)  # 上个月时间
            # date.strftime('%Y-%m') #上个月份
            months_list.append(date.strftime('%Y-%m'))
        months_list.append(enddate)

        ins_log.read_log('info', startdate)
        ins_log.read_log('info', enddate)
        ins_log.read_log('info', zhibiao)
        ins_log.read_log('info', city)
        ins_log.read_log('info', months_list)
        temo_zhibiao_list = []
        for  z in eval(zhibiao):
          data_list = []
          for d in  months_list:
            with DBContext('r') as session:
                todata = session.query(Business).filter(Business.riqi == d).all()
                tocount = session.query(Business).filter(Business.riqi == d).count()
                for msg in todata:
                    businessdict = {}
                    data_dict = model_to_dict(msg)
                    businessdict["id"] = data_dict["id"]
                    businessdict[city] = data_dict[city]
                    data_list.append(eval(data_dict[city])[z])
                if tocount < 1:
                    data_list.append(0)
          temo_zhibiao_dict = {
              "name": allzhibiaoList[z],
              "keyname":z,
              "type": 'line',
              # "stack": '总量',
              "data": data_list
          }
          temo_zhibiao_list.append(temo_zhibiao_dict)
        ins_log.read_log('info', startdate)
        ins_log.read_log('info', enddate)
        ins_log.read_log('info', zhibiao)
        ins_log.read_log('info', city)
        ins_log.read_log('info', months_list)
        ins_log.read_log('info', data_list)
        legendlist = []
        for z in eval(zhibiao):
            legendlist.append(allzhibiaoList[z])
        if len(temo_zhibiao_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=temo_zhibiao_list,months=months_list,legendlist = legendlist))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

business_urls = [
    (r"/v2/accounts/business/upload3/", uploadRankinglist3),
    (r"/v2/accounts/business/",businessHandler ),
    (r"/v2/accounts/getcity/",getcityHandler ),
    (r"/v2/accounts/zhibiao/",getzhibiaoHandler ),
    (r"/v2/accounts/businesspost/",businesspostHandler ),
]

if __name__ == "__main__":
    pass
