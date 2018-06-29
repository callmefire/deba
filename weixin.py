# -*- coding: utf-8 -*-

import web
import os
import time
import hashlib
import json
try:
    import urllib2
except:
    pass
import urllib
import xml.etree.ElementTree as etree

# Get access token from WinXin server

def getWinXinToken():
    appid      = 'wxd2e10b923ddc4b72'
    secret     = '4a92ddfeed71dc3e92f5dcf6137a2211'
    url        = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + secret
    result     = urllib2.urlopen(url)
    token_json = json.loads(result.read())
    return token_json['access_token']

# Dynamic menu management

def createMenu():
    access_token = getWinXinToken()

    menu = '''
    {
        "button":[
        {
            "type":"click",
            "name":"关于",
            "key" :"关于"
        },
        {
            "name":"话题",
            "sub_button": [
            {
                "type":"view",
                "name":"日本",
                "url" :"http://deba.applinzi.com/japan"
            },
            {
                "type":"click",
                "name":"旅行",
                "key" :"旅行"
            },
            {
                "type":"click",
                "name":"美食",
                "key" :"美食"
            },
            {
                "type":"click",
                "name":"杂谈",
                "key" :"杂谈"
            },
            {
                "type":"click",
                "name":"所有文章",
                "key" :"所有文章"
            }]
        },
        {
            "name":"工具",
            "sub_button": [
            {
                "type":"click",
                "name":"搜索",
                "key" :"搜索"
            },
            {
                "type":"view",
                "name":"地铁路线查询",
                "url" :"http://deba.applinzi.com/subway"
            },
            {
                "type":"click",
                "name":"录音",
                "key" :"录音"
            },
            {
                "type":"click",
                "name":"导航",
                "key" :"导航"
            }]
        }]
    } '''

    url4menu = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + access_token
    req      = urllib2.Request(url4menu, menu)
    return urllib2.urlopen(req)

class CreateMenu:
    def GET(self):
        return createMenu()

# Material management

def getMaterialCount():
    url4mcount = 'https://api.weixin.qq.com/cgi-bin/material/get_materialcount?access_token=' + getWinXinToken()

    req = urllib2.Request(url4mcount)
    response = urllib2.urlopen(req)
    return response

def getMaterialEntries():
    url4articlelist = 'https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token=' + getWinXinToken()

    msg = '''
    {
        "type"   : "image",
        "offset" : "0",
        "count"  : "20"
    } '''

    req = urllib2.Request(url4articlelist,msg)
    response = urllib2.urlopen(req)
    return response

def uploadIMG():
    url4uploadimg = 'https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=' + getWinXinToken()

    msg = '''
    {
        "type" : "image",
        "media" : "/Users/dchang/Documents/callmefire/gnu2.png"
    } '''
    req = urllib2.Request(url4uploadimg,msg)
    response = urllib2.urlopen(req)
    return response

# Entry function for access from web browser

def browserDebugHandler(self):
    return uploadIMG()

# Entry class for communication with WeiXin client user

class WeiXin:
    def __init__(self):
        self.app_root       = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root,'template')
        self.render         = web.template.render(self.templates_root)

    def GET(self):
        data = web.input()

        if data == {}:
            return browserDebugHandler(self)

        # Only for server verification
        signature = data.signature
        timestamp = data.timestamp
        nonce     = data.nonce
        echostr   = data.echostr

        token = "callmefire"
        list  = [token,timestamp,nonce]
        list.sort()

        sha1 = hashlib.sha1()
        map(sha1.update,list)
        hashcode = sha1.hexdigest()

        if hashcode == signature:
            return echostr

    def POST(self):
        xml      = etree.fromstring(web.data())
        mstype   = xml.find("MsgType").text
        fromUser = xml.find("FromUserName").text
        toUser   = xml.find("ToUserName").text

        if mstype == "event":
            event = xml.find("Event").text
            if event == "subscribe":
                replyText = u'欢迎光临'
                return self.render.event_reply(fromUser,toUser,111111,replyText)
            elif event == "CLICK":
                menu_key = xml.find("EventKey").text
                replyText = u'您访问了 ' + menu_key
                return self.render.event_reply(fromUser,toUser,111111,replyText)

            elif event == "VIEW":
                menu_url = xml.find("EventKey").text
                replyText = u'您打开了 ' + menu_url
                return self.render.event_reply(fromUser,toUser,111111,replyText)


