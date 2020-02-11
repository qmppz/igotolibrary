#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @filename:mhandle_content.py
# @author: wheee/qmppz
# @time:20190709
# @description:  handle msg, python3

import configparser
import time
import random
import json
import os
import re
import requests

import sys
# sys.path.append("../..")
# import igotolibrary.mhandle_content as test_mhandle_content

import utils
import crawldata

'''
conf for this py file
refresh first time
'''
# GBCF = utils.GBCF
a_task = utils.Atask()

CF = utils.GBCF()

# add value
CF.task_id = int(utils.get_date().split('_')[0]) - 20180000 + (100 if int(utils.get_date().split('_')[0]) % 2 == 0 else -100) + 1110
requests.adapters.DEFAULT_RETRIES = 5
CF.sess = requests.Session()
CF.sess.keep_alive = False
# sql action
sqlact = utils.SqlAct()
# memcache
mc = utils.MyMemcache()

# debug print
debug_p = utils.debug_p


'''
get_reply_msg from robot
'''


def get_reply_msg(str_info, str_flg='ROBOT', sess=object):
    if str_flg == "ROBOT":
        # if str_info.find("抢座") >= 0 or str_info.find("帮助") >= 0  :
        #     return ' '
        # turing robot
        api_url = 'http://openapi.tuling123.com/openapi/api/v2'
        data = {
            "reqType": 0,  # 输入类型 0-文本, 1-图片, 2-音频
            "perception":  # 信息参数
            {
                "inputText":  # 文本信息
                {
                    "text": str_info
                },

                "selfInfo":  # 用户参数
                {

                }
            },
            "userInfo":
            {
                "apiKey": ["b5f0fb8408a5490a8bbd844772514798", "00410b2abac142e9941af7c8f5604e6c", "808a6d0f20bd47a28e575a9561900038"][random.randint(0, 3)],
                # 改为自己申请的key
                "userId": "0001"  # 用户唯一标识(随便填, 非密钥)
            }
        }
        data = json.dumps(data).encode('utf8')

        response = requests.post(api_url, data=data, headers={'content-type': 'application/json'})

        replys = json.loads(response.text, encoding="UTF-8")

        return replys
    elif str_flg == "RIGHT":
        return str_info
    elif str_flg == "ERROR":
        return str_info
    else:
        return "#[E]: 致命错误!"


'''
class for cmd prefix map to function
'''


