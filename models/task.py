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
