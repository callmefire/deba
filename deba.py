# -*- coding: utf-8 -*-
import web
import os

# Web browser Interface
class DeBa:
    def __init__(self):
        self.app_root       = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root,'template')
        self.render         = web.template.render(self.templates_root)

    def GET(self):
        browserReqHandler(self)

def browserReqHandler(self):
    return self.render.index("嘚吧")