class CmdFunction():

    CMD_HINT = {
        'HELP': '请回复:\n\n指令帮助\n\n',
        'CMD_HELP': '【抢座指令】请按如下格式发送指令:\n#抢座; 学校英文简称; 自习室id;座位号; 自习室id;座位号; wechat_sess_id; serverid;',
        'CMD_CHECK': ' '
    }

    HELP_INFO = {

    }

    face_ico = {
        'positive': ['😃 ', '😏 ', '😁 ', '😌 ', '😜 ', '😝', '😂 '],
        'emmm': ['😂'],
        'negative': ['😂', '😰 ', '😭 ', '😱 ', '😨 ', '😷 ', '😔']
    }

    def getico(flag='emmm'):
        if flag == -1:
            flag = 'negative'
        elif flag == 1:
            flag = 'positive'
        elif flag == 0:
            flag = 'emmm'
        return random.choice(CmdFunction.face_ico[flag])

    '''
    modify_opentime
    '''
    # @utils.catch_exception
    def modify_opentime(userid, content):
        # xgqzsj, bjtu, 20:35
        # opentime : 20:35
        _, schl_abbr, opentime = content.split(CF.USER_CMD_SPLTCH)
        opentime = opentime.split('-')[0].replace('.', ':')

        # 6:00 --> 06:00
        if len(opentime.split(':')[0]) == 1:
            opentime = '0' + opentime
        # 20:10  --> 20:10:00
        if opentime.count(':') == 1:
            opentime += ':00'

        if not schl_abbr or not opentime or opentime.count(':') < 1:
            return 'modify_opentime failed'
        # UPDATE schl_lib_stmp SET open_time = '00:00' WHERE schl_abbr like  'bjtu';
        sql_update = 'UPDATE ' + sqlact.tb_schl_lib_stmp + ' SET open_time = \'' + opentime + '\'  WHERE schl_abbr like \'' + schl_abbr.lower() + '\';'
        sqlact.cur.execute(sql_update)
        sqlact.conn.commit()

        return 'modify_opentime succ'

    '''
    check school info if exist
    '''
    def check_school(userid, content):
        check_cmd_str = '#查询; 学校英文简称'
        info = {
            'verify_failed_format': CmdFunction.getico(-1) + '操作失败:【指令格式可能有误】;请按如下指令查询学校信息:\n\n' + check_cmd_str,
            'schl_info_not_found': CmdFunction.getico(-1) + '暂无 [{school_info}] 的自习室信息，请发送【添加】指令进行学校信息添加；格式如下:\n\n#添加学校; 学校英文简称; wechat_sess_id; serverid',
            'check_succ': CmdFunction.getico(1) + '查询成功，[{school_name}-{schl_abbr}]自习室信息如下:\n\n{classrm_libid}\n开放抢座时间：{open_time}'
        }
        func_name = '[check_school]'
        tmp_ls = content.split(CF.USER_CMD_SPLTCH)
        if len(tmp_ls) < 2:
            return info['verify_failed_format']
        _, schl_abbr = tmp_ls[:2]

        # check [school_name] seatmap data exist or not; # {user_name:'',schl_abbr:'', 'open_time':'', school_name:'', classroom:[{'classroom_name':classroom_name,'libid':libid, 'path':classroom_path,'seat_map':''},{},{}...]}
        user_conf_dict = sqlact.query_school_info(schl_abbr=schl_abbr)  # , libid1='', libid2=libid2)
        debug_p('func_name=', func_name, 'query_school_info()', user_conf_dict)
        if not user_conf_dict:
            # schl_info_not_found
            reply_text = info['schl_info_not_found'].replace('{school_info}', schl_abbr)
            debug_p('func_name=', func_name, 'reply_text=', reply_text)
            return reply_text
        else:
            school_name = user_conf_dict.get('school_name', 'school_name')
            # schl_info_found
            reply_text = info['check_succ'].replace('{school_name}', school_name).replace('{schl_abbr}', schl_abbr).replace('{open_time}', user_conf_dict.get('open_time', '--:--')).replace('{classrm_libid}', '\n'.join([e['classroom_name'] + '-id=' + str(e['libid']) for e in user_conf_dict['classroom']]))
            debug_p('func_name=', func_name, 'reply_text=', reply_text)
            return reply_text

    '''
    force_add_school_info
    '''
    def force_add_school_info(userid, content):
        func_name = '[force_add_school_info]'
        debug_p(func_name, 'content=', content)
        return CmdFunction.add_school_info(userid=userid, content=content, force=True)

    '''
    add school  info
    '''
    def add_school_info(userid, content, force=False):
        '''
        #添加学校; bbmc; wechat_sess_id; serverid
        '''
        func_name = '[add_school_info]'
        info = {
            'verify_failed_format': CmdFunction.getico(-1) + '操作失败:【添加指令格式可能有误】；\n在自身没有预约座位和自习室开放的状态下，添加指令才能有效；请按如下指令添加学校信息:\n\n#添加学校; 学校英文简称; wechat_sess_id; serverid',
            'verify_failed_wechat_sess_id_invalid': CmdFunction.getico(-1) + '操作失败:【wechat_sess_id; serverid可能失效】;\nwechat_sess_id、serverid是需要自己去抓包获取的，不是示例里面的qwertyxxxx，具体获取方法请看指令帮助文档。',
            'failed_add_school_except': CmdFunction.getico(-1) + '操作失败:【尝试获取自习室信息失败】\n 在自身没有预约座位和自习室开放的状态下，添加指令才能有效；多次出错请联系管理员',
            'already_exist': CmdFunction.getico(1) + '操作成功:【学校 [{schl_abbr}] 的自习室信息已经存在】;自习室信息如下:\n\n{classrm_libid}\n开放抢座时间：{open_time};\n快使用抢座指令添加任务吧！\n自习室的数量 id 时间不正确请反馈管理员',
            'succ_add_school_info': CmdFunction.getico(1) + '操作成功:【成功添加学校 [{school_name}-{schl_abbr}] 的自习室信息】;信息如下:\n\n{classrm_libid}\n开放抢座时间：{open_time}\n自习室的数量 id 时间不正确请反馈管理员'

        }
        # #添加学校, schl_abbr, sess_id, - 平台=来选座
        tmp_ls = content.split(CF.USER_CMD_SPLTCH)
        # if len(tmp_ls) < 4:
        if len(tmp_ls) < 3:
            return info['verify_failed_format']
        # _, schl_abbr, wechat_sess_id, serverid = tmp_ls[:4]
        _, schl_abbr, wechat_sess_id = tmp_ls[:3]

        cmd_dict = utils.parse_extra_cmd(extra_cmd=content)
        # init a_task
        # if cmd_dict.get('platform') == 'CTRS':
        a_task = utils.Atask(platform=cmd_dict.get('platform', CF.PLATFORM['IGTL']))

        # schl_abbr transfer to  lower
        schl_abbr = str(schl_abbr).replace('[', '').replace(']', '').lower()

        # verify_key = '您好'
        # url_homepage = 'https://wechat.v2.traceint.com/index.php/reserve/index.html?f=wechat'
        # # fill cookies
        # if serverid.split('|') != 3:
        #     serverid = serverid.split('|')[0] + '|' + '1234567890' + '|' + a_task.M_COOKIES['SERVERID'].split('|')[-1]
        # a_task.M_COOKIES = utils.fill_cookies(cookies=a_task.M_COOKIES, serverid=serverid, wechat_sess_id=wechat_sess_id)
        a_task.M_COOKIES = utils.fill_cookies(cookies=a_task.M_COOKIES, wechat_sess_id=wechat_sess_id, platform=a_task.platform)
        # entry homepage
        homepage_response = utils.get_response(url=a_task.CURRENT_URL['home_page'],
                                               sess=CF.sess,
                                               m_headers=a_task.M_HEADERS,
                                               m_cookies=a_task.M_COOKIES,
                                               verify_key=a_task.VERIFYKEY_OF_HOMEPAGE)
        if not homepage_response:
            # verify failed; cmd is invalid
            return info['verify_failed_wechat_sess_id_invalid']
        debug_p('homepage_response=', homepage_response[:200])
        # parse homepage_response get user_name, school_name
        user_name, school_name = crawldata.get_name(homepage_response)

        # check [school_name] seatmap data exist or not; # {user_name:'',schl_abbr:'', school_name:'', 'open_time':'', classroom:[{'classroom_name':classroom_name,'libid':libid, 'path':classroom_path,'seat_map':''},{},{}...]}
        user_conf_dict = sqlact.query_school_info(schl_abbr=schl_abbr, libid1='', libid2='')

        # if query failed, refresh school info
        if force == True or not user_conf_dict:
            # school info not exist, refresh this school;     # {user_name:'',schl_abbr:'', school_name:'', 'open_time':'', classroom:[{'classroom_name':classroom_name,'libid':libid, 'path':classroom_path,'seat_map':''},{},{}...]}
            # user_conf_dict = crawldata.refresh_school_info(homepage_url='', homepage_response=homepage_response,
            #                                                sess=CF.sess, m_headers=a_task.M_HEADERS,
            #                                                m_cookies=a_task.M_COOKIES,
            #                                                verify_key='',
            #                                                schl_abbr=schl_abbr,
            #                                                platform=a_task.platform,
            #                                                sql_conn=sqlact.conn
            #                                                )
            user_conf_dict = crawldata.refresh_school_info(homepage_response=homepage_response,
                                                           a_task=a_task,
                                                           schl_abbr=schl_abbr,
                                                           sess=CF.sess, m_headers=a_task.M_HEADERS,
                                                           m_cookies=a_task.M_COOKIES,
                                                           sql_conn=sqlact.conn
                                                           )
        else:
            # already exist
            reply_text = info['already_exist'].replace('{schl_abbr}', schl_abbr).replace('{open_time}', user_conf_dict.get('open_time', '--:--')).replace('{classrm_libid}', '\n'.join([e['classroom_name'] + '-id=' + str(e['libid']) for e in user_conf_dict['classroom']]))
            debug_p('func_name=', func_name, 'reply_text=', reply_text)
            return reply_text
        if not user_conf_dict.get('classroom', []):
            return info['failed_add_school_except']

        reply_text = info['succ_add_school_info'].replace('{school_name}', user_conf_dict.get('school_name', 'school_name')).replace('{schl_abbr}', schl_abbr).replace('{open_time}', user_conf_dict.get('open_time', '--:--')).replace('{classrm_libid}', '\n'.join([e['classroom_name'] + '-id=' + str(e['libid']) for e in user_conf_dict['classroom']]))
        debug_p('func_name=', func_name, 'reply_text=', reply_text)
        return reply_text

    '''
    parse trace,return serverid wechat_sess_id  # and two time value
    '''
    def parse_trace(userid, content):
        # verify content format
        info = {
            'verify_failed': CmdFunction.getico(-1) + '您发送的 trace 校验格式不通过，请重新获取后再尝试！'

        }

        if len(content) < 100:
            return info['verify_failed']
        if content.find('wechatSESS_ID') < 0:
            return info['verify_failed'] + '\n' + '没有找解析出 wechatSESS_ID 字段'
        # elif content.find('SERVERID')<0:
        #     return info['verify_failed']+'\n'+'没有找解析出 SERVERID 字段'

        try:
            content += ' ;'
            # pattern = re.compile(r'SERVERID\=\w+\|\d{10}\|\d{10}')
            # SERVERID = pattern.search(content).group(0)

            pattern = re.compile(r'wechatSESS_ID\=\w+(?=[\s;])')
            wechatSESS_ID = pattern.search(content).group(0)

            # pattern = re.compile(r'(?<=Hm_lvt_\w{32}\=)\d{10}(?=[\s;])')
            # Hm_lvt_time = pattern.search(content).group(0)
            #
            # SERVERID_time_2 = re.compile(r'(?<=SERVERID\=\w{32}\|\d{10}\|)\d{10}(?=[\s;])')
            # SERVERID_time_2 = pattern.search(content).group(0)

            return '\n' + wechatSESS_ID + '\n'  # +SERVERID

        except Exception as e:
            debug_p('[E]: action [%s] failed, exception is %s' % ('parse_trace', repr(e)))
            return info['verify_failed'] + '[wechatSESS_ID 没有找到]'

    '''
    realtime
    '''
    def realtime(userid, content):
        func_name = '#realtime'
        debug_p('func_name=', func_name, 'userid, content', userid, content)
        return CmdFunction.grab_seat(userid, content, task_kind=CF.TASK_KIND['realtime'])

    '''
    grab_seat
    '''
    def grab_seat(userid, content, task_kind=CF.TASK_KIND['reserve']):
        '''
        实时预定 | 捡漏 | jl | #jl | 明日预约 | 抢座 | #qz | qz    ；
        学校英文简称 | 首拼；
        自习室id1；座位号1；自习室id2，座位号2；
        serverid；wechat_sess_id
        extra_info:
        exetime  首次执行时间 | 开抢时间;
        pre_today 当日即时预订 | 明日预约;
        lgtl_or_ctrs 我去图书馆  |  来选座;
        unknown_cmd 扩展指令
        '''
        func_name = '#grab_seat'
        debug_p('func_name=', func_name, 'userid, content', userid, content)
        task_kind_str = '[准点抢座] ' if task_kind == CF.TASK_KIND['reserve'] else '[实时捡漏]  '
        info = {
            'grab_cmd_help': 'help info',
            'verify_failed_format': CmdFunction.getico(-1) + task_kind_str +'task提交失败:【抢座指令格式可能有误】\n请仔细检查并按如下顺序重新编辑发送:\n\n#抢座; 学校英文简称; 自习室id;座位号;自习室id;座位号; wechat_sess_id; serverid',
            'verify_failed_wechat_sess_id_invalid': CmdFunction.getico(-1) + task_kind_str + 'task提交失败:【wechat_sess_id; serverid可能失效】\nwechat_sess_id、serverid是需要自己去抓包获取的，不是示例里面的qwertyxxxx，更不是wechat_sess_id，serverid这两个单词；具体获取方法请看指令帮助文档。',
            'verify_failed_get_school_info': CmdFunction.getico(-1) + task_kind_str + 'task提交失败:【座位表信息不匹配】请确认自习室信息存在且自习室id正确\n如需帮助请联系管理员处理',
            'verify_failed_seatnum_not_found': CmdFunction.getico(-1) + task_kind_str + 'task提交失败:【自习室id不匹配或不存在此座位号】请检查后再试\n支持的自习室的id信息:{classrm_libid}',

            'unknown_error': CmdFunction.getico(-1) + task_kind_str + 'task提交失败；未知错误；\n请联系管理员并提供如下信息:\n\n{unknown_error}',

            'verify_succ': CmdFunction.getico(1) + task_kind_str + 'task提交成功:task_id={task_id}；\n您的任务信息如下:\n{task_info}',

        }
        if not content:
            reply_text = info['help_info']
            debug_p('func_name=', func_name, 'reply_text=', reply_text)
            return reply_text

        # cmd type = user
        # verify format, cmd_dict : # {schl_abbr: '', libid1: '', seat_num1: '', libid2: '', seat_num2: '',serverid:'', wechat_sess_id:''}
        cmd_dict = utils.parse_grab_seat_cmd(command=content)
        debug_p('func_name=', func_name, 'parse_grab_seat_cmd()', cmd_dict)

        if not cmd_dict:
            reply_text = info['verify_failed_format']
            debug_p('func_name=', func_name, 'reply_text=', reply_text)
            return reply_text

        # normal cmd
        # schl_abbr, libid1, seat_num1, libid2, seat_num2, wechat_sess_id, serverid = cmd_dict['schl_abbr'], cmd_dict['libid1'], cmd_dict['seat_num1'], cmd_dict['libid2'], cmd_dict['seat_num2'], cmd_dict['wechat_sess_id'], cmd_dict['serverid']
        schl_abbr, libid1, seat_num1, libid2, seat_num2, wechat_sess_id, = cmd_dict['schl_abbr'], cmd_dict['libid1'], cmd_dict['seat_num1'], cmd_dict['libid2'], cmd_dict['seat_num2'], cmd_dict['wechat_sess_id']  # , cmd_dict['serverid']
        # cmd
        exe_time = cmd_dict.get('exe_time', '')  # open_time
        # pattern = cmd_dict.get('pattern', CF.PATTERN['PRE'])  # pre

        # a task , a Atask, init
        a_task = utils.Atask(platform=cmd_dict.get('platform', CF.PLATFORM['IGTL']),
                             pattern=cmd_dict.get('pattern', CF.PATTERN['TODAY']))

        # verify serverid and wechat_sess_id
        # fill cookies
        # a_task.M_COOKIES = utils.fill_cookies(cookies=a_task.M_COOKIES, serverid=serverid, wechat_sess_id=wechat_sess_id, platform=a_task.platform)
        a_task.M_COOKIES = utils.fill_cookies(cookies=a_task.M_COOKIES, wechat_sess_id=wechat_sess_id, platform=a_task.platform)
        debug_p('func_name=', func_name, 'fill_cookies()', a_task.M_COOKIES)
        # entry homepage
        # test
        homepage_response = utils.get_response(url=a_task.CURRENT_URL['home_page'], sess=CF.sess,
                                                                                m_headers=a_task.M_HEADERS,
                                                                                m_cookies=a_task.M_COOKIES,
                                                                                verify_key=a_task.VERIFYKEY_OF_HOMEPAGE)

        debug_p('func_name=', func_name, 'get_response()', homepage_response[:300])
        if not homepage_response:
            # verify failed; cmd is invalid
            reply_text = info['verify_failed_wechat_sess_id_invalid']
            debug_p('func_name=', func_name, 'reply_text=', reply_text)
            return reply_text
        # debug_p('homepage_response=', homepage_response)
        # parse homepage_response get user_name, school_name

        user_name, school_name = crawldata.get_name(homepage_response)

        # check [school_name] seatmap data exist or not; # {user_name:'',schl_abbr:'', 'open_time':'', school_name:'', classroom:[{'classroom_name':classroom_name,'libid':libid, 'path':classroom_path,'seat_map':''},{},{}...]}
        user_conf_dict = sqlact.query_school_info(schl_abbr=schl_abbr)  # , libid1='', libid2=libid2)
        debug_p('func_name=', func_name, 'query_school_info()', str(user_conf_dict)[:400])

        # # if query failed, refresh school info
        # if not user_conf_dict:
        #     # school info not exist, refresh this school;     # {user_name:'',schl_abbr:'', 'open_time':'', school_name:'', classroom:[{'classroom_name':classroom_name,'libid':libid, 'path':classroom_path,'seat_map':''},{},{}...]}
        #     user_conf_dict = crawldata.refresh_school_info(homepage_url='', homepage_response=homepage_response,
        #                                                    sess=CF.sess, m_headers=CF.M_HEADERS, m_cookies=CF.M_COOKIES,
        #                                                    verify_key='',
        #                                                    schl_abbr=schl_abbr,
        #                                                    sql_conn=sqlact.conn
        #                                                    )
        #     debug_p('func_name=', func_name, 'refresh_school_info()', user_conf_dict)

        # action query and refresh both failed
        if not user_conf_dict:
            reply_text = info['verify_failed_get_school_info']
            debug_p('func_name=', func_name, 'reply_text=', reply_text)
            return reply_text

        # get school info succ and then construct [re_reserve_cmd] data: task_id;userid; 323;21,31; 324;41,51; wechat_sess_id; serverid; comment_info
        user_conf_dict['user_name'] = user_name
        # get seat coordinate and classroom_name

        # all_lib_clssrm dict{libid: clssrm}
        all_lib_clssrm = dict([(classroom['libid'], classroom['classroom_name']) for classroom in user_conf_dict['classroom']])
        lib_seat_ls = [(libid1, seat_num1), (libid2, seat_num2)]
        clssrm_crdnt = CmdFunction.verify_seat(lib_seat_ls, user_conf_dict)

        # if coordinate not match, exception
        if not clssrm_crdnt:
            reply_text = info['verify_failed_seatnum_not_found'].replace('{classrm_libid}', '\n'.join([e['classroom_name'] + '-id=' + str(e['libid']) for e in user_conf_dict['classroom']]))
            debug_p('func_name=', func_name, 'reply_text=', reply_text)
            return reply_text

        classroom_name1, coordinate1 = clssrm_crdnt[0]
        classroom_name2, coordinate2 = clssrm_crdnt[1]

        debug_p('func_name=', func_name, 'get coordinate1 and coordinate2', 'classroom_name1=', classroom_name1,
                'coordinate1=',
                coordinate1, 'classroom_name2=', classroom_name2, 'coordinate2=', coordinate2)

        # construct[re_reserve_cmd] task_id; userid; user_name; school_name; classroom_name1;323;seat_num; 21,31; classroom_name2; 324; seat_num2; 41,51; wechat_sess_id; serverid; comment_info
        open_time = user_conf_dict.get('open_time', '00:00-00:00') if task_kind == CF.TASK_KIND['reserve'] else utils.get_date(format="%H:%M:%S")
        submit_time = utils.get_date(format='%Y-%m-%d %H:%M:%S')

        open_time = exe_time if exe_time else open_time
        wechat_sess_id = wechat_sess_id
        succ_failed, detail_info, others_result_info = '', '', ''
        task_id = CF.TASK_ID

        # others_info is json format
        others_info = {}
        others_info['all_lib_clssrm'] = all_lib_clssrm

        comment_info = ''
        serverid = CF.SERVERID if a_task.platform == CF.PLATFORM['IGTL'] else ''
        # print('serverid', serverid)
        param = (
            userid, task_kind, wechat_sess_id, succ_failed, detail_info, others_result_info, task_id,
            user_name, school_name, schl_abbr, open_time, classroom_name1, libid1, seat_num1, coordinate1,
            classroom_name2, libid2, seat_num2, coordinate2, serverid, comment_info, submit_time,
            a_task.pattern, a_task.platform, json.dumps(others_info)
        )

        #
        tb_today_task = 'today_task'

        # replace will delete the exist trace and insert a new trace, then the id will change
        # insert into tb_today_task
        # REPLACE into today_task  (userid, task_kind, wechat_sess_id, succ_failed, detail_info, others_result_info , task_id, user_name, school_name, schl_abbr, open_time, classroom_name1, libid1, seat_num1, coordinate1, classroom_name2,  libid2, seat_num2, coordinate2, serverid, comment_info, submit_time, pattern, platform, others_info )

        sql_today_task = 'REPLACE INTO ' + tb_today_task + \
                         '(userid, task_kind, wechat_sess_id, succ_failed, detail_info, others_result_info, task_id,' \
            'user_name, school_name, schl_abbr, open_time, classroom_name1, libid1, seat_num1, coordinate1,' \
            'classroom_name2, libid2, seat_num2, coordinate2, serverid, comment_info, submit_time,' \
            'pattern, platform, others_info) ' + \
                         ' VALUES(' + '?,' * (len(param) - 1) + '?)'

        sqlact.cur.execute(sql_today_task, param)
        sqlact.conn.commit()

        debug_p('func_name=', func_name, 'REPLACE and INSERT action; param=', param)

        reply_text = info['verify_succ'].replace('{task_id}', str(CF.TASK_ID)).replace('{task_info}', '\n[' + school_name + '-' + schl_abbr + ']' +
                                                   '的\n[' + classroom_name1 + '-id=' + libid1 + ']的[' + str(seat_num1) + ']号座位\n' +
                                                   '[' + classroom_name2 + '-id=' + libid2 + ']的[' + str(seat_num2) + ']号座位\n执行时间:' + open_time + '') + \
                                                   '\n模式:' + ('预定当日💺' if a_task.pattern == CF.PATTERN['TODAY'] else '预约明天💺') + '\n平台:' + ('<我去图书馆>' if a_task.platform == CF.PLATFORM['IGTL'] else '<来选座>')
        CF.TASK_ID += 1
        debug_p('func_name=', func_name, 'TASK_ID=', CF.TASK_ID, 'grab_seat action over, reply_text=', reply_text)
        return reply_text

    '''
    query_realtime_result
    '''
    def query_realtime_result(userid, content):
        func_name = '[query_realtime_result]'
        debug_p(func_name, 'userid, content', userid, content)
        return CmdFunction.query_result(userid, content, task_kind=CF.TASK_KIND['realtime'])

    '''
    parse the dict from memcache
    return reply str

    '''
    def parse_dct_from_mc(result_dct={}, char_limit=CF.CHAR_LIMIT):
        # exe trace format
        # TRACE_FORMAT = {
        #     'head': '状态:{status}\n[{school_name}-{schl_abbr}_{task_id}]\n{submit_time} 提交\n',
        #     'exe_trace': '{emoji}{try_cnt}. {exe_time} [{classroom_name}]-[{seat_num}]号座位:{feedback}\n',
        # }
        default_value = ''
        flag = {
            'SUCC': '✅',
            'FAILED': '❌',
            # 'Ongoing': '🔄',
            'Ongoing': '🌀',
            # 'exe_trace_failed': '⏬'
            'exe_trace_failed': '🔸'
        }
        status = 'Ongoing'
        reply_str = '...\n'
        reply_str += CF.TRACE_FORMAT['head'].format(status=flag[status] + status, school_name=result_dct.get('school_name', default_value),
                                                    schl_abbr=result_dct.get('schl_abbr', default_value), task_id=result_dct.get('task_id', default_value),
                                                    submit_time=result_dct.get('submit_time', default_value))
        if len(result_dct['exe_trace']) < 1:
            return reply_str
        code = result_dct['exe_trace'][-1].get('code', default_value)
        completed_flag = result_dct['exe_trace'][-1].get('completed_flag', default_value)
        if completed_flag == 'completed':
            status = 'SUCC' if str(code) == '0' else 'FAILED'

        for i, trace in enumerate(result_dct['exe_trace']):
            reply_str += CF.TRACE_FORMAT['exe_trace'].format(
                emoji=flag['exe_trace_failed'] if str(trace.get('code', default_value)) != '0' else flag['SUCC'],
                try_cnt=i, exe_time=trace.get('exe_time', default_value),
                classroom_name=trace.get('clssrm', default_value),
                seat_num=trace.get('seat_num', default_value), feedback=trace.get('msg', default_value))
        return reply_str[-1*char_limit:]

    '''
    query task result
    '''
    def query_result(userid, content, task_kind=CF.TASK_KIND['reserve']):
        func_name = '[query_result]'
        debug_p('func_name=', func_name, 'userid, content', userid, content)
        info = {
            'default': '没有查询到最近这段时间抢座任务执行状态信息',
        }

        reply_str = info['default']

        result = mc.get_value(key=task_kind + '_' + userid, default='')
        if result:
            reply_str = CmdFunction.parse_dct_from_mc(result)
        # parse the dict from memcache
        debug_p(func_name, 'task result reply_str=', reply_str)

        # return {'kind': 'no_prefix', 'reply_str': reply_str}
        return reply_str

    '''
    FUNCTION_MAP
    '''
    FUNCTION_MAP = {
        '#check_schl': check_school,
        '#add_school_info': add_school_info,
        '#force_add_school_info': force_add_school_info,
        '#parse_trace': parse_trace,
        '#grab_seat': grab_seat,
        '#modify_opentime': modify_opentime,
        # '#needhelp': needhelp,
        '#query_result': query_result,
        '#realtime': realtime,
        '#query_realtime_result': query_realtime_result,

    }

    # verify_seat, return clssrm_crdnt=[(classroom_name, coordinate), () ... ]
    def verify_seat(lib_seat_ls, user_conf_dict, num_0_value='任意'):
        clssrm_crdnt = []
        for libid, seatnum in lib_seat_ls:
            if int(libid) <= 0:
                seatnum = '0'

            # user_conf_dict['classroom']:[{'classroom_name':classroom_name,'libid':libid, 'path':classroom_path,'seat_map':''}
            # if libid == 0:
            classroom_name, coordinate = num_0_value, '0'
            for classroom in user_conf_dict['classroom']:
                # if int(libid) == 0: classroom_name = "任意"; coordinate = '0'; break
                if int(libid) != 0 and coordinate == '0' and classroom['libid'] == libid.replace('-', ''):
                    classroom_name = classroom['classroom_name']
                    if seatnum == '0':
                        coordinate = '0'
                        break
                    for pre_0 in ['', '0', '00', '000']:
                        coordinate = classroom['seat_map'].get(pre_0 + seatnum, coordinate)
            if libid != '0' and classroom_name == num_0_value:
                # error: libid not found
                return []

            clssrm_crdnt.append((classroom_name, coordinate))

        return clssrm_crdnt


