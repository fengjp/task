#!/usr/bin/env python
# -*-coding:utf-8-*-
import os
import sys
_op = os.path.dirname
cwdir = _op(os.path.abspath(__file__))
project_path = _op(_op(os.path.abspath(__file__)))
app_path = _op(project_path)
sys.path.insert(0, project_path)
import dateutil.relativedelta
from datetime import datetime
import requests
from settings import CUSTOM_DB_INFO
from multiprocessing import Pool
from libs.mysql_conn import MysqlBase
from libs.aes_coder import encrypt, decrypt
from libs.mysql_conn import MysqlBase
from libs.oracle_conn import OracleBase

def getdatebase(datebase_name, select_str):
    CUSTOM_DB_INFO['db'] = datebase_name
    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
    db_info = mysql_conn.query(select_str)
    return db_info
def change_datebase(datebase_name, select_str):
    CUSTOM_DB_INFO['db'] = datebase_name
    mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
    db_info = mysql_conn.change(select_str)
    return db_info
#互联网平台网页服务监控（网页） https://gd.122.gov.cn/
def web12123():
    # while 1:
      print("请求https://gd.122.gov.cn/开始")
      toSeconds = 0
      req = requests.get("https://gd.122.gov.cn/")
      if req.status_code != 200:
            toSeconds = req.elapsed.microseconds/1000000   #1秒=1000000微妙
            print(toSeconds)
      else:
          pass

      #获取当前月份
      set_day = "'" + datetime.now().strftime('%Y-%m') + "'"
      sql_str = "select id,fuwu_defen,fuwu_remarks from  scorelist where today = " + set_day
      meter_date = getdatebase("codo_task", sql_str)

      if len(meter_date):
             if toSeconds > 0:
                defenlist = []
                get_id,get_defen, get_remarks  = meter_date[0]
                defen_sum = int(get_defen)
                remarkslist = eval(get_remarks)
                remarks = {}
                remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                remarks["getlongtime"] = toSeconds
                remarkslist.append(remarks)
                for  i  in remarkslist:
                    defenlist.append(int(i["getlongtime"]))  #获取时长列表，取最长的时长

                if max(defenlist) >3*60*60:  #连续服务故障3小时以上的，扣10分(满分是10分)
                    defen_sum = 10 - 10
                elif  1*60*60 < max(defenlist) <= 3*60*60:  #对于互联网平台（网页版）连续服务故障1至3小时的，扣5分;(满分是10分)
                    defen_sum = 10 - 5
                toremark = '"' + str(remarkslist) + '"'
                defen_str = '"' + str(defen_sum) + '"'
                sql_str3 = "update  scorelist set fuwu_defen = "  + defen_str +","+  "  fuwu_remarks=" + toremark +  "  where id=" + str(get_id)
                print(sql_str3)
                get_num = change_datebase("codo_task", sql_str3)

      else:
                #新增一条数据
                remarkslist = []
                remarks = {}  # {"gettime":"","getlongtime":""}
                remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                remarks["getlongtime"] = toSeconds
                remarkslist.append(remarks)
                toremark  =  '"' + str(remarkslist) + '"'
                set_creattime = '"' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '"'
                defen_sum = 10
                if toSeconds >3*60*60:  #连续服务故障3小时以上的，扣10分(满分是10分)
                    defen_sum = 10 - 10
                elif  1*60*60 <  toSeconds <= 3*60*60:  #对于互联网平台（网页版）连续服务故障1至3小时的，扣5分;(满分是10分)
                    defen_sum = 10 - 5
                defen_str = '"' + str(defen_sum) + '"'

                temp_str = "  , " +defen_str +"," + toremark +   " , '10' , '[]' , '5' , '[]' , '10', '[]' , '5' , '[]' , '5' , '[]', '10' , '[]' ,"

                sql_str2 = "insert into scorelist(today,fuwu_defen,fuwu_remarks,xitong_defen,xitong_remarks,duanxin_defen,duanxin_remarks,nwwang_defen," \
                          +  "nwwang_remarks,yidi_defen,yidi_remarks,renlian_defen,renlian_remarks,yunxing_defen,yunxing_remarks,create_time) " \
                          +  "  values("  + set_day + temp_str + set_creattime + ")"

                get_num = change_datebase("codo_task", sql_str2)


