#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
role   : 启动程序
"""

import fire
from tornado.options import define
from websdk.program import MainProgram
from settings import settings as app_settings
from tk.applications import Application as MgApp

define("service", default='api', help="start service flag", type=str)


class MyProgram(MainProgram):
    def __init__(self, service='tk', progressid=''):
        self.__app = None
        settings = app_settings
        if service == 'tk':
            self.__app = MgApp(**settings)

        super(MyProgram, self).__init__(progressid)
        self.__app.start_server()


if __name__ == '__main__':
    fire.Fire(MyProgram)
