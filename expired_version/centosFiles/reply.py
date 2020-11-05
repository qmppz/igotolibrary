# -*- coding: utf-8 -*-
# filename: reply.py

import time
class Msg(object):
        def __init__(self):
            """
            Initialize the object

            Args:
                self: (todo): write your description
            """
                pass
        def send(self):
            """
            Send the message.

            Args:
                self: (todo): write your description
            """
                return "success"
class TextMsg(Msg):
        def __init__(self, toUserName, fromUserName, content):
            """
            Initialize a user object from a dictionary.

            Args:
                self: (todo): write your description
                toUserName: (str): write your description
                fromUserName: (str): write your description
                content: (str): write your description
            """
                self.__dict = dict()
                self.__dict['ToUserName'] = toUserName
                self.__dict['FromUserName'] = fromUserName
                self.__dict['CreateTime'] = int(time.time())
                self.__dict['Content'] = content
        def send(self):
            """
            Send the xml format >

            Args:
                self: (todo): write your description
            """
                XmlForm = """
                <xml>
                <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
                <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
                <CreateTime>{CreateTime}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{Content}]]></Content>
                </xml>
                """
                return XmlForm.format(**self.__dict)
class ImageMsg(Msg):
        def __init__(self, toUserName, fromUserName, mediaId):
            """
            Initialize user object

            Args:
                self: (todo): write your description
                toUserName: (str): write your description
                fromUserName: (str): write your description
                mediaId: (str): write your description
            """
                self.__dict = dict()
                self.__dict['ToUserName'] = toUserName
                self.__dict['FromUserName'] = fromUserName
                self.__dict['CreateTime'] = int(time.time())
                self.__dict['MediaId'] = mediaId
        def send(self):
            """
            Send the xml format >

            Args:
                self: (todo): write your description
            """
                XmlForm = """
                <xml>
                <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
                <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
                <CreateTime>{CreateTime}</CreateTime>
                <MsgType><![CDATA[image]]></MsgType>
                <Image>
                <MediaId><![CDATA[{MediaId}]]></MediaId>
                </Image>
                </xml>
                """
                return XmlForm.format(**self.__dict)
