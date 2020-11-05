# -*- coding: UTF-8 -*-
'''
filename: utils.py
run: --
user: wheee/qmppz
time: 20190709
description: utils
'''

import json, time, random, re
import configparser
from pymemcache.client.base import Client
import sqlite3
import requests
import traceback
import platform
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LOCAL = False
if 'Darwin' == platform.system():
    # maxos == Darwin
    # centos == Linux
    LOCAL = True


'''
decorators catch_exception
'''
def catch_exception(func):
    """
    Decorator to catch exceptions exceptions.

    Args:
        func: (callable): write your description
    """
    def wrapper(*args, **kwargs):
        """
        Decorator for the function

        Args:
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            debug_p('[ERROR-BREAK]:func_name='+str(func.__name__)+'\n'+traceback.format_exc()+'\n')
            return '\n[E]: 一个致命异常发生了...请联系管理员研究一下这是什么情况。\n添加指令必须在自身没有预约座位的状态下才能成功\n管理员vx: turing_01110101'
    return wrapper

'''
get today date
'''
def get_date(offset=0,format='%Y%m%d_%H%M%S'):
    """
    Returns a string representation of the current date.

    Args:
        offset: (int): write your description
        format: (str): write your description
    """
    t = str(time.strftime(format, time.localtime()))
    return t

'''
get ipproxy
'''
@catch_exception
def get_proxy(type='', count=5, protocol=1, country=''):
    """
    Get a proxy

    Args:
        type: (todo): write your description
        count: (str): write your description
        protocol: (str): write your description
        country: (str): write your description
    """

    return {}
    # http://127.0.0.1:8000/?protocol=1&count=10&country=%E5%9B%BD%E5%86%85 #国内
    r = requests.get('http://127.0.0.1:8000/?protocol='+str(protocol)+'&count='+str(count))
    ipproxy_ls = json.loads(r.text)
    if not ipproxy_ls:
        return {}
    # ["218.60.8.99", 3129, 10]
    ip, port, score = ipproxy_ls[random.randint(0, len(ipproxy_ls)-1)]
    proxy = {
        "https": "https://"+ip+':'+str(port)
    }
    return proxy

'''
global config for all file read
init/refresh by igtl.conf
timing refresh value
one instance
only modified by GBCF itself
'''
class GBCF(object):
    '''
    global value
    '''

    # char limit
    CHAR_LIMIT = 500

    # version
    VERSION_INFO = '1.5.0'

    EXTRA_CMD = {'exe_time': 'exetime',
                 'pattern': '',
                 'platform': '我去图书馆'}

    # extra split flag
    EXTRA_FLAG = '--'

    # serverid
    SERVERID = ('b9fc7bd86d2eed91b23d7347e0ee995e', 'd3936289adfff6c3874a2579058ac651')[random.randint(0, 1)] \
                            + '|' + str(int(time.time() - 1)) + '|1570361133'

    USER_CMD_SPLTCH = ';'

    CHECK_SCHOOL_TIME = PREPARE_TIME = 60 * 2 * 1000

    HOST = {'IGTL': 'wechat.v2.traceint.com',
            'CTRS': 'wechat.laixuanzuo.com'}

    # REG_hexcode_url = "https://static\.wechat\.v2\.traceint\.com/template/theme2/cache/layout/.+"

    # user - agent
    USER_AGENT = [
        'Mozilla/5.0 (Linux; Android 8.1; PAR-AL00 Build/HUAWEIPAR-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044304 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x26070333) NetType/WIFI Language/zh_CN Process/tools',
        'Mozilla/5.0 (Linux; Android 8.1; EML-AL00 Build/HUAWEIEML-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.143 Crosswalk/24.53.595.0 XWEB/358 MMWEBSDK/23 Mobile Safari/537.36 MicroMessenger/6.7.2.1340(0x2607023A) NetType/4G Language/zh_CN',
        'Mozilla/5.0 (Linux; Android 8.0; DUK-AL20 Build/HUAWEIDUK-AL20; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044353 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x26070333) NetType/WIFI Language/zh_CN Process/tools',
        'Mozilla/5.0 (Linux; Android 5.1.1; vivo X6S A Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044207 Mobile Safari/537.36 MicroMessenger/6.7.3.1340(0x26070332) NetType/4G Language/zh_CN Process/tools',
        ''
    ]

    PATH = {
        'P_': './',
        'P_LOG': './log/',
        'P_CLASSROOM': './classroom/',

        'F_IGTL_CONF': './data/igtl.conf',
        'F_ORGN_CMD_LOG': 'origin_command.log',
        'F_MAIN_LOOP_TASK_LOG': 'main_loop_task.log',
        'F_CLSSRM_TASK_CONF': 'clssrm_id_and_today_task.conf'
    }

    # task_id
    TASK_ID = int(get_date().split('_')[0]) - 20180000 + (100 if int(get_date().split('_')[0]) % 2 == 0 else -100) + 1110

    # reserve thread
    RS = {
        'SUCCESS':  ' ',
    }

    # task
    # task_kind
    TASK_KIND = {
        'reserve': 'reserve',
        'realtime': 'realtime'
    }

    # platform
    PLATFORM = {
        'IGTL': 'IGTL',
        'CTRS': 'CTRS'
    }

    # pattern
    PATTERN = {
        'PRE': 'PRE',
        'TODAY': 'TODAY'
    }

    # # memcache
    # MC = {
    #     # reserve  prefix
    #     TASK_KIND['reserve']: 'reserve_',
    #     TASK_KIND['realtime']: 'realtime_',
    #     # user task stats
    #     'task_stats': 'task_stats',
    #     # all task success rate
    #     'rate': 'rate_',
    # }

    # exe trace format
    TRACE_FORMAT = {
        'head': '状态:{status}\n[{school_name}-{schl_abbr}_{task_id}]\n{submit_time} 提交\n',
        'exe_trace': '{emoji}{try_cnt}. {exe_time} [{classroom_name}]-[{seat_num}]号座位:{feedback}\n',
    }


    # task_result
    TASK_RESULT = {
        'school_name': '',#'蚌埠医学院',
        'schl_abbr': '', #''bbmc',
        'task_id': '', #'12311',
        'submit_time': '',#'2019.10.06_09:00:12',
        'exe_trace': []#[EXE_TRACE],
    }

class Atask(object):
    '''
    init,
    platform = {'IGTL', 'CTRS'}
    pattern = {'PRE', 'TODAY'}
    '''
    def __init__(self, platform=GBCF.PLATFORM['IGTL'], pattern=GBCF.PATTERN['PRE']):
        """
        Initialize the connection

        Args:
            self: (todo): write your description
            platform: (todo): write your description
            GBCF: (todo): write your description
            PLATFORM: (todo): write your description
            pattern: (str): write your description
            GBCF: (todo): write your description
            PATTERN: (str): write your description
        """

        self.USER_CMD_SPLTCH = GBCF.USER_CMD_SPLTCH
        # self.PREPARE_TIME = 300 * 1000
        # self.CHECK_SCHOOL_TIME = self.PREPARE_TIME

        # transfer platform from {'1', '2'}  to   {'IGTL', 'CTRS'}
        self.platform = platform # ['IGTL', 'CTRS'][int(platform)-1] if len(str(platform)) == 1 else platform
        self.pattern = pattern # ['PRE', 'TODAY'][int(pattern)-1] if len(str(pattern)) == 1 else pattern

        self.mhost = GBCF.HOST[self.platform]

        self.task_result = GBCF.TASK_RESULT

        self.BASE_URL = {
            'test': 'http://www.baidu.com',
            'host': 'http://' + self.mhost,  # 'wechat.v2.traceint.com',
            'home_page': 'https://' + self.mhost + '/index.php/reserve/index.html?f=wechat',
            'usage_rules': 'https://' + self.mhost + '/index.php/center/rule.html',
            # https://wechat.v2.traceint.com/index.php/prereserve/save/libid=323&sTKmM3nQBnQEx=28,23&yzm=
            'pre_reserve': 'https://' + self.mhost + '/index.php/prereserve/save/libid={libid}&{hexch}={coordinate}&yzm=',
            'pre_reserve_prefix': '\"https://' + self.mhost + '/index.php/prereserve/save/\"',
            # https://wechat.v2.traceint.com/index.php/reserve/layoutApi/action=prereserve_event&libid=323
            'pre_seatmap_page': 'https://' + self.mhost + '/index.php/reserve/layoutApi/action=prereserve_event&libid={libid}',

            # https://wechat.v2.traceint.com/index.php/reserve/get/libid=323&KzZJcpGyJe=25,41&yzm=    200    GET    wechat.v2.traceint.com    /index.php/reserve/get/libid=323&KzZJcpGyJe=25,41&yzm=    61    Sat Jul 13 14:27:54 CST 2019    495    Complete
            # 'today_reserve': 'https://wechat.v2.traceint.com/index.php/reserve/get/libid={libid}&{hexch}e={coordinate}&yzm=',
            # https://wechat.v2.traceint.com/index.php/reserve/get/libid=323&Rd7mhiBe=29,26&yzm=1832	200	GET	wechat.v2.traceint.com	/index.php/reserve/get/libid=323&Rd7mhiBe=29,26&yzm=1832	62	Sun Jul 21 08:50:38 CST 2019	462	Complete
            'today_reserve': 'https://' + self.mhost + '/index.php/reserve/get/libid={libid}&{hexch}={coordinate}&yzm=',
            'today_reserve_prefix': '\"https://' + self.mhost + '/index.php/reserve/get/\"',
            # https://wechat.v2.traceint.com/index.php/reserve/layout/libid=323.html&1562572495    200    GET    wechat.v2.traceint.com    /index.php/reserve/layout/libid=323.html&1562572495    57    Sat Jul 13 14:27:47 CST 2019    6418    Complete
            'today_seatmap_page': 'https://' + self.mhost + '/index.php/reserve/layout/libid={libid}.html&{now_time}',
            'verifycode_page': 'https://' + self.mhost + '/index.php/misc/verify.html',

            'rules': 'https://' + self.mhost + '/index.php/center/rule.html',

        }

        self.REG_HEXCODE_URL = {
            'IGTL': "https://static\.wechat\.v2\.traceint\.com/template/theme2/cache/layout/.+?",
            'CTRS': "https://static\.wechat\.laixuanzuo\.com/template/theme2/cache/layout/.+?"
        }[self.platform]

        # verify key of seat_map page
        self.VERIFYKEY_OF_SEATMAP = {'PRE': '预定明天座位', 'TODAY': '座位选择'}[self.pattern]
        #verify key of homepage page
        self.VERIFYKEY_OF_HOMEPAGE = '您好'

        # config
        self.CURRENT_URL = {
            'host': self.BASE_URL['host'],
            'home_page': self.BASE_URL['home_page'],
            'usage_rules': self.BASE_URL['usage_rules'],
            'reserve_prefix': self.BASE_URL['pre_reserve_prefix' if self.pattern == 'PRE' else 'today_reserve_prefix'],
            'seatmap_page': self.BASE_URL['pre_seatmap_page' if self.pattern == 'PRE' else 'today_seatmap_page'],
            'verifycode_page': self.BASE_URL['verifycode_page'],
        }

        # self.M_HEADERS = {
        #     'upgrade-insecure-requests': '1',
        #     'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        #     # 'user-agent': random.choice(GBCF.USER_AGENT), #'Mozilla/5.0 (Linux; Android 8.0.0; MI 5 Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044705 Mobile Safari/537.36 MMWEBID/5292 MicroMessenger/7.0.3.1400(0x27000334) Process/tools NetType/WIFI Language/zh_CN',
        #     'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; MI 5 Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044705 Mobile Safari/537.36 MMWEBID/5292 MicroMessenger/7.0.3.1400(0x27000334) Process/tools NetType/WIFI Language/zh_CN',
        #     # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,image/wxpic,image/sharpp,image/apng,image/tpg,*/*;q=0.8',
        #     'accept': 'application/json, text/javascript, */*; q=0.01',
        #     'accept-encoding': 'gzip, deflate, br',
        #     'accept-language': 'zh-CN,en-US;q=0.9'
        # }

        # self.M_HEADERS_PRE_RESERVE = {
        #     'accept': 'application/json, text/javascript, */*; q=0.01',
        #     'x-requested-with': 'XMLHttpRequest',
        #     # 'user-agent': random.choice(GBCF.USER_AGENT),#'Mozilla/5.0 (Linux; Android 8.0.0; MI 5 Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044705 Mobile Safari/537.36 MMWEBID/5292 MicroMessenger/7.0.3.1400(0x27000334) Process/tools NetType/WIFI Language/zh_CN',
        #     'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; MI 5 Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044705 Mobile Safari/537.36 MMWEBID/5292 MicroMessenger/7.0.3.1400(0x27000334) Process/tools NetType/WIFI Language/zh_CN',
        #     # referer    https://' + mhost + '/index.php/reserve/layoutApi/action=prereserve_event&libid=323
        #     'accept-encoding': 'gzip, deflate, br',
        #     'accept-language': 'zh-CN,en-US;q=0.9',
        # }

        if self.platform == 'IGTL':
            self.M_COOKIES = {
                'FROM_TYPE': 'weixin',
                'SERVERID': ('b9fc7bd86d2eed91b23d7347e0ee995e', 'd3936289adfff6c3874a2579058ac651')[random.randint(0, 1)] \
                                + '|' + str(int(time.time() - 1)) + '|1570204089',
                'Hm_lvt_7ecd21a13263a714793f376c18038a87': '1570204075',
                'wechatSESS_ID': 'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww',
                'Hm_lpvt_7ecd21a13263a714793f376c18038a87': str(int(time.time() - 1))
            }
            self.M_HEADERS = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            # 'x-requested-with': 'XMLHttpRequest',
            'user-agent': random.choice(GBCF.USER_AGENT),#'Mozilla/5.0 (Linux; Android 8.0.0; MI 5 Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044705 Mobile Safari/537.36 MMWEBID/5292 MicroMessenger/7.0.3.1400(0x27000334) Process/tools NetType/WIFI Language/zh_CN',
            # 'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; MI 5 Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044705 Mobile Safari/537.36 MMWEBID/5292 MicroMessenger/7.0.3.1400(0x27000334) Process/tools NetType/WIFI Language/zh_CN',
            # referer    https://' + mhost + '/index.php/reserve/layoutApi/action=prereserve_event&libid=323
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,en-US;q=0.9',
        }
        else:
            # CTRS
            self.M_COOKIES = {
                'wechatSESS_ID': 'llllllllllllllllllllllllllllllllll',
                'FROM_TYPE': 'weixin',
                'Hm_lvt_7838cef374eb966ae9ff502c68d6f098': '1570279152',
                'Hm_lpvt_7838cef374eb966ae9ff502c68d6f098': '1570279491',
                # try add serverid
                # 'SERVERID': 'b9fc7bd86d2eed91b23d7347e0ee995e|' + str(int(time.time() - 1)) + '|1562944815',
            }
            self.M_HEADERS = {
                'Host': 'wechat.laixuanzuo.com',
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                # 'X-Requested-With': 'XMLHttpRequest',
                'user-Agent': random.choice(GBCF.USER_AGENT),#'Mozilla/5.0 (Linux; Android 8.0.0; MI 5 Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044705 Mobile Safari/537.36 MMWEBID/5292 MicroMessenger/7.0.3.1400(0x27000334) Process/tools NetType/WIFI Language/zh_CN',
                # 'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; MI 5 Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044904 Mobile Safari/537.36 MMWEBID/5292 MicroMessenger/7.0.3.1400(0x27000334) Process/tools NetType/WIFI Language/zh_CN',
                'Referer': 'https://wechat.laixuanzuo.com/index.php/reserve/layout/libid=10037.html&1570279514',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,en-US;q=0.9',
            }


        self.RESPONSE_FLAG = {
            'COOKIES_EXPIRED': '\u767b\u9646\u8fc7\u671f,\u8bf7\u91cd\u65b0\u5237\u65b0\u9875\u9762',# code : 4
            'HAS_RESERVED':'\u4f60\u5df2\u7ecf\u9884\u5b9a\u4e86\u660e\u5929\u7684', # code : 2
            # 该座位已经被人预定了!  code 1
            'SEAT_HAS_BEEN_RESERVE': '\u8be5\u5ea7\u4f4d\u5df2\u7ecf\u88ab\u4eba\u9884\u5b9a\u4e86!', # code 1
            'NEED_VERIFY_CODE': '\u8bf7\u8f93\u5165\u9a8c\u8bc1\u7801', #请输入验证码
            'RESERVE_SUCC': '\u9884\u5b9a\u5ea7\u4f4d\u6210\u529f', # code : 0


        }
    # # refresh value
    # @catch_exception
    # def refresh(self):
    #     # read igtl.conf refresh config value
    #     PATH = '/root/igotolibrary/'
    #     if LOCAL:
    #         PATH = './'
    #
    #     igtl_conf_file = PATH+'igtl.conf'
    #     igtl_dict = read_conf(igtl_conf_file, section='', key_name='')
    #     igtl_section = igtl_dict['igotolibrary']
    #     self.USER_CMD_SPLTCH = igtl_section['USER_CMD_SPLTCH'.lower()].strip()
    #
    #     global_cookies_section = igtl_dict['global_cookies']
    #     keys = ['FROM_TYPE', 'Hm_lvt_7ecd21a13263a714793f376c18038a87', 'wechatSESS_ID', 'SERVERID', 'Hm_lpvt_7ecd21a13263a714793f376c18038a87']
    #     for key in keys:
    #         self.M_COOKIES[key] = global_cookies_section.get(key.lower(), self.M_COOKIES[key]).strip()

        # grab_seat_time_section = igtl_dict['grab_seat_time']
        # self.GRAB_TIME_LS = grab_seat_time_section

'''
fill serverid , wechat_sess_id and others 
and fill now timestamp
then return cookies
'''
def fill_cookies(cookies={}, serverid='', wechat_sess_id='', hm_lvt_time='', platform='IGTL'):
    '''
    hm_lpvt_time=nowtime
    serverid_time1=nowtime
    '''
    Hm_lvt_key = {
        'IGTL': 'Hm_lvt_7ecd21a13263a714793f376c18038a87',
        'CTRS': 'Hm_lvt_7838cef374eb966ae9ff502c68d6f098'
    }
    Hm_lpvt_key = {
        'IGTL': 'Hm_lpvt_7ecd21a13263a714793f376c18038a87',
        'CTRS': 'Hm_lpvt_7838cef374eb966ae9ff502c68d6f098'
    }

    now_timestamp = int(time.time())

    if platform == GBCF.PLATFORM['IGTL']:
        if serverid:
            serverid = serverid.split('=')[-1]
            cookies['SERVERID'] = serverid.strip()
        cookies['SERVERID'] = cookies.get('SERVERID', GBCF.SERVERID)
        tmp_ls = cookies.get('SERVERID', GBCF.SERVERID).split('|')
        # debug_p('tmp_ls=',tmp_ls)
        cookies['SERVERID'] = tmp_ls[0] + '|' + str(now_timestamp - 2) + '|' + tmp_ls[2]
        pass
    if wechat_sess_id:
        wechat_sess_id = wechat_sess_id.split('=')[-1]
        cookies['wechatSESS_ID'] = wechat_sess_id.strip()
    if hm_lvt_time:
        cookies[Hm_lvt_key[platform]] = str(hm_lvt_time)
    # if serverid_t2:
    #     tmp_ls = cookies['SERVERID'].split('|')
    #     cookies['SERVERID'] = tmp_ls[0]+'|'+str(tmp_ls[1])+'|'+str(serverid_t2)

    # fill now timestamp
    cookies[Hm_lpvt_key[platform]] = str(now_timestamp - 1)

    # debug_p('cookies=', cookies)
    return cookies

'''
debug_p
'''
DEBUG_MODEL = 1
def debug_p(*args):
    """
    Print debug information.

    Args:
    """
    # date2ts
    # int(time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S")))
    now_ts = time.time() # '1564905302.6147149'
    millisecond = str(str(now_ts).split('.')[-1])[:3]
    t = str(time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime(now_ts))) + '.'+millisecond
    args = ' '.join([str(e) for e in args])
    if DEBUG_MODEL:
        print('----#' + t + '|' + args)

'''
operate file save or write
return read the file content or operate status
'''
def operate_file(file_path='./text.txt', op_model='r', write_str='\n'):
    """
    .. version 1. operand

    Args:
        file_path: (str): write your description
        op_model: (str): write your description
        write_str: (str): write your description
    """
    if op_model == 'a' or op_model == 'w':
        with open(file_path, op_model, encoding='utf-8') as f:
            status = f.write(write_str)
            return status
    # elif op_model == 'r':
    #     with open(file_path, op_model, encoding='utf-8') as f:
    #         pass

'''
parse extra cmd
'''
def parse_extra_cmd(extra_cmd='', splt_ch=GBCF.USER_CMD_SPLTCH, extra_flag=GBCF.EXTRA_FLAG):
    """
    Parse the extra arguments.

    Args:
        extra_cmd: (str): write your description
        splt_ch: (todo): write your description
        GBCF: (todo): write your description
        USER_CMD_SPLTCH: (str): write your description
        extra_flag: (todo): write your description
        GBCF: (todo): write your description
        EXTRA_FLAG: (todo): write your description
    """
    cmd_dict = {}
    # extra_cmd
    if extra_cmd:
        # --
        extra_cmd = extra_cmd.split(extra_flag)[-1]
        key_dct = {
            'exe_time': {'开抢时间', '时间', 't', 'time', 'exe_time', '执行时间', '抢座时间'},
            'pattern': {'预约模式', '今明', '哪天', '抢座模式', '模式', 'ms', 'moshi', 'yyms', 'qzms', 'pattern'},
            'platform': {'平台', 'platform', '公众号', 'pingtai', 'gongzhonghao', 'pt', 'gzh'}
        }
        value_dct = {
            'exe_time': {},
            'pattern': {'PRE': {'pre', '明', '明天', '明日', 'm', 'mr', 'mt', 'ming', 'mingtian', 'tomorrow', '明日预约'},
                                'TODAY': {'today', '今', '今天', '今日', 'j', 'jr', 'jin', 'jt', 'jintian', '当日', '当日即时预订'}},
            'platform': {'IGTL': {'我去图书馆', 'igtl', 'wqtsg'}, 'CTRS': {'来选座', 'lxz', 'ctrs'}}
        }
        extra_kv_split = '='

        # transfer to lower and replace  [;=;] to [=]  ;   [==] to [=]  ;  [：] to [:]
        extra_cmd = extra_cmd.lower().\
                replace(splt_ch+extra_kv_split+splt_ch, extra_kv_split).\
                replace(extra_kv_split+extra_kv_split, extra_kv_split).\
                replace(u'：', ':')

        for key_value in extra_cmd.split(splt_ch):
            # print('### test', key_value)
            key_value = key_value.strip()
            if not key_value or len(key_value.split(extra_kv_split)) != 2:
                continue
            # debug_p('### test', '+'*10, key_value)
            # 平台=我去图书馆     模式=今
            key, value = key_value.split(extra_kv_split)
            key = get_key_by_value(key, key_dct)
            value = get_key_by_value(value, value_dct.get(key, {}))

            # print('### test', key, value)
            # push into cmd_dict
            cmd_dict[key] = str(value)

        # exe_time
        if 'exe_time' in cmd_dict:
            hh, mm, ss = (cmd_dict['exe_time']+':00:00').split(':')[:3]
            exe_time = ''
            for item in [hh, mm, ss]:
                exe_time += str('0' + item) if len(item) == 1 else item
                exe_time += ':'
            cmd_dict['exe_time'] = exe_time[:-1]
    return cmd_dict

'''
parse command from wechat backstage
'''
def parse_grab_seat_cmd(command='', splt_ch=GBCF.USER_CMD_SPLTCH, extra_flag=GBCF.EXTRA_FLAG):
    """
    Parse command line

    Args:
        command: (str): write your description
        splt_ch: (str): write your description
        GBCF: (todo): write your description
        USER_CMD_SPLTCH: (todo): write your description
        extra_flag: (todo): write your description
        GBCF: (todo): write your description
        EXTRA_FLAG: (todo): write your description
    """
    user_cmd_len = 7# 8
    '''
    type=user
        
    实时预定 | 捡漏 | jl | #jl | 明日预约 | 抢座 | #qz | qz    ；   
    学校英文简称 | 首拼；
    自习室id1；座位号1；自习室id2，座位号2；
    serverid(可选)；wechat_sess_id
    extra_info:
    exetime  首次执行时间 | 开抢时间;
    pre_today 当日即时预订 | 明日预约;
    lgtl_or_ctrs 我去图书馆  |  来选座;
    unknown_cmd 扩展指令
        
    type=log
        #抢座; taskid; SERVERID; wechat_sess_id; BBMC; 323:21,31;324:56,76; uid; seat_comment; 时间;
        taskid|serverid|wechat_sess_id|libid1_coordinate|libid2_coordinate|comment_info

    type=pre_reserve
        task_id;
        cookies_param;
        school_name and clssrm_id and seat coordinate;
        others_info

        taskid; userid; user_name; school_name; classroom_name1;323;seat_num; 21,31; classroom_name2; 324; seat_num2; 41,51; serverid; wechat_sess_id; comment_info
    '''

    # ensure ensure wechatSESS_ID and SERVERID
    if command.find('wechatSESS_ID=') < 0: #or command.find('SERVERID=') < 0:
        return ''

    # split command and extra_cmd;  extra_flag is --
    command, extra_cmd = (command+'\n'+extra_flag).split(extra_flag)[:2]
    # parse_extra_cmd
    cmd_dict = parse_extra_cmd(extra_cmd=extra_cmd, splt_ch=splt_ch, extra_flag=extra_flag)

    # normal command
    # debug_p('### test', cmd_dict)


    if command[-1] == splt_ch:
        command = command[:-1]
    cmd_splt = command.split(splt_ch)
    # check serverid
    cmd_splt = [_ for _ in cmd_splt if _ and str(_).find('SERVERID') < 0][:user_cmd_len]

    # print('### test1', cmd_dict)

    if len(cmd_splt) == user_cmd_len - 2:
        cmd_splt = cmd_splt[:4] + [cmd_splt[2], cmd_splt[3]] + cmd_splt[4:]
        # print('### test1.5', cmd_splt)

    if len(cmd_splt) == user_cmd_len:
        # _, cmd_dict['schl_abbr'], cmd_dict['libid1'], cmd_dict['seat_num1'], \
        #     cmd_dict['libid2'], cmd_dict['seat_num2'],\
        #     cmd_dict['wechat_sess_id'], cmd_dict['serverid'] = [str(e).strip() for e in cmd_splt if e]

        _, cmd_dict['schl_abbr'], cmd_dict['libid1'], cmd_dict['seat_num1'], \
        cmd_dict['libid2'], cmd_dict['seat_num2'], \
        cmd_dict['wechat_sess_id'],                = [str(e).strip() for e in cmd_splt if e]

        # schl_abbr transfer to  lower
        cmd_dict['schl_abbr'] = cmd_dict['schl_abbr'].lower()
        # if libid <=0 then seat_num and coordinate must equal 0

        # print('### test2', cmd_dict)

        # seatnum prefix 0
        cmd_dict['seat_num1'] = str(int(cmd_dict['seat_num1'])) if int(cmd_dict['libid1']) > 0 else '0'
        cmd_dict['seat_num2'] = str(int(cmd_dict['seat_num2'])) if int(cmd_dict['libid2']) > 0 else '0'
        # {schl_abbr: '', libid1: '', seat_num1: '', libid2: '', seat_num2: '',serverid:'', wechat_sess_id:''}

        debug_p('cmd_dict=', cmd_dict)
        return cmd_dict
    return ''

'''
get_key_by_value
'''
def get_key_by_value(value, key_dct):
    """
    Return the value of a key from a dict.

    Args:
        value: (todo): write your description
        key_dct: (str): write your description
    """
    # exe_time`s value is 06:00 or 23:59 and so on ...;  exe_time key_dct is empty
    # debug_p('### test',  value,  key_dct)
    if not key_dct:
        return value
    for k in key_dct.keys():
        if value in key_dct[k]:
            return k
    return ''

'''
get response 
'''
def get_response(url, sess, m_headers={}, m_cookies={}, verify_key='', platform='IGTL') -> str:
    """
    Get a response. : parameter.

    Args:
        url: (str): write your description
        sess: (todo): write your description
        m_headers: (dict): write your description
        m_cookies: (dict): write your description
        verify_key: (str): write your description
        platform: (str): write your description
    """
    Hm_lvt_key = {
        'IGTL': 'Hm_lvt_7ecd21a13263a714793f376c18038a87',
        'CTRS': 'Hm_lvt_7838cef374eb966ae9ff502c68d6f098'
    }
    Hm_lpvt_key = {
        'IGTL': 'Hm_lpvt_7ecd21a13263a714793f376c18038a87',
        'CTRS': 'Hm_lpvt_7838cef374eb966ae9ff502c68d6f098'
    }
    func_name = '[utils.get_response]'
    response = 'response_default'
    try:
        time_stamp = int(time.time())
        # m_cookies['Hm_lvt_7ecd21a13263a714793f376c18038a87'] = str(time_stamp)
        if platform == GBCF.PLATFORM['IGTL']:
            tmp = m_cookies.get('SERVERID', GBCF.SERVERID).split('|')
            m_cookies['SERVERID'] = tmp[0] + '|' + str(time_stamp-1) + '|' + tmp[2]
        m_cookies[Hm_lpvt_key[platform]] = str(time_stamp-1)
        # debug_p('get_response()  ', 'm_cookies=', m_cookies, 'm_headers=', m_headers)
        # print(m_cookies)

        # debug_p(func_name, 'url=', url, 'm_cookies=', m_cookies, 'mheaders=', m_headers)

        response = sess.get(url=url,
                         timeout=3,
                         headers=m_headers,
                         cookies=m_cookies,
                         #proxies=get_proxy(),
                         verify=False)
        response.encoding = 'utf8'
        # verify success or failed
        if response and response.status_code == 200 and (response.text.find(verify_key) >= 0 if verify_key else True):
            return response.text
        debug_p(func_name, '[E]: response verify failed, status_code=', response.status_code,
                'verify_key=', verify_key, 'response_text=', response.text)
    except Exception as e:
        debug_p(func_name, '[E]: action [get response] failed, status_code=', response.status_code,
                'verify_key=', verify_key, 'exception is %s, url is %s' % (repr(e), url), traceback.format_exc())
    return ''

'''
get sleep time 
unit millisecond
'''
def get_sleep_time(start_time):
    """
    Return the number of a given start time.

    Args:
        start_time: (int): write your description
    """
    offset = start_time - int(time.time()*1000)
    if offset < 5 * 1000:
        # return 0.1 * 1000
        return offset
    if offset < 30 * 1000:
        return 5 * 1000
    if offset < 90 * 1000:
        return 20 * 1000
    if offset < 3 * 60 * 1000:
        return 60 * 1000
    return 2 * 60 * 1000

'''
get_prepare_school
time unit is millisecond
'''
def get_prepare_school(left_region=0, right_region=0, opentime_lsdict=[]) -> list:
    """
    Prepare the left and end timestamp.

    Args:
        left_region: (str): write your description
        right_region: (todo): write your description
        opentime_lsdict: (str): write your description
    """
    # opentime_lsdict : #[{'schl_abbr':''20:10-23:59'},{}...]
    schl_dct = {}
    for schl in opentime_lsdict:
        schl, timestr = schl['schl_abbr'], schl['open_time']
        timestr = timestr.replace(' ', '').replace('：', ":").split('-')[0]
        timestamp = int(time.mktime(time.strptime(get_date(format='%Y%m%d')+' '+timestr.strip()+':00', "%Y%m%d %H:%M:%S") )) * 1000
        if timestamp >= left_region and timestamp<right_region:
            schl_dct[schl] = timestamp
    #  {'schl':int}; millisecond
    return schl_dct

'''
read conf with sections param
return dict
'''
def read_conf(file='./test', section='', key_name='')-> dict:
    """
    Read configuration file.

    Args:
        file: (str): write your description
        section: (todo): write your description
        key_name: (str): write your description
    """
    try:
    # if True:
        conf = configparser.ConfigParser()
        conf.read(file, encoding="utf-8")
        # section == None
        if not section:
            # return section-k-v
            tmp_dict = {}
            section_ls = conf.sections()
            for sct in section_ls:
                tmp_dict[str(sct)] = dict(conf.items(sct))
            return tmp_dict

        # section not found
        section_ls = conf.sections()
        if section not in section_ls:
            raise Exception('#section not found')
            return {}

        # key_name == None
        if not key_name:
            # return section k-v
            return dict(conf.items(section))
        # key_name not found
        options_keys_ls = conf.options()
        if key_name not in options_keys_ls:
            raise Exception('#key_name not found')
            return {}

        return {key_name: conf.get(section, key_name)}
    except Exception as e:
        # debug_p('[E]: action [%s] failed, exception is %s' % ('read_conf', repr(e)))
        return {}

'''
sqlite3 action
compatible all sqlite database
'''
class SqlAct():
    # PATH = './'
    # PATH = '/root/igotolibrary/data/' if not LOCAL else './data/'
    # local path
    LOCAL_PATH = './'
    PATH = LOCAL_PATH if LOCAL else '/root/igotolibraryagain/data/'
    # db_igtl_data = './data/igtl_data.db'
    db_igtl_data = 'igtl_data.db'
    tb_schl_lib_stmp = 'schl_lib_stmp'
    tb_today_task = 'today_task'
    tb_origin_cmd_log = 'origin_cmd_log'

    # tb_task_history =  'task_history'
    tb_task_result = 'task_result'
    # task_kind_dct = {'reserve': 2, 'realtime': 1}
    pattern_dct = {'pre': 2, 'today': 1}
    succ_failed_dct = {'succ': 2, 'failed': 1}

    creat_tb_cmd = '''
        CREATE TABLE IF NOT EXISTS schl_lib_stmp(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                platform TEXT NOT NULL,
                schl_abbr TEXT NOT NULL ,
                schl_nm TEXT  NOT NULL ,
                open_time DATETIME ,
                libid INTEGER NOT NULL UNIQUE ,
                clssrm_nm TEXT NOT NULL ,
                seatmap_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS task_result(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            userid TEXT NOT NULL  NOT NULL ,
            task_id INTEGER  NOT NULL,
            task_kind INTEGER    NOT NULL ,
            wechat_sess_id TEXT  NOT NULL ,
            submit_time DATETIME ,
            succ_failed INTEGER ,
            detail_info TEXT ,
            others_result_info TEXT        
        );

        CREATE TABLE IF NOT EXISTS origin_cmd_log(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            task_id INTEGER NOT NULL, 

            userid TEXT NOT NULL  NOT NULL , 
            task_kind INTEGER    NOT NULL ,
            wechat_sess_id TEXT  NOT NULL ,

            succ_failed INTEGER ,
            detail_info TEXT,
            others_result_info TEXT,

            user_name TEXT, 
            school_name TEXT,

            schl_abbr TEXT,
            open_time DATETIME,

            classroom_name1 TEXT, 

            libid1 INTEGER, 
            seat_num1 INTEGER,
            coordinate1 TEXT,

            classroom_name2 TEXT, 
            libid2 INTEGER, 
            seat_num2 INTEGER, 

            coordinate2 TEXT,
            serverid TEXT, 
            comment_info TEXT,

            submit_time DATETIME,
            pattern INTEGER,
            platform INTEGER,

            others_info TEXT
        );

        CREATE TABLE IF NOT EXISTS today_task(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            task_id INTEGER NOT NULL, 

            userid TEXT NOT NULL  NOT NULL , 
            task_kind INTEGER    NOT NULL ,
            wechat_sess_id TEXT   NOT NULL ,

            succ_failed INTEGER ,
            detail_info TEXT,
            others_result_info TEXT,

            user_name TEXT, 
            school_name TEXT,

            schl_abbr TEXT,
            open_time DATETIME,

            classroom_name1 TEXT, 

            libid1 INTEGER, 
            seat_num1 INTEGER,
            coordinate1 TEXT,

            classroom_name2 TEXT, 
            libid2 INTEGER, 
            seat_num2 INTEGER, 

            coordinate2 TEXT,
            serverid TEXT, 
            comment_info TEXT,

            submit_time DATETIME,
            pattern INTEGER,
            platform INTEGER,
            
            others_info TEXT
        );
        
        
        

        CREATE UNIQUE INDEX IF NOT EXISTS  today_task_idx ON today_task(task_kind, userid);



        CREATE TRIGGER IF NOT EXISTS  cmd_backup AFTER INSERT ON today_task 
        FOR EACH ROW 
        BEGIN 
            INSERT INTO origin_cmd_log 
                    (userid, task_kind, wechat_sess_id, succ_failed, detail_info, others_result_info , task_id, user_name, school_name, schl_abbr, open_time, classroom_name1, libid1, seat_num1, coordinate1, classroom_name2,  libid2, seat_num2, coordinate2, serverid, comment_info, submit_time, pattern, platform, others_info )
                    VALUES(new.userid, new.task_kind, new.wechat_sess_id,                           new.succ_failed, new.detail_info, new.others_result_info , new.task_id, new.user_name, new.school_name, new.schl_abbr, new.open_time, new.classroom_name1, new.libid1, new.seat_num1, new.coordinate1, new.classroom_name2, new.libid2, new.seat_num2, new.coordinate2, new.serverid, new.comment_info, new.submit_time, new.pattern, new.platform, new.others_info);
        END;

        '''
        # CREATE UNIQUE INDEX IF NOT EXISTS  origin_cmd_log_idx ON origin_cmd_log(task_kind, userid);

    test_sql = '''
          insert into today_task  (userid, task_kind, wechat_sess_id, succ_failed, detail_info, others_result_info , task_id, user_name, school_name, schl_abbr, open_time, classroom_name1, libid1, seat_num1, coordinate1, classroom_name2,  libid2, seat_num2, coordinate2, serverid, comment_info, submit_time, pattern, platform, others_info )
          VALUES( 'omCB3wRBvkwvKiGWRyFi0CsdAnLk', 1,'wechatSESS_ID=574a9960510a35e96205d1343b070b506737f48c3f542f39', 2, '成功', 'others_result_info', 11711, '___user_name       ', '北京交通大学', 'bjtu' ,'20:10', '第一自习室A区 (5楼)', 323, 80, '8,29 ','第二自习室B区(5楼) ','324 ','81 ','15,19 ','SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1234567890|1562999230 ','comment_info',20190718172349, 1, 1, 'others_info')

                REPLACE into today_task  (userid, task_kind, wechat_sess_id, succ_failed, detail_info, others_result_info , task_id, user_name, school_name, schl_abbr, open_time, classroom_name1, libid1, seat_num1, coordinate1, classroom_name2,  libid2, seat_num2, coordinate2, serverid, comment_info, submit_time, pattern, platform, others_info )
          VALUES( 'omCB3wRBvkwvKiGWRyFi0CsdAnLk', 2,'wechatSESS_ID=574a9960510a35e96205d1343b070b506737f48c3f542f39', 2, '成功', 'others_result_info', 11711, '___user_name       ', '北京交通大学', 'bjtu' ,'20:10', '第一自习室A区 (5楼)', 323, 80, '8,29 ','第二自习室B区(5楼) ','324 ','81 ','15,19 ','SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1234567890|1562999230 ','comment_info',20190718172349, 1, 1, 'others_info')


                   REPLACE into today_task  (userid, task_kind, wechat_sess_id, succ_failed, detail_info, others_result_info , task_id, user_name, school_name, schl_abbr, open_time, classroom_name1, libid1, seat_num1, coordinate1, classroom_name2,  libid2, seat_num2, coordinate2, serverid, comment_info, submit_time, pattern, platform, others_info )
          VALUES( '2omCB3wRBvkwvKiGWRyFi0CsdAnLk', 1,'2wechatSESS_ID=574a9960510a35e96205d1343b070b506737f48c3f542f39', 2, '成功', 'others_result_info', 11711, '___user_name       ', '北京交通大学', 'bjtu' ,'20:10', '第一自习室A区 (5楼)', 323, 80, '8,29 ','第二自习室B区(5楼) ','324 ','81 ','15,19 ','SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1234567890|1562999230 ','comment_info',20190718172349, 1, 2, 'others_info')

        '''

    # init
    def __init__(self, db_name='igtl_data'):
        """
        Initialize a sqlite database

        Args:
            self: (todo): write your description
            db_name: (str): write your description
        """
        self.conn = sqlite3.connect(SqlAct.PATH+SqlAct.db_igtl_data, check_same_thread=False)
        # transfer query result to dict
        def dict_factory(cursor, row):
            """
            Return a dictionary of sqlite table.

            Args:
                cursor: (todo): write your description
                row: (str): write your description
            """
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        self.conn.row_factory = dict_factory
        self.cur = self.conn.cursor()


        # creat table if not exist
        self.cur.executescript(SqlAct.creat_tb_cmd)
        self.conn.commit()

    # insert seat map
    def insert(self, sql_cmd):
        '''
        insert seat map
        :param sql_cmd:
        :return:
        '''
        pass

    # # execute sql statement
    # def exe_sql(self, act_kind = 'select', kind='SELECT', sql_cmd='SELECT * FROM test_table', param=[()]):
    #     '''
    #     execute sql statement
    #     :param act_kind:
    #     :param sql_cmd:
    #     :return: exe status
    #     '''
    #     res = self.cur.executemany(sql_cmd,param)
    #     return res

    # query today task
    @catch_exception
    def query_today_task(self, schl_abbr='') -> dict:
        '''
        query {} from sqlite3 where schl_abbr=schl_abbr and ..

        '''
        # sql_select = 'SELECT * FROM ' + SqlAct.tb_today_task + ' WHERE schl_abbr LIKE \"' + schl_abbr.lower() + '\";'
        #SELECT * FROM   today_task  WHERE schl_abbr LIKE  'ecut' AND timestamp LIKE '20190802%';
        today_date = get_date()
        sql_select = 'SELECT * FROM ' + SqlAct.tb_today_task + ' WHERE schl_abbr LIKE \"' + schl_abbr.lower() + '\" AND timestamp LIKE \"'+today_date+'%\";'
        self.cur.execute(sql_select)
        res = self.cur.fetchall()
        if not res:
            return {}
        # res is list[dict]
        return res

    # query_school_info return   {            ,school_abbr:'', school_name:'', classroom:[{'classroom_name':classroom_name,'libid':libid,                       'seat_map':''},{},{}...]}
    @catch_exception
    def query_school_info(self, schl_abbr='', libid1='', libid2=''):
        '''
        query {} from sqlite3 where schl_abbr=schl_abbr and ..

        '''
        libid1 = libid2 if not libid1 else libid1
        sql_select = 'SELECT * FROM ' + SqlAct.tb_schl_lib_stmp + ' WHERE schl_abbr LIKE \"' + schl_abbr.lower() +'\"'
        condition = ' AND ( '
        if libid1:
            condition += ' libid == ' + str(libid1) + ' ' + (' OR libid == ' + str(libid2) if libid2 else ' ')
        else:
            condition += ' TRUE '
        condition += ' );'
        # debug_p('sql_select=', sql_select)#+condition)
        # query
        self.cur.execute(sql_select)#+condition)
        # dict : [{'id': 3, 'schl_abbr': 'bbmc', 'schl_nm': '蚌埠医学院','open_time':'06:10-08:00', 'libid': 231, 'clssrm_nm': '图书馆一楼', 'seatmap_json': "'{22:01,02}'"}, {} ]
        res = self.cur.fetchall()
        if not res:
            # except , data not found
            return {}
        user_conf_dict = {}
        user_conf_dict['schl_abbr'], user_conf_dict['school_name'], user_conf_dict['open_time'],  = res[0]['schl_abbr'], res[0]['schl_nm'], res[0]['open_time']
        clssrm = []
        for a_record in res:
            clssrm.append({'classroom_name': a_record['clssrm_nm'], 'libid':str(a_record['libid']), 'seat_map': json.loads(a_record['seatmap_json'])})
        # {user_name:'',school_abbr:'', school_name:'','open_time':'06:10', classroom:[{'classroom_name':classroom_name,'libid':libid, 'path':classroom_path,'seat_map':''},{},{}...]}
        # {            ,school_abbr:'', school_name:'','open_time':'06:10', classroom:[{'classroom_name':classroom_name,'libid':libid,                       'seat_map':''},{},{}...]}
        user_conf_dict['classroom'] = clssrm
        # assert open_time format is hh:mm:ss , three part
        if user_conf_dict['open_time'].count(':') == 1:
            user_conf_dict['open_time'] += ':00'
        return user_conf_dict

    '''
    get open time list from sqlite
    '''
    @catch_exception
    def get_opentime(self):
        """
        Return a list of sqlite databases.

        Args:
            self: (todo): write your description
        """
        sql_select = 'SELECT schl_abbr, open_time FROM ' + SqlAct.tb_schl_lib_stmp + ' GROUP BY schl_abbr ;'
        self.cur.execute(sql_select)
        res = self.cur.fetchall()
        if not res:
            # except , data not found
            return [{}]
        user_conf_dict = res
        #[{'schl_abbr':''20:10-23:59'},{}...]
        return user_conf_dict

    '''
    close conn and re-open database
    '''
    @catch_exception
    def refresh(self):
        """
        Refresh the connection

        Args:
            self: (todo): write your description
        """

        try:
            self.conn.close()
        except Exception as e:
            print('#self.conn.close except')

            pass
        self.__init__()

    '''
    del tb_today_task
    '''
    @catch_exception
    def del_todaytask(self):
        """
        Deletes a task s tasks.

        Args:
            self: (todo): write your description
        """
        sql_delete = ' DELETE FROM  ' + self.tb_today_task+' ;'
        self.cur.execute(sql_delete)
        self.conn.commit()
        debug_p('[utils.del_todaytask] del_todaytask action succ')

    '''
    save task_result to sqlite
    '''
    @catch_exception
    def update_comment(self, task_result, condition_id):
        """
        Updates the comment

        Args:
            self: (todo): write your description
            task_result: (todo): write your description
            condition_id: (str): write your description
        """
        func_name = '[utils.update_comment]'
        sql_update = 'UPDATE ' + self.tb_origin_cmd_log + ' SET comment_info = \'' + \
                     task_result + '\'' + ' WHERE id=' + str(condition_id) + ';'
        try:
            self.cur.execute(sql_update)
            self.conn.commit()
        except Exception as E:
            debug_p(func_name, '[E]: update_comment action error', task_result, condition_id)

    '''
    get_ready_task
    '''
    @catch_exception
    def get_ready_task(self, start_ts=1570245000000, end_ts=1570245120000):
        """
        Returns a task object for the task

        Args:
            self: (todo): write your description
            start_ts: (todo): write your description
            end_ts: (todo): write your description
        """

        start_date = time.strftime("%Y-%m-%d %H:%M:%S",  time.localtime(start_ts//1000)).split()[1]
        end_date = time.strftime("%Y-%m-%d %H:%M:%S",  time.localtime(end_ts//1000)).split()[1]
        '''
        SELECT *, strftime('%s', \'{date}\' || open_time || \'{:00}\') as open_time_ts FROM  today_task WHERE  open_time_ts >= {start_s} AND'
          ' open_time_ts < {end_s} ; '.format()
          
          SELECT strftime('%s', '2019-10-05' || ' ' || open_time || ':00', 'utc') as open_time_ts    FROM  today_task ;
        '''
        # assert open_time format is hh:mm:ss,   because   20:09:59 < 20:10 < 20:10:00
        sql_select = 'SELECT * FROM  ' + self.tb_today_task + ' WHERE ' \
                      '(task_kind=\'' + GBCF.TASK_KIND['realtime'] + '\'  AND open_time < \'{end_date}\') OR ' \
                      '( open_time >= \'{start_date}\' AND open_time < \'{end_date}\' ) ; '

        sql_select = sql_select.format(start_date=start_date, end_date=end_date)
        self.cur.execute(sql_select)
        # [{}, {}, ...]
        res = self.cur.fetchall()
        if not res:
            res = []
        print(sql_select,  res)
        return res

    '''
    del a task
    '''
    @catch_exception
    def del_task(self, userid, task_kind, wechat_sess_id):
        '''

        '''
        sql_delete = ' DELETE FROM ' + self.tb_today_task + '  WHERE ' + \
            'userid=\'{userid}\' AND task_kind=\'{task_kind}\' AND wechat_sess_id=\'{wechat_sess_id}\' ; '.\
            format(userid=userid, task_kind=task_kind, wechat_sess_id=wechat_sess_id)
        # debug_p('### test', sql_delete)
        self.cur.execute(sql_delete)
        self.conn.commit()

    '''
    insert/replace into tast_result
    '''
    @catch_exception
    def add_task_result(self, task):
        '''
        '''
        sql_insert = 'INSERT INTO ' + self.tb_task_result + \
                     '(userid, task_id, task_kind, wechat_sess_id, submit_time, succ_failed, detail_info, others_result_info)' + \
                     ' VALUES(?,?,?,?,?,?,?,?)'

        param = (task['userid'], task['task_id'], task['task_kind'], task['wechat_sess_id'], task['submit_time'], task['succ_failed'],
                 task['detail_info'], task['others_result_info'])
        self.cur.execute(sql_insert, param)
        self.conn.commit()

'''
memcache
'''
class MyMemcache(object):

    def __init__(self, ip='localhost', port=11211):
        """
        Init a new serializer.

        Args:
            self: (todo): write your description
            ip: (str): write your description
            port: (int): write your description
        """
        # json_serializer(key, value)
        def json_serializer(key, value):
            """
            Convert a serializer.

            Args:
                key: (str): write your description
                value: (todo): write your description
            """
            if type(value) == str:
                return value, 1
            return json.dumps(value), 2
        # json_deserializer(key, value, flags) python3
        def json_deserializer(key, value, flags):
            """
            Deserialize the given value.

            Args:
                key: (str): write your description
                value: (todo): write your description
                flags: (todo): write your description
            """
            if flags == 1:
                return value.decode('utf-8')
            if flags == 2:
                return json.loads(value.decode('utf-8'))
            raise Exception("Unknown serialization format")

        self.ip = ip
        self.port = port
        self.client = Client((ip, port),
                              serializer=json_serializer,
                              deserializer=json_deserializer,
                              key_prefix='',
                              encoding='utf8',
                              allow_unicode_keys=True)

    '''
    set_task_result
    '''
    @catch_exception
    def set_value(self, key, value):
        """
        Sets the value of a key.

        Args:
            self: (todo): write your description
            key: (str): write your description
            value: (todo): write your description
        """
        # set(key, value, expire=0, noreply=None, flags=None)
        # result = "-".join(result.split())
        expire_second = int(60 * 60 * 24 * 1.2) # expire_second must int
        self.client.set(key=key, value=value, expire=expire_second)

        # debug_p('[set_value]', key, value)

    '''
    get_task_result
    '''
    @catch_exception
    def get_value(self, key, default=''):
        """
        Returns the value of a key.

        Args:
            self: (todo): write your description
            key: (str): write your description
            default: (todo): write your description
        """
        result = self.client.get(key=key, default=default)

        debug_p('[get_value]', key, result)

        return result

    '''
    close
    '''
    def client_close(self):
        """
        Closes the connection.

        Args:
            self: (todo): write your description
        """
        try:
            self.client.close()
        except Exception as e:
            #
            pass
'''
test main
'''
if __name__ == '__main__':
    LOCAL = True

    # mc = MyMemcache()
    # mc.set_task_result(userid='userid_test1121', result='座💺位预定成、\n功，1  2')
    # print('set ok')
    # 
    # result = mc.get_task_result(userid='userid_test1121')
    # print('get ok, result=', result)

    a = SqlAct()

    a.get_ready_task()

    debug_p('ok', 'cf.RESPONSE_FLAG[NEED_VERIFY_CODE', )


