# -*- coding: utf-8 -*-
# filename: receive.py

import xml.etree.ElementTree as ET

def parse_xml(web_data):
    """
    Parse an xml document from an xml.

    Args:
        web_data: (todo): write your description
    """
        if len(web_data) == 0:
                return None
        xmlData = ET.fromstring(web_data)
        msg_type = xmlData.find('MsgType').text
        if msg_type == 'text':
                return TextMsg(xmlData)
        elif msg_type == 'image':
                return ImageMsg(xmlData)

class Msg(object):
        def __init__(self, xmlData):
            """
            Parses xml data.

            Args:
                self: (todo): write your description
                xmlData: (todo): write your description
            """
                self.ToUserName = xmlData.find('ToUserName').text
                self.FromUserName = xmlData.find('FromUserName').text
                self.CreateTime = xmlData.find('CreateTime').text
                self.MsgType = xmlData.find('MsgType').text
                self.MsgId = xmlData.find('MsgId').text

class TextMsg(Msg):
        def __init__(self, xmlData):
            """
            Reset xml content.

            Args:
                self: (todo): write your description
                xmlData: (todo): write your description
            """
                Msg.__init__(self, xmlData)
                self.Content = xmlData.find('Content').text.encode("utf-8")

class ImageMsg(Msg):
        def __init__(self, xmlData):
            """
            Parses xml data from xml.

            Args:
                self: (todo): write your description
                xmlData: (todo): write your description
            """
                Msg.__init__(self, xmlData)
                self.PicUrl = xmlData.find('PicUrl').text
                self.MediaId = xmlData.find('MediaId').text
