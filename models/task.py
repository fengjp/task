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
    totitle = Column('totitle', String(500))  # 标题
    header = Column('header', String(500))  # 标题
    dbname_id = Column('dbname_id', String(300))  # 数据源
    dataname = Column('dataname', String(300))  # 数据库名
    dbid = Column('dbid', String(50), ) #id
    cycle  = Column('cycle', String(50), ) #id
    times = Column('times', String(20)) #执行时间
    download_dir = Column('download_dir', String(50)) #文件目录
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间