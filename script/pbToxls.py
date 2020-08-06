#!/usr/bin/env python
# -*-coding:utf-8-*-

import pandas as pd


def saveExce(columns, data, file_path):
    _z = zip(*data)
    obj = dict(zip(columns, _z))

    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    df = pd.DataFrame(obj)
    df.to_excel(writer, index=False, encoding='utf-8', sheet_name='Sheet')
    writer.save()


if __name__ == '__main__':
    file_path = 'test.xls'
    res = (('粤A', '广州', 904, 904, 0, 547, 56, 0),
           ('粤F', '韶关', 123, 123, 4, 324, 657, 0),
           ('粤B', '深圳', 677, 454, 0, 789, 567, 0),
           ('粤C', '珠海', 345, 644, 0, 789, 567, 0))
    columns = ['发证机关', '支队', '预警总数', '台账数', '预警数', '检查总数', '台账检查数', '处罚数']
    _z = zip(*res)
    obj = dict(zip(columns, _z))

    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    df = pd.DataFrame(obj)
    df.to_excel(writer, index=False, encoding='utf-8', sheet_name='Sheet')
    writer.save()