'''
extra help info
'''


class ExtraInfo(object):
    prefix = '\n\nℹ️随机帮助信息ℹ️\n'
    I = {
        # 'help': '强调：wechat_sess_id和serverid是需要自己抓包获取的，不是示例里面的qwertyxxx，请仔细阅读说明\n为了避免id失效，抢座任务请尽量在开抢前的5-30分钟时间段内提交\ngithub:https://github.com/qmppz/igotolibrary',
        # 'administrator_info': '如果出现指令无响应无反馈、添加学校失败、多次任务失败...等等摸不着头脑的问题请联系管理员处理。\nwx: turing_01110101',
    }
    others = ['查看<为了学习>抢座工程的更新进度和即时通知，请看管理员朋友圈。wx: turing_01110101',
              '<为了学习>已经向<我去图书馆>官方反馈了抢座漏洞，官方答复:正在修复中。',
              'wechat_sess_id、serverid是需要自己去抓包获取的，不是示例里面的qwertyxxxx，具体获取方法请看指令帮助文档',
              '指令分隔符可以是逗号或句号或分号或空格或回车，。；,.; 且支持中文符号和英文符号。',
              '<为了学习>工程抢座原理已经开源，且无收费的服务、不买卖程序!只为非计算机的同学提供近似公平的抢座。',
              '服务器已经升级，抢座task实际测试速度提升明显。',
              '服务器指令解析需要时间，请等待几秒钟。',
              '有什么意见或者建议请向管理员反馈。',
              '指令中的[学校简称]是英文简称，而不是学校名字的首拼。'
              '为避免抓包获取的serverid失效以及抢座任务遗漏，请在开抢前5-30分钟时间段提交抢座任务。',
              '如果出现指令无响应无反馈、添加学校失败、多次任务失败...等等摸不着头脑的问题请联系管理员。',
              '注意不要把抓包获取到的trace发到<我去图书馆>...请认准<为了学习>',
              '后台消息过多，反馈问题或者建议意见请发送到管理员的微信 turing_01110101',
              '抓包的意思就是进行网络监听并将请求的数据记录显示出来，所以开启抓包软件的时候手机会有风险提示',
              '使用[添加指令]需要满足:1, 在自身没有预定座位的状态下; 2, 自习室都开放的状态下',
              '自习室数量、开抢时间等不正确请反馈管理员wx:turing_01110101',
              '抢座任务在开抢前5-30分钟时间段内提交才能有效',
              # '接下来尝试更新'

              ]

    # cmd_help = '\n指令帮助文档:https://mp.weixin.qq.com/s/1FVTjlDunfngwMip3TFakA'
    cmd_help = '\n<a href="https://mp.weixin.qq.com/s/8HmS4Ct02ZQIcBYRnhTl9Q"> ☞☞指令帮助文档 </a>'

    # get_random_info
    def get_random_info(whichone=-1):
        info = list(ExtraInfo.I.values()) + ExtraInfo.others
        return ExtraInfo.prefix + random.choice(info) + ExtraInfo.cmd_help


