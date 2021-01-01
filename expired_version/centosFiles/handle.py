# -*- coding: utf-8 -*-
# filename: handle.py

import handleContent as myHandle
import hashlib
import reply
import receive
import web
import sys
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')

class Handle(object):
        def GET(self):
                try:
                        data = web.input()
                        if len(data) == 0:
                                return "hello, test_wx!"
                        signature = data.signature
                        timestamp = data.timestamp
                        nonce = data.nonce
                        echostr = data.echostr
                        token = "test_wx_token" #请按照公众平台官网\基本配置中信息填写

                        list = [token, timestamp, nonce]
                        list.sort()
                        sha1 = hashlib.sha1()
                        map(sha1.update, list)
                        hashcode = sha1.hexdigest()
                        print "handle/GET func: hashcode, signature: ", hashcode, signature
                        if hashcode == signature:
                                return echostr
                        else:
                                return ""
                except Exception, Argument:
                        return Argument
        def POST(self):
                try:
                        webData = web.data()
                        print "Handle Post webdata is ", webData
                        #后台打日志
                        recMsg = receive.parse_xml(webData)
                        if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                                toUser = recMsg.FromUserName
                                fromUser = recMsg.ToUserName

                                #content = "test"
                                content = recMsg.Content
                                content = myHandle.saveConfAndReply(toUser,content)
                                print("return : ",content)

                                replyMsg = reply.TextMsg(toUser, fromUser, content)
                                return replyMsg.send()
                        else:
                                print "暂且不处理"
                                return "success"
                except Exception, Argment:
                        print(Argment)
                        return Argment