#APP应用服务监控(交管12123APP)   http://gd.122.gov.cn/app/m/monitor
def app12123():
    # while 1:
      print("请求http://gd.122.gov.cn/app/m/monitor开始")
      toSeconds = 0
      req = requests.get("http://gd.122.gov.cn/app/m/monitor")
      if req.status_code != 200:
            toSeconds = req.elapsed.microseconds/1000000   #1秒=1000000微妙
            print(toSeconds)
      else:
          pass

      #获取当前月份
      set_day = "'" + datetime.now().strftime('%Y-%m') + "'"
      sql_str = "select id,fuwu_defen,fuwu_remarks from  scorelist where today = " + set_day
      meter_date = getdatebase("codo_task", sql_str)

      if len(meter_date):
             if toSeconds > 0:
                defenlist = []
                get_id,get_defen, get_remarks  = meter_date[0]
                defen_sum = int(get_defen)
                remarkslist = eval(get_remarks)
                remarks = {}
                remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                remarks["getlongtime"] = toSeconds
                remarkslist.append(remarks)
                for  i  in remarkslist:
                    defenlist.append(int(i["getlongtime"]))  #获取时长列表，取最长的时长

                if max(defenlist) >2*60*60:  #连续服务故障2小时以上的，扣10分(满分是10分)
                    defen_sum = 10 - 10
                elif  1*60*60 < max(defenlist) <= 2*60*60:  #对于互联网平台（网页版）连续服务故障1至2小时的，扣5分;(满分是10分)
                    defen_sum = 10 - 5
                toremark = '"' + str(remarkslist) + '"'
                defen_str = '"' + str(defen_sum) + '"'
                sql_str3 = "update  scorelist set fuwu_defen = "  + defen_str +","+  "  fuwu_remarks=" + toremark +  "  where id=" + str(get_id)
                print(sql_str3)
                get_num = change_datebase("codo_task", sql_str3)

      else:
                #新增一条数据
                remarkslist = []
                remarks = {}  # {"gettime":"","getlongtime":""}
                remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                remarks["getlongtime"] = toSeconds
                remarkslist.append(remarks)
                toremark  =  '"' + str(remarkslist) + '"'
                set_creattime = '"' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '"'
                defen_sum = 10
                if toSeconds >2*60*60:  #连续服务故障2小时以上的，扣10分(满分是10分)
                    defen_sum = 10 - 10
                elif  1*60*60 <  toSeconds <= 2*60*60:  #对于互联网平台（网页版）连续服务故障1至2小时的，扣5分;(满分是10分)
                    defen_sum = 10 - 5
                defen_str = '"' + str(defen_sum) + '"'

                temp_str = "  , " +defen_str +"," + toremark +   " , '10' , '[]' , '5' , '[]' , '10', '[]' , '10' , '[]' , '10' , '[]', '10' , '[]' ,"

                sql_str2 = "insert into scorelist(today,fuwu_defen,fuwu_remarks,xitong_defen,xitong_remarks,duanxin_defen,duanxin_remarks,nwwang_defen," \
                          +  "nwwang_remarks,yidi_defen,yidi_remarks,renlian_defen,renlian_remarks,yunxing_defen,yunxing_remarks,create_time) " \
                          +  "  values("  + set_day + temp_str + set_creattime + ")"

                get_num = change_datebase("codo_task", sql_str2)