'''
parse msg from wechat handle; verify if is cmd and execute the  cmd`s function
return response
'''
@utils.catch_exception
def handle_msg(userid, content, my_id, LOCAL=False):
    # transfer content from byte to str
    m_content = content
    if isinstance(content, bytes):
        m_content = content.decode(encoding='utf-8')
    func_name = '#handle_msg'
    debug_p('func_name=', func_name, 'userid=', userid, 'content=', content)

    '''
    check if is test, discard test flag
    '''
    if str(m_content[:4].split()[0]).lower() in {'test', '内测', '测试'}:
        m_content = m_content[:4].replace('test', '').replace('内测', '').replace('测试', '') +\
            m_content[4:]
    # else:
    #     # old version entrance function
    #     return old_version_entrance(userid, content, my_id)

    # content is none
    content = m_content
    if not content:
        # return get_reply_msg(str_info=content)
        reply_text = CmdFunction.getico(1) + '\n'
        return reply_text + ExtraInfo.get_random_info()

    # parse, if  command
    cmd_pre_flag = {
        # 'igotolibrary': {'我去图书馆', '来选座'},
        # qiangzuo task
        '#grab_seat': {'抢座', '明日预约', '预约座位', '抢座位', '抢坐', '#抢坐', '抢位置', 'grab_seat', '#抢座', 'qz', '#qz'},
        # realtime greb seat
        '#realtime': {'捡漏', '实时预定', '即时预订', '实时预订', '即时预定', 'jl', 'ssyd', 'jsyd', 'realtime'},
        '#check_schl': {'查询', '#查询', 'cx', '#cx', 'chaxun', '#查询学校', '查询学校'},
        # parse trace
        '#parse_trace': {'jx', '#jx', '解析', '#解析', 'wechatsess_id=', 'get'},
        # status query
        '#add_school_info': {'#添加学校', '添加学校', 'tj', '#tj', '#添加', '添加'},
        # force add school
        '#force_add_school_info': {'强制添加', '强制添加学校', '强制添加学校信息', 'qztj', 'qztjxxxx'},
        # '#needhelp':{'帮助', 'help', 'bz', '帮助信息', '提示'},
        # admin cmd
        '#gengxin': {},
        # modify opentime
        '#modify_opentime': {'修改抢座时间', 'xgqzsj', '修改开抢时间', 'xgkqsj'},
        # query reserve result
        '#query_result': {'查询结果', '结果', 'jg', 'cxjg', '抢座结果', 'qzjg', '查询抢座结果', '查询抢座'},
        # query realtime result
        '#query_realtime_result': {'查询捡漏结果', '捡漏结果', 'jljg', 'cxjljg', 'jlqzjg', 'jl结果', '实时预定结果', '实时预订结果'}

    }
    # formatting split_ch to blank
    frmt_content = re.sub(r'[(（）)，；。;,\.]', ' ', content.replace(u'＃', '')
                          .replace(u'#', '')
                          .replace(u'－', '-').replace(u'➖', '-').replace('- -',  '--')
                          .replace('＝', '=')
                          .replace('\n', CF.USER_CMD_SPLTCH)
                          )
    # del all \n \r and blank
    frmt_content = re.sub(r'\s+', CF.USER_CMD_SPLTCH, frmt_content.strip())

    content = frmt_content
    # judge which kind cmd from index 0
    cmd_ls = content.split(CF.USER_CMD_SPLTCH)
    cmd_kind = ''
    for pre_flag in cmd_pre_flag.keys():
        if cmd_ls[0].lower().replace('#', '').strip() in cmd_pre_flag[pre_flag]:
            cmd_kind = pre_flag
            break
    if not cmd_kind:
        # specify parse trace
        if len(content) > 100 and content.find('wechatSESS_ID') >= 0:  # and content.find('SERVERID') >= 0:
            # parse trace
            cmd_kind = '#parse_trace'
        else:
            # content is not cmd
            no_match_cmd_reply = ['没有匹配到指令...不知道该回应什么',
                                  '没有匹配到指令...反馈问题请联系管理员']
            reply_text = CmdFunction.getico(1) * 3 + random.choice(no_match_cmd_reply) + '\n'
            return reply_text + ExtraInfo.get_random_info()

    # swap wechatSESS_ID and SERVERID to ...;wechatSESS_ID; SERVERID
    # if len(cmd_ls) > 2 and cmd_ls[-1].find('wechatSESS_ID') >= 0 and cmd_ls[-2].find('SERVERID') >= 0:
    #     cmd_ls[-1], cmd_ls[-2] = cmd_ls[-2], cmd_ls[-1]
    #     content = CF.USER_CMD_SPLTCH.join(cmd_ls)

    # print('cmd_ls=', cmd_ls)
    # content is cmd then save cmd log
    a_cmd_log = utils.get_date() + '|from_user=' + userid + '|cmd_kind=' + cmd_kind + '|content=' + content + '\n'
    debug_p('func_name=', func_name, 'cmd_kind=', cmd_kind, 'a_cmd_log=', a_cmd_log)

    # content is cmd then exe cmd function
    reply_text = CmdFunction.FUNCTION_MAP[cmd_kind](userid, content)

    # return reply text
    if reply_text.find('状态') < 0:
        reply_text = reply_text + ExtraInfo.get_random_info() if cmd_kind != '#parse_trace' else reply_text
    return reply_text


