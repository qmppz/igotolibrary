# -*- coding: UTF-8 -*-
'''
filename: reserve.py
run: python3 reserve.py [schoool_name] [pre_reserve_time]
user: wheee/qmppz
time: 20190707
description: reserve a seat again
'''

import requests
import json, time, random, re, sys, copy, traceback
from bs4 import BeautifulSoup
import execjs
import threading
import utils, crawldata
from aip import AipOcr

# ...

'''
others function...
'''

# reserve a seat
@utils.catch_exception
def reserve_a_seat(self, libid='', coordinate='', pre_or_today=pre):
   key_seat_page = pre_seatmap_page
   verify_key = verify_key
   url_prefix = url_prefix_pre
   seatmap_pageurl = seatmap_pageurl_pre
   seatmap_page_html = utils.get_response(
       url=seatmap_pageurl, sess=self.sess,
       m_headers=self.CF.M_HEADERS_PRE_RESERVE, m_cookies=self.CF.M_COOKIES, verify_key=verify_key)
   if not seatmap_page_html:
       return False
   soup = BeautifulSoup(seatmap_page_html, 'html.parser')
   hexch_js_code = requests.get([e for e in soup.find_all('script') if
          str(e).find(cache_layout_url) >= 0][0]['src'], verify=False)
   hexch_js_code.encoding='utf8'
   ajax_url = re.compile(r'(?<=[A-Z]\.ajax_get\().*?(?=,)').search(hexch_js_code.text).group(0).replace('AJAX_URL', url_prefix)
   hexch_js_code = re.sub(r'[A-Z]\.ajax_get', 'return %s ; T.ajax_get' % ajax_url, hexch_js_code.text)
   http_hexch_seatinfo = execjs.compile(hexch_js_code).call('reserve_seat', str(libid), coordinate)
   response = self.sess.get(http_hexch_seatinfo, proxies=utils.get_proxy(), headers=self.CF.M_HEADERS_PRE_RESERVE, cookies=self.CF.M_COOKIES, verify=False)
   # return 
   return verify_response(response.text)


'''
and so on ...
'''

