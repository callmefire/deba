# -*- coding: utf-8 -*-

import sys
import web

from weixin import WeiXin
from weixin import CreateMenu
from deba   import DeBa
from japan  import Japan
from subway import Subway

urls = (
     '/','DeBa',
     '/weixin','WeiXin',
     '/creatmenu','CreateMenu',
     '/japan', 'Japan',
     '/subway', 'Subway',
#    '/travel','Travel',
#    '/delicacy',"Delicacy",
#    '/essay','Essay',
#    '/all','All'
)
try:
     reload(sys)
     sys.setdefaultencoding('utf8')
except:
     pass

web.config.debug = True

application = web.application(urls,globals()).wsgifunc()