'''
test
'''
if __name__ == '__main__':
    LOCAL = utils.LOCAL
    # zl_ls = [
    #     # '#抢座; bjtu; 323;81; 324;80;  d3936289adfff6c3874a2579058ac651|1563028695|1563028690; 12cb1a0ebdb4f4260e4d2527110a2959491c24eccf287d75',
    #     # '#抢座; bbmc; 323;81; 324;80;  d3936289adfff6c3874a2579058ac651|1563028695|1563028690; 12cb1a0ebdb4f4260e4d2527110a2959491c24eccf287d75',
    #     # '#抢座; pku; 323;81; 324;80;  d3936289adfff6c3874a2579058ac651|1563028695|1563028690; 12cb1a0ebdb4f4260e4d2527110a2959491c24eccf287d75',
    #     #  '查询；bbmc',
    #
    #     # '添加；hbucm; wechatSESS_ID=5c4b33b34a20e0e0fea9864a253bd3575dcf545689ce9c0e SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1565443472|1565443470'
    #
    #     # '＃xgqzsj, bjtu,21:22'
    #     'jl, bjtu, 323, 7,  324  77 ' + \
    #     # 'tj, bjtu ' + \
    #     'wechatSESS_ID=26443f7ddc48027297ce0e4330308d17f4b7d624aff7b416 ' + \
    #     'SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1570237808|1570237801   ' + \
    #     '-- t=07:00. 平台=lxz; 今明=明'
    #
    #     # 'cxqwejg,'
    #     ]

    for i in range(1, 2):
        # zl = random.choice(['捡漏', '实时预定', '即时预订', '实时预订', '即时预定', 'jl', 'ssyd', 'jsyd', 'realtime',
        #                     '抢座', '抢座位', '抢坐', '#抢坐', '抢位置', 'grab_seat', '#抢座', 'qz', '#qz']) + \
        #     ' bjtu ' + \
        #     ' ' + random.choice(['323 ', '324 ']) + random.choice([str(_) for _ in range(1, 100)]) + \
        #     ' ' + random.choice(['323 ', '324 ']) + random.choice([str(_) for _ in range(1, 100)]) + \
        #     ' wechatSESS_ID=ssid'+random.choice([str(_) for _ in range(111, 999)]) + \
        #     ' SERVERID=serid|1231232321|1321234' + random.choice([str(_) for _ in range(111, 999)]) + \
        #     ' -- ' + \
        #     random.choice(['开抢时间', '时间', 't', 'T', 'time'])+'' \
        #         '='+str(random.randint(6,23))+':'+str(random.randint(0,59))+':'+str(random.randint(0,59))+' ' + \
        #     random.choice(['预约模式', '今明', '哪天', '模式'])+'='+random.choice(['pre', '明', '明天','today', '今', '今天']) + ' ' + \
        #     random.choice(['平台', '公众号'])+'='+random.choice(['我去图书馆', 'igtl', 'wqtsg','来选座', 'lxz']) + ' '

        zl = 'jl;bjtu;323;1 323 0  ,,;;' \
             'SERVERID=d3936289adfff6c3874a2579058ac651|1570612694|1570612692 ' \
             'wechatSESS_ID=5ef6f21dde35722c92e4595b2100b6fef8f08f50adfe6cb3;' \
             ' -- 时间=12:00;模式=明;平台=我去图书馆'
        zl = '抢座;ycgxy;1234;355;' \
             'wechatSESS_ID=672c5459adb7c20f3a3f64e677dfdfebac2455b49c34e280;SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1570632661|1570631371' \
             ';—-;时间=6:00;模式=明;平台=我去图书馆'

        zl = '捡漏, bjtu,0,0 wechatSESS_ID=14a69992ca6af9a2e11b4c3ba270a752a6d28a49fc116272'
        zl = '#抢座; bjtu; 0; 046; 0; 045; ' \
             'wechatSESS_ID=d251fce0daa72515a1d71eefb5b55debc1cbae9d1a32d721; ' \
             'SERVERID=d3936289adfff6c3874a2579058ac651|1570707938|1570707927 ' \
             '-- t=17:20 模式=今'


        zl = 'test 捡漏,    tyut,  323, 0,   324,0,    wechatSESS_ID=0db7db1b5250d65e4d1c2af0a707296c0f689afc5f901273  SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1570926044|1570924907 --  时间=08:40, 模式=今天'
        #
        # zl = '添加学校;sxau;wechatSESS_ID=65dece8f05041ee8c849e5ec5c622a14 -- pt=lxz'
        # 'SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1570237808|1570237801   ' + \
        # ' SERVERID=d3936289adfff6c3874a2579058ac651|1570237808|1570237801   ' + \

        # zl = '添加；    ycgxy;        wechat_sess_id=672c5459adb7c20f3a3f64e677dfdfebac2455b49c34e280;'

        # zl = '抢座；bjtu；324；10；323；85；SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1570448431|1570448430；wechatSESS_ID=65bf8d12c374bf3b1fc466a279bd5ba04f2d9fe375ee717f;'

        # zl = '#jl; tyut; 311; 100; 313; 91;' + \
        #      ' wechatSESS_ID=ed024e28d954710784abf2f385eb9ee1d7de4c53bfdfd898; SERVERID=d3936289adfff6c3874a2579058ac651|1570400154|1570400153;' +\
        # '-- t=07:00 平台=wqtsg; 今明=j'
        # zl = 'jljg'

        # zl = '''
        # GET /index.php/url/auth.html?r=%2Findex.php%2Freserve%2Findex.html%3Ff%3Dwechat%26n%3D5d9bd23e7dc9a&code=081elvY90k3kSy1WSDW90ZsgY90elvY6&state=1 HTTP/1.1 Host: wechat.laixuanzuo.com Connection: keep-alive Upgrade-Insecure-Requests: 1 User-Agent: Mozilla/5.0 (Linux; Android 7.0; PRO 7 Plus Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044904 Mobile Safari/537.36 MMWEBID/4071 MicroMessenger/7.0.7.1521(0x27000736) Process/tools NetType/4G Language/zh_CN Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,image/wxpic,image/sharpp,image/apng,image/tpg,*/*;q=0.8 Accept-Encoding: gzip, deflate, br Accept-Language: zh-CN,en-US;q=0.9 Cookie: FROM_TYPE=weixin; Hm_lvt_7838cef374eb966ae9ff502c68d6f098=1570464181; Hm_lpvt_7838cef374eb966ae9ff502c68d6f098=1570489433; wechatSESS_ID=85807fb3863be66e8b868e4dfce18da0
        # '''

        # zl = 'test 捡漏 sxau;    10281, 0;      0,0;    wechatSESS_ID=89040c2998084ed651a8a7991ce11264 -- 时间=21:40 模式=今天 平台=来选座'
        # zl = 'test tj sxau;    wechatSESS_ID=89040c2998084ed651a8a7991ce11264 -- 时间=21:40 模式=今天 平台=来选座'
        # zl = 'test  jl, bjtu 323, 0, 323, 1 wechatSESS_ID=de2e1d47c50c59709ebb5ee102ea6f738092499495a61e5e  SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1572577791|1572577787 -- 模式=今天'
        zl = 'test  tj, sxau  wechatSESS_ID=0d9a58a026826c2f6aebb2d3926eb01d -- 平台=来选座'
        # zl = 'test cx, wnsfxy'
        # zl = 'test  jl,wnsfxy,  10110, 0, 0 ,0, wechatSESS_ID=35ed243f92be7b748a21d53cce7179b9 -- 平台=来选座 模式=今天'
        zl = 'test jl；sxau；10238；086；10238；004；wechatSESS_ID=0d9a58a026826c2f6aebb2d3926eb01d -- 平台=来选座'
        res = handle_msg(userid='userid_test_' + str(i), content=zl, my_id='my_id_' + str(i), LOCAL=LOCAL)

    mc.client_close()

    debug_p('complete!\n', res)