#APP应用服务监控(交管12123APP)   http://gd.122.gov.cn/app/m/monitor
def xitong():
    all_url =[
        "https://gd.122.gov.cn/veh/monitor", #机动车服务监控
        "https://gd.122.gov.cn/veh1/monitor",#机动车选号服务监控
        "https://gd.122.gov.cn/vio/monitor",  # 机动车违法服务监控
        "https://gd.122.gov.cn/mhs/monitor",#两个教育服务监控
        "https://gd.122.gov.cn/user/m/monitor",#用户鉴权服务监控
        "https://gd.122.gov.cn/sys/m/monitor",#互联网管理后台服务监控
        "https://gd.122.gov.cn/drv/monitor",#驾驶证服务监控
    ]
    for k in  all_url:
            print("请求" + k + "开始")
            toSeconds = 0
            req = requests.get(k)
            if req.status_code != 200:
                  toSeconds = req.elapsed.microseconds/1000000   #1秒=1000000微妙
                  print(toSeconds)
            else:
               pass

            #获取当前月份
            set_day = "'" + datetime.now().strftime('%Y-%m') + "'"
            sql_str = "select id,xitong_defen,xitong_remarks from  scorelist where today = " + set_day
            meter_date = getdatebase("codo_task", sql_str)

            if len(meter_date):
                if toSeconds > 0:
                   defenlist = []
                   get_id,get_defen, get_remarks  = meter_date[0]

                   remarkslist = eval(get_remarks)
                   remarks = {}
                   remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                   remarks["getlongtime"] = toSeconds
                   remarkslist.append(remarks)
                   for  i  in remarkslist:
                       defenlist.append(int(i["getlongtime"]))  #获取时长列表，取最长的时长

                   #对于请求服务处理平均时间小于0.1秒的，得10分，请求服务处理平均时间每增加0.1秒，扣1分，直至0分为止。
                   if  max(defenlist) == 0:
                       defen_sum = 10
                   else:
                       defen_sum = 10 - int((max(defenlist) - 0.1) / 0.1)
                   toremark = '"' + str(remarkslist) + '"'
                   defen_str = '"' + str(defen_sum) + '"'
                   sql_str3 = "update  scorelist set xitong_defen = "  + defen_str +","+  "  xitong_remarks=" + toremark +  "  where id=" + str(get_id)
                   # print(sql_str3)
                   get_num = change_datebase("codo_task", sql_str3)

            else:
                #新增一条数据
                remarkslist = []
                remarks = {}  # {"gettime":"","getlongtime":""}
                remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                remarks["getlongtime"] = toSeconds
                remarkslist.append(remarks)
                toremark  =  '"' + str(remarkslist) + '"'
                set_creattime = '"' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '"'
                defen_sum = 10
                # 对于请求服务处理平均时间小于0.1秒的，得10分，请求服务处理平均时间每增加0.1秒，扣1分，直至0分为止。
                if toSeconds == 0:
                    defen_sum = 10
                else:
                    defen_sum = 10 - int((toSeconds - 0.1) / 0.1)
                defen_str = '"' + str(defen_sum) + '"'

                temp_str = "  , " +defen_str +"," + toremark +   " , '5' , '[]' , '10', '[]' , '10' , '[]' , '10' , '[]', '10' , '[]' ,"

                sql_str2 = "insert into scorelist(today,xitong_defen,xitong_remarks,duanxin_defen,duanxin_remarks,nwwang_defen," \
                          +  "nwwang_remarks,yidi_defen,yidi_remarks,renlian_defen,renlian_remarks,yunxing_defen,yunxing_remarks,create_time) " \
                          +  "  values("  + set_day + temp_str + set_creattime + ")"

                get_num = change_datebase("codo_task", sql_str2)


#支付平台地址监控http://wsjf.gdgpo.gov.cn/GdOnlinePay/ 运行支付
def yunxing():
    print("请求支付平台地址监控http://wsjf.gdgpo.gov.cn/GdOnlinePay/开始")
    toSeconds = 0
    req = requests.get("http://wsjf.gdgpo.gov.cn/GdOnlinePay/")
    if req.status_code != 200:
        toSeconds = req.elapsed.microseconds / 1000000  # 1秒=1000000微妙
        print(toSeconds)
    else:
        pass

    # 获取当前月份
    set_day = "'" + datetime.now().strftime('%Y-%m') + "'"
    sql_str = "select id,yunxing_defen,yunxing_remarks from  scorelist where today = " + set_day
    meter_date = getdatebase("codo_task", sql_str)

    if len(meter_date):
        if toSeconds > 0:
            defenlist = []
            get_id, get_defen, get_remarks = meter_date[0]
            defen_sum = int(get_defen)
            remarkslist = eval(get_remarks)
            remarks = {}
            remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            remarks["getlongtime"] = toSeconds
            remarkslist.append(remarks)
            for i in remarkslist:
                defenlist.append(int(i["getlongtime"]))  # 获取时长列表，取最长的时长

            if max(defenlist) < 2  * 60:  # 监测用户网上支付成功交易的平均操作时长，对于用户平均操作时长小于2分钟的，得5分
                defen_sum = 5

            toremark = '"' + str(remarkslist) + '"'
            defen_str = '"' + str(defen_sum) + '"'
            sql_str3 = "update  scorelist set yunxing_defen = " + defen_str + "," + "  yunxing_remarks=" + toremark + "  where id=" + str(get_id)
            # print(sql_str3)
            get_num = change_datebase("codo_task", sql_str3)

    else:
        # 新增一条数据
        remarkslist = []
        remarks = {}  # {"gettime":"","getlongtime":""}
        remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        remarks["getlongtime"] = toSeconds
        remarkslist.append(remarks)
        toremark = '"' + str(remarkslist) + '"'
        set_creattime = '"' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '"'
        defen_sum = 10
        if toSeconds < 2 * 60:  # 监测用户网上支付成功交易的平均操作时长，对于用户平均操作时长小于2分钟的，得5分
            defen_sum = 5
        defen_str = '"' + str(defen_sum) + '"'

        temp_str = "  , " + defen_str + "," + toremark

        sql_str2 = "insert into scorelist(today,yunxing_defen,yunxing_remarks,create_time) " \
                   + "  values(" + set_day + temp_str + set_creattime + ")"

        get_num = change_datebase("codo_task", sql_str2)



