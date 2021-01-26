#!/usr/bin/env python
# -*-coding:utf-8-*-

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper
from datetime import datetime

Base = declarative_base()


def model_to_dict(model):
    model_dict = {}
    for key, column in class_mapper(model.__class__).c.items():
        model_dict[column.name] = getattr(model, key, None)
    return model_dict


class CustomQuery(Base):
    __tablename__ = 'custom_query'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    title = Column('title', String(50), default='')  # 标题
    dblinkId = Column('dblinkId', Integer)  # 数据库源ID
    database = Column('database', String(100), default='')  # 数据库名
    user = Column('user', String(50), default='')  # 用户名
    password = Column('password', String(100), default='')  # 密码
    sql = Column('sql', Text, default='')  # SQL
    colnames = Column('colnames', Text, default='')  # 自定义字段名
    timesTy = Column('timesTy', String(50), default='')  # 轮询频率
    timesTyVal = Column('timesTyVal', String(50), default='')  # 轮询频率值
    colalarms = Column('colalarms', Text, default='')  # 告警配置
    status = Column('status', String(5), default='1')  # 状态
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间
    update_time = Column('update_time', DateTime(), default=datetime.now, onupdate=datetime.now)  # 记录更新时间
    description = Column('description', Text, default='')  # 描述
    seq = Column('seq', Integer)  # 序号
    groupID = Column('groupID', String(255), default='')  # 层级组ID
    urls = Column('urls', String(512), default='')  # urls
    type = Column('type', String(50), default='')  # 监控类型


class CustomQuerySub(Base):
    __tablename__ = 'custom_query_sub'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    qid = Column('qid', Integer)  # 支队表ID
    title = Column('title', String(50), default='')  # 标题
    dblinkId = Column('dblinkId', Integer)  # 数据库源ID
    database = Column('database', String(100), default='')  # 数据库名
    user = Column('user', String(50), default='')  # 用户名
    password = Column('password', String(100), default='')  # 密码
    sql = Column('sql', Text, default='')  # SQL
    colnames = Column('colnames', Text, default='')  # 自定义字段名
    timesTy = Column('timesTy', String(50), default='')  # 轮询频率
    timesTyVal = Column('timesTyVal', String(50), default='')  # 轮询频率值
    colalarms = Column('colalarms', Text, default='')  # 告警配置
    status = Column('status', String(5), default='1')  # 状态
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间
    update_time = Column('update_time', DateTime(), default=datetime.now, onupdate=datetime.now)  # 记录更新时间
    description = Column('description', Text, default='')  # 描述
    seq = Column('seq', Integer)  # 序号
    groupID = Column('groupID', String(255), default='')  # 层级组ID
    groupName = Column('groupName', String(255), default='')  # 二级组名
    group2ndSeq = Column('group2ndSeq', Integer, default='')  # 二级组排序
    zdlinkID = Column('zdlinkID', Integer, default='')  # 支队连接ID


class CustomGroup(Base):
    __tablename__ = 'custom_group'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    groupName = Column('groupName', String(50), default='')  # 组名
    grouptype = Column('grouptype', Integer)  # 类型 1：一级分组。 2：二级分组
    groupSeq = Column('groupSeq', Integer)  # 排序号


class CustomZdLink(Base):
    __tablename__ = 'custom_zdlink'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(50), default='')
    link = Column('link', String(255), default='')


class CustomTmp(Base):
    __tablename__ = 'custom_tmp'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    tmpNa = Column('tmpNa', String(50), default='')  # 标题
    selectionAll = Column('selectionAll', Text, default='')
    username = Column('username', String(50), default='')
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间


class Score(Base):
    __tablename__ = 'scorelist'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    today = Column('today', String(200), default='')  # 组名
    fuwu_defen = Column('fuwu_defen', String(5), default='')  # 组名
    fuwu_remarks = Column('fuwu_remarks', Text, default='')
    xitong_defen = Column('xitong_defen', String(5), default='')
    xitong_remarks = Column('xitong_remarks', Text, default='')
    duanxin_defen = Column('duanxin_defen', String(5), default='')
    duanxin_remarks = Column('duanxin_remarks', Text, default='')
    nwwang_defen = Column('nwwang_defen', String(5), default='')
    nwwang_remarks = Column('nwwang_remarks', Text, default='')
    yidi_defen = Column('yidi_defen', String(5), default='')
    yidi_remarks = Column('yidi_remarks', Text, default='')
    renlian_defen = Column('renlian_defen', String(5), default='')
    renlian_remarks = Column('renlian_remarks', Text, default='')
    yunxing_defen = Column('yunxing_defen', String(5), default='')
    yunxing_remarks = Column('yunxing_remarks', Text, default='')
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间


class Customized(Base):
    __tablename__ = 'customizedList'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    totitle = Column('totitle', String(1500))  # 标题
    dbid = Column('dbid', String(50), )  # 数据库脚本id
    cycle = Column('cycle', String(50), )  # 周期
    times = Column('times', String(20))  # 执行时间
    flag = Column('flag', String(20))
    todate = Column('todate', String(100))
    download_dir = Column('download_dir', String(50))  # 文件目录
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间
    start_end = Column('start_end', String(50))


class Ranking(Base):
    __tablename__ = 'ranking'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    fuwu = Column('fuwu', String(5))
    fuwu_remarks = Column('fuwu_remarks', Text, default='')
    xitong = Column('xitong', String(5),)
    xitong_remarks = Column('xitong_remarks', Text, default='')
    peizhi = Column('peizhi', String(5),)
    peizhi_remarks = Column('peizhi_remarks', Text, default='')
    shengji = Column('shengji', String(5))
    shengji_remarks = Column('shengji_remarks', Text, default='')
    zhichi = Column('zhichi', String(5))
    zhichi_remarks = Column('zhichi_remarks', Text, default='')
    duanxin = Column('duanxin', String(5))
    duanxin_remarks = Column('duanxin_remarks', Text, default='')
    qudao = Column('qudao', String(5))
    qudao_remarks = Column('qudao_remarks', Text, default='')
    xiangmu = Column('xiangmu', String(5))
    xiangmu_remarks = Column('xiangmu_remarks', Text, default='')
    tuikuan = Column('tuikuan', String(5))
    tuikuan_remarks = Column('tuikuan_remarks', Text, default='')
    yunxing = Column('yunxing', String(5))
    yunxing_remarks = Column('yunxing_remarks', Text, default='')
    jiaohuan = Column('jiaohuan', String(5))
    jiaohuan_remarks = Column('jiaohuan_remarks', Text, default='')
    shengji_jiaohuan = Column('shengji_jiaohuan', String(5))
    shengji_jiaohuan_remarks = Column('shengji_jiaohuan_remarks', Text, default='')
    yidi = Column('yidi', String(5))
    yidi_remarks = Column('yidi_remarks', Text, default='')
    renlian = Column('renlian', String(5))
    renlian_remarks = Column('renlian_remarks', Text, default='')
    riqi = Column('riqi', String(30))
    paiming = Column('paiming', String(5))
    zongfen = Column('zongfen', String(5))
    create_time = Column('create_time', DateTime(), default=datetime.now)
class CustomQueryLog(Base):
    __tablename__ = 'custom_query_log'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    title = Column('title', String(50), default='')  # 标题
    qid = Column('qid', Integer, index=True) # 查询项目id
    ty = Column('ty', Integer, index=True)  # 总队 0 支队 1
    targeted_val = Column('targeted_val', String(50), default='')  # 指标值
    remark = Column('remark', String(50), default='')  # 备注
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间
