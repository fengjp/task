#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
新版办件数据上报
'''


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


class CertDataUpLoadLog(Base):
    __tablename__ = 'certDataUpLoadLog'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    topic = Column('topic', String(50), default='')  # kafka主题
    total = Column('total', Integer)  # 总数
    success = Column('success', Integer)  # 成功
    failed = Column('failed', Integer)  # 失败
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间

class CertDataUpLoadError(Base):
    __tablename__ = 'certDataUpLoadError'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    topic = Column('topic', String(50), default='')  # kafka主题
    data = Column('data', Text, default='')
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间

class CertDataDownLoadError(Base):
    __tablename__ = 'certDataDownLoadError'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    topic = Column('topic', String(50), default='')  # kafka主题
    data = Column('data', Text, default='')
    create_time = Column('create_time', DateTime(), default=datetime.now)  # 创建时间