def renlian():
    print("人脸识别率统计：开始")
    temp_sql_str5 = "select   sum(decode(rlsbzt,'1',1,0))  as cgl , count(*) as zl ,sum(decode(rlsbzt,'1',1,0))/count(*) from  net_mhs_face_result where  cjsj>=to_date('startdate','yyyymmdd') and  cjsj<to_date('enddate','yyyymmdd')"

    today = str(datetime.now().strftime('%Y%m')) + "01"  # 当前月份
    now = datetime.now()
    date = now + dateutil.relativedelta.relativedelta(months=-1)  # 上个月时间
    befor_day = str(date.strftime('%Y%m'))  + "01"  #上个月份
    temp_sql_str5 = str(temp_sql_str5).replace('startdate',befor_day)
    sql_str5 = str(temp_sql_str5).replace('enddate',today)
    print("9999999999999999999999")
    print(sql_str5)
    print(today)
    print(befor_day)
    print(sql_str5)
    print("9999999999999999999999")
    sql_str = "select id,db_host,db_port,db_user,db_pwd,db_type,db_instance  from  asset_db"
    asset_date = getdatebase("codo_cmdb",sql_str)  # 数据库源
    for s_id,s_db_host,s_db_port,s_db_user,s_db_pwd,s_db_type,s_db_instance in asset_date: # 数据库源
       CUSTOM_DB_INFO = dict(
          host=s_db_host,
          port=s_db_port,
          user=s_db_user,
          passwd=decrypt(s_db_pwd),
          db=s_db_instance # 库名
          )
       print("11111111111111111111111111111111111111")
       print(CUSTOM_DB_INFO)
       print("11111111111111111111111111111111111111")
       try:
            if s_db_type == "mysql":
                   mysql_conn = MysqlBase(**CUSTOM_DB_INFO)
                   db_data = mysql_conn.query(sql_str5)
            if s_db_type == "oracle":
                   oracle_conn = OracleBase(**CUSTOM_DB_INFO)
                   db_data = oracle_conn.query(sql_str5)
       except:
              traceback.print_exc()
    #duanxin_date = getdatebase("codo_task", sql_str5)
    # 获取当前月份
    set_day = "'" + datetime.now().strftime('%Y-%m') + "'"
    sql_str = "select id,renlian_defen,renlian_remarks from  scorelist where today = " + set_day
    meter_date = getdatebase("codo_task", sql_str)

    if len(meter_date):
        # if toSeconds > 0:
            defenlist = []
            get_id, get_defen, get_remarks = meter_date[0]
            defen_sum = int(get_defen)
            remarkslist = eval(get_remarks)
            remarks = {}
            remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            remarks["getlongtime"] = 0 
            remarkslist.append(remarks)
            for i in remarkslist:
                defenlist.append(int(i["getlongtime"]))  # 获取时长列表，取最长的时长

            if max(defenlist) < 2  * 60:  # 监测用户网上支付成功交易的平均操作时长，对于用户平均操作时长小于2分钟的，得5分
                defen_sum = 5

            toremark = '"' + str(remarkslist) + '"'
            defen_str = '"' + str(defen_sum) + '"'
            sql_str3 = "update  scorelist set duanxin_defen = " + defen_str + "," + "  duanxin_remarks=" + toremark + "  where id=" + str(get_id)
            # print(sql_str3)
            get_num = change_datebase("codo_task", sql_str3)

    else:
        # 新增一条数据
        remarkslist = []
        remarks = {}  # {"gettime":"","getlongtime":""}
        remarks["gettime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        remarks["getlongtime"] = 0
        remarkslist.append(remarks)
        toremark = '"' + str(remarkslist) + '"'
        set_creattime = '"' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '"'
        defen_sum = 10

        defen_str = '"' + str(defen_sum) + '"'

        temp_str = "  , " + defen_str + "," + toremark

        sql_str2 = "insert into scorelist(today,yunxing_defen,yunxing_remarks,create_time) " \
                   + "  values(" + set_day + temp_str + set_creattime + ")"

        get_num = change_datebase("codo_task", sql_str2)





if __name__ == "__main__":
   while(True):
     web12123()
     app12123()
     xitong()
     yunxing()
     # renlian()
     
