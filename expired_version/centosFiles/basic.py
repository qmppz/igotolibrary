# -*- coding: utf-8 -*-
# filename: basic.py

import urllib
import time
import json

class Basic:
        def __init__(self):
            """
            Initializes the accessor.

            Args:
                self: (todo): write your description
            """
                self.__accessToken = ''
                self.__leftTime = 0

        def __real_get_access_token(self):
            """
            Gets the access token.

            Args:
                self: (todo): write your description
            """
                appId = "xxxxxxxxxxxxx"
                appSecret = "xxxxxxxxxxxxxxxxxxxxx"
                postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="
                   "client_credential&appid=%s&secret=%s" % (appId, appSecret))
                urlResp = urllib.urlopen(postUrl)
                urlResp = json.loads(urlResp.read())
                self.__accessToken = urlResp['access_token']
                self.__leftTime = urlResp['expires_in']

        def get_access_token(self):
            """
            Get the access token.

            Args:
                self: (todo): write your description
            """
                if self.__leftTime < 10:
                        self.__real_get_access_token()
                return self.__accessToken

        def run(self):
            """
            Run the loop.

            Args:
                self: (todo): write your description
            """
                while(True):
                        if self.__leftTime > 10:
                                time.sleep(2)
                                self.__leftTime -= 2
                        else:
                                self.__real_get_access_token()
