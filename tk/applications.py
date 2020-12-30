#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
role   : 管理端 Application
"""

from websdk.application import Application as myApplication
from tk.handlers.customquery_handler import customquery_urls
from tk.handlers.report_handler import report_urls
from tk.handlers.monitor_handler import monitor_urls
from tk.handlers.customized_handler import customized_urls
from tk.handlers.certdata_handler import certdata_urls
from tk.handlers.meter_handler import meter_urls


class Application(myApplication):
    def __init__(self, **settings):
        urls = []
        urls.extend(customquery_urls)
        urls.extend(report_urls)
        urls.extend(monitor_urls)
        urls.extend(customized_urls)
        urls.extend(certdata_urls)
        urls.extend(meter_urls)
        super(Application, self).__init__(urls, **settings)


if __name__ == '__main__':
    pass
