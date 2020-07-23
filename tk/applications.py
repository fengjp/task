#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
role   : 管理端 Application
"""

from websdk.application import Application as myApplication
from tk.handlers.customquery_handler import customquery_urls

class Application(myApplication):
    def __init__(self, **settings):
        urls = []
        urls.extend(customquery_urls)
        super(Application, self).__init__(urls, **settings)


if __name__ == '__main__':
    pass
