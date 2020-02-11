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
from aip import AipOcr

import utils, crawldata


debug_p = utils.debug_p

CF = utils.GBCF()
sqlact = utils.SqlAct()
'''
init_start
'''
@utils.catch_exception
def init_start():

    #read global config file
    splt_ch = '|'

    param = {'school_name': '',
             'pre_reserve_time': ''}
    # get comandline param
    if len(sys.argv)-1 != len(param.keys()):
        raise Exception('#param num do not equals to len(param.keys())')
    param['school_name'] = sys.argv[1]
    param['pre_reserve_time'] = sys.argv[2]

    # read today_task list
    file_name = 'clssrm_id_and_today_task.conf'
    file_path = './classroom' + '/' + param['school_name'] + '/' +file_name
    section = 'today_task'
    task_ls = utils.read_conf(file_path, section=section).keys()


    # random or in order
    random_model = False
    if random_model == True:
        random.shuffle(task_ls)
    else:
        # sort
        task_ls.sorted(key=lambda t: int(t.split(splt_ch, 1)[0]), reverse=False)
    debug_p(task_ls)

    for task in task_ls:
        task_param_d = utils.parse_command(task, type='simplify')

        # thread or sequence exe
        # pre reserve a seat

'''
class Reserve
'''
class Reserve(threading.Thread):

    # STATUS = {
    #     'SUCCESS': '😏 😏 恭喜!抢座成功!!!😏 😏',
    #     'FAILED': '😱 😱 很抱歉，抢座失败 😱 😱'
    # }
    #

    # exe trace limit number
    TRACE_LIMIT = 20

    '''
    init
    '''
    def __init__(self, threadID='threadID', thread_name='thread_name', task_info_ls=[]):
        threading.Thread.__init__(self)

        requests.adapters.DEFAULT_RETRIES = 5
        self.sess = requests.Session()
        self.sess.keep_alive = False

        self.threadID = threadID
        self.thread_name = thread_name #task_info_ls[-1]['schl_abbr'] + '_' + task_info_ls[-1]['task_id']

        #
        self.task_info_ls = task_info_ls

        # ATASK
        self.a_task = object()


        # request cnt limit or  random libid/seat num limit
        self.request_num_limit = 3

        # memcache
        self.mc = utils.MyMemcache()

        # trace of this task  from memcache
        self.mc_task_trace = {}

        # self.trace_dct_ls for every (lib, coordinate); type=list  [{'libid': libid, 'clssrm': clssrm, ... },  {}]
        self.trace_dct_ls = []
        # tmp
        self.tmp_trace_dct = {}

        # a task try times limit
        self.try_limit = 10


    '''
    prepare a task, return dict
    '''
    def task_prepare(self, task):

        if self.a_task.platform == CF.PLATFORM['IGTL']:
            self.a_task.M_COOKIES['SERVERID'] = task['serverid'].split('=')[-1]
        self.a_task.M_COOKIES['wechatSESS_ID'] = task['wechat_sess_id'].split('=')[-1]
        task['open_time_ts'] = int(time.mktime(time.strptime(
            utils.get_date(format="%Y-%m-%d ")+task['open_time'], "%Y-%m-%d %H:%M:%S")))

        # task['submit_time'] format is 2019-10-05 19:00:00
        task['task_result'] = 'school:'+task['school_name']+'-'+task['schl_abbr']+'\n'+\
                            'task_id:'+str(task['task_id'])+'\n'+\
                            '任务提交:'+task['submit_time']+'\n\n'
        return task

    '''
    get verify code 
    
    '''
    @utils.catch_exception
    def get_verifycode(self, client=object, imageUrl=''):

        APP_ID = '10690100'
        API_KEY = 'reFMjIqdUT6Q983odq60Qp0M'
        SECRET_KEY = 'aw5DLqn0YpzsuMNNxWYFC21MUdESvfzO'

        options = {}
        options["recognize_granularity"] = "big"
        options["detect_direction"] = "true"

        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        retry_times = 3
        i = 0
        while i < retry_times:
            i += 1
            try:
                # image = get_file_content(tmpImageName)
                image = self.sess.get(imageUrl, proxies=utils.get_proxy(),
                                      headers=self.a_task.M_HEADERS,
                                      cookies=self.a_task.M_COOKIES,
                                      verify=False)
                # open('vc____.jpg', 'wb').write(image.content)
                response = client.numbers(image.content, options)
                debug_p('[get_verifycode] vc_code response=', response)
                # dict: {'log_id': 3705378724129786481, 'direction': 0, 'words_result_num': 1, 'words_result': [{'location': {'width': 78, 'top': 1, 'left': 13, 'height': 37}, 'words': '4217'}]}
                words_result = response['words_result']
                verifycode = words_result[0].get('words', '')
                if not verifycode or len(verifycode) < 4:
                    continue
                if len(verifycode) > 4:
                    verifycode = verifycode[:4]
                debug_p('[get_verifycode] verifycode=', verifycode, 'i=', i)
                return verifycode
            except Exception as e:
                # speed up
                i += 1
                debug_p('[get_verifycode] Exception', 'i=', i, 'traceback=', traceback.format_exc())
                pass
        return '0000'

    '''
    parse response from reserve_a_seat, update self.feedback
    return [status, feedback]
    '''
    def parse_response(self, response):
        emoji_flag = {
            'SUCC': '✅',
            'FAILED': '❌',
            'ITEM': '🔸',
            'ROBOT_FACE': '🤖'
        }
        exception_msg = '【抢座结果解析异常-{except_info},任务很可能失败,请向管理员反馈】'
        exception_code = -1

        if not response:
            feedback = exception_msg.format(except_info='None')
            return [exception_code, feedback]
        if response.status_code != 200:
            feedback = exception_msg.format(except_info=str(response.status_code))
            return [exception_code, feedback]
        try:
            dct_str = json.loads(response.text)
            msg = dct_str.get('msg', '抢座结果解析失败-msg')
            code = dct_str.get('code', exception_code)
            return [code, msg]
        except Exception as e:
            debug_p('[E]: func=parse_response, json.loads(response) filed', traceback.format_exc())
            return [exception_code, exception_msg]

    '''
    get_empty_seat
    return candidate_seat_crdnt , type = list  [(seat_num, coordinate), (), ... ]
    '''
    def get_empty_seat(self, html_seatmap='', number=1, discard_seatnum='0'):
        empty_seat_dct = crawldata.get_seatmap(html_seatmap=html_seatmap, return_empty_seat=True)
        empty_seat_dct.pop(discard_seatnum, 'default_value')
        candidate_seat_crdnt = random.sample(empty_seat_dct.items(), min(number, len(empty_seat_dct)))
        # [(seat_num, coordinate), (), ... ]
        return candidate_seat_crdnt

    '''
    check feedback msg, return True   if task is completed else   False
    completed mean task is done, maybe succ , maybe failed, just completed.
    continue mean failed
    '''
    def check_msg(self, msg):
        key_dct = {
            'completed': {
                '成功',
                '已经预定',
                '验证码',
                '黑名单',
                #
                '名额已满',
            },
            'continue': {
                '不正确',
                '被人预定',
                '不存在',
                '刷新',
                '稍后',
                '名额已满',
            }
        }
        for key in key_dct['continue']:
            if msg.find(key) >= 0:
                # continue
                # return False
                return 'continue'
        else:
            # completed
            # return True
            return 'completed'

    '''
    reserve a seat
    '''
    @utils.catch_exception
    def reserve_a_seat(self, m_libid, m_clssrm, m_seat_num, m_coordinate, all_lib_clssrm, get_hexcodejs_from_url, verify_key, reserve_url_prefix, lib_seat_info):
        # func_name = 'reserve_a_seat' + str('threadid='+str(self.threadID) + ' thread_name='+str(self.thread_name)+' counter='+str(self.counter))
        func_name = '[r_s] thread='+str(self.thread_name)+'|  '
        debug_p(func_name, 'lib_seat_info=', lib_seat_info, 'libid', m_libid,  'coordinate', m_coordinate)

        requests_time_limit = 3
        self.tmp_trace_dct = {}

        # # exec_time
        exec_ts = time.time() + 0.1  # '1564905302.6147149'
        millisecond = str(str(exec_ts).split('.')[-1])[:3]
        t = str(time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime(exec_ts))) + '.' + millisecond
        self.tmp_trace_dct['exe_time'] = t

        # add lib_seat_info
        # self.task_result += lib_seat_info + '\n'
        # self.task_result += '执行:' + self.exe_time + '\n'

        # type = list  [(lib, clssrm), ()...]
        candidate_libid_clssrm = [{}]
        if int(m_libid) > 0:
            candidate_libid_clssrm = [(m_libid, m_clssrm)]
        elif int(m_libid) < 0:
            # all_lib_clssrm  dict{libid: clssrm}
            all_lib_clssrm.pop(m_libid[1:], 'default_value')
            candidate_libid_clssrm = random.sample(all_lib_clssrm.items(), min(self.request_num_limit, len(all_lib_clssrm)))
        else:
            candidate_libid_clssrm = random.sample(all_lib_clssrm.items(), min(self.request_num_limit, len(all_lib_clssrm)))

        debug_p(func_name, '||candidate libid=', candidate_libid_clssrm)

        # candidate_libid_clssrm = [(lib, clssrm), ()...]
        for (libid, clssrm) in candidate_libid_clssrm:

            self.tmp_trace_dct['libid'] = libid
            self.tmp_trace_dct['clssrm'] = clssrm

            if requests_time_limit <= 0:
                break

            ### test
            time.sleep(3)

            # debug_p(func_name, 'get_hexcodejs_from_url=', get_hexcodejs_from_url)
            # entry pre_seatmap_page

            # print('123', self.a_task.M_COOKIES)

            #
            if self.a_task.pattern == "PRE":
                get_hexcodejs_from_url = get_hexcodejs_from_url.format(libid=libid)
            else:
                # TODAY
                get_hexcodejs_from_url = get_hexcodejs_from_url.format(libid=libid, now_time=int(time.time()))

            html_seatmap = utils.get_response(
                url=get_hexcodejs_from_url, sess=self.sess,
                m_headers=self.a_task.M_HEADERS, m_cookies=self.a_task.M_COOKIES,
                verify_key=verify_key, platform=self.a_task.platform)
            # judge html_doc
            if not html_seatmap:
                # sessid invalid--> task completed
                self.tmp_trace_dct['code'] = 404
                self.tmp_trace_dct['msg'] = '尝试进入座位表失败!可能:{不在预约时间, 服务器无响应, id失效}'

                # task failed,  sessionid invalid
                debug_p(func_name, '[E]: pre_seatmap_page is none, get_hexcodejs_from_url='+get_hexcodejs_from_url)
                # info = '结果:{succ_failed}-【{msg}】\n'
                # info = info.format(succ_failed='FAILED',
                #                    msg='未知原因-进入座位表页面失败，请反馈管理员处理...')
                # self.task_result += info
                # sessionid invalid, task completed
                return True #, 'pre_seatmap_page is none, get_hexcodejs_from_url='+get_hexcodejs_from_url

            # get get_empty_seat
            # type = list [(seat_num, coordinate), (), ...]
            candidate_seat_crdnt = []
            if int(libid) > 0 and int(m_seat_num) > 0:
                candidate_seat_crdnt = [(m_seat_num, m_coordinate)]
            elif int(libid) <= 0:
                # assert seat_num==0
                candidate_seat_crdnt = self.get_empty_seat(html_seatmap=html_seatmap, number=1)
            elif int(m_seat_num) <= 0:
                # m_lib > 0 and m_seat_num <= 0 , get three candidate without m_seat_num
                candidate_seat_crdnt = self.get_empty_seat(html_seatmap=html_seatmap, number=self.request_num_limit,
                                                           discard_seatnum=m_seat_num)
            else:
                pass
            if len(candidate_seat_crdnt) == 0:
                # no candidate seat crdnt
                continue
            debug_p(func_name, '||candidate seat=', candidate_seat_crdnt)
            #
            soup = BeautifulSoup(html_seatmap, 'html.parser')

            ### test
            open('lxz_seatmap.html', 'w').write(html_seatmap)

            # debug_p(func_name, '\n\nhtml_doc=', html_seatmap)
            # get hexch_js_code
            # hexch_js_url = [e for e in soup.find_all('script') if
            #        str(e).find('https://static.wechat.v2.traceint.com/template/theme2/cache/layout') >= 0][0]['src']
            debug_p(func_name, 'REG_HEXCODE_URL=', self.a_task.REG_HEXCODE_URL)
            hexch_js_url = soup.find('script', src=re.compile(
                                            self.a_task.REG_HEXCODE_URL)).get('src', '')
            debug_p(func_name, 'hexch_js_url=', hexch_js_url, 'ts=', time.time()-exec_ts+0.1)

            hexch_js_code = requests.get(hexch_js_url, verify=False)
            hexch_js_code.encoding = 'utf8'
            hexch_js_code = hexch_js_code.text

            # insert 'return ...' into hexch_js_code
            # pattern = re.compile(r'(?<=[A-Z]\.ajax_get\().*?(?=,)')
            pattern = re.compile(r'(?<=T\.ajax_get\().*?(?=,)')
            ajax_url = pattern.search(hexch_js_code).group(0).replace('AJAX_URL', reserve_url_prefix)
            debug_p(func_name, 'ajax_url=', ajax_url, 'ts=', time.time()-exec_ts+0.1)
            # hexch_js_code = re.sub(r'[A-Z]\.ajax_get', 'return %s ; T.ajax_get' % ajax_url, hexch_js_code)
            hexch_js_code = re.sub(r'T\.ajax_get', 'return %s ; T.ajax_get' % ajax_url, hexch_js_code)


            #  candidate_seat_crdnt = [(seat_num, coordinate), (), ...]
            for seat_num, cordinate in candidate_seat_crdnt:

                self.tmp_trace_dct['libid'] = libid
                self.tmp_trace_dct['clssrm'] = clssrm
                self.tmp_trace_dct['seat_num'] = seat_num
                self.tmp_trace_dct['cordinate'] = cordinate
                self.tmp_trace_dct['code'] = ''
                self.tmp_trace_dct['msg'] = '没有合适的'

                if requests_time_limit <= 0:
                    break
                ### test
                time.sleep(3)

                # exe hexch_js_code
                tmp = execjs.compile(hexch_js_code)
                http_hexch_seatinfo = tmp.call('reserve_seat', libid, cordinate)
                debug_p(func_name, 'http_hexch_seatinfo=', http_hexch_seatinfo, 'ts=', time.time()-exec_ts+0.1)
                # debug_p(func_name, 'cookies=', self.a_task.M_COOKIES)

                # if need verify code , try times = 1
                try_times_limit = 1
                # check if need  verify code
                vc_code = ''
                while True:
                    time.sleep(3)
                    # reserve a seat
                    requests_time_limit -= 1

                    # exec_time
                    t = time.time() + 0.1  # '1564905302.6147149'
                    millisecond = str(str(t).split('.')[-1])[:3]
                    exe_time = str(time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime(t))) + '.' + millisecond
                    debug_p(func_name, 'request, tmp_trace_dct=', self.tmp_trace_dct)

                    # response = requests.get(http_hexch_seatinfo, proxies=utils.get_proxy(), headers=self.a_task.M_HEADERS, cookies=self.a_task.M_COOKIES, verify=False)
                    response = self.sess.get(http_hexch_seatinfo + vc_code, proxies=utils.get_proxy(),
                                             headers=self.a_task.M_HEADERS, cookies=self.a_task.M_COOKIES,
                                             verify=False)
                    # response.encoding = 'utf8'
                    debug_p(func_name, 'reserve response=', response.text[:300])
                    # type(code) = int
                    code, msg = self.parse_response(response=response)
                    self.tmp_trace_dct['code'] = code
                    self.tmp_trace_dct['msg'] = msg

                    if code != 1000:
                        # self.trace_dct_ls += [{'libid': libid, 'clssrm': clssrm, 'seat_num': seat_num, 'cordinate': cordinate,
                        #                         'exe_time': exe_time, 'code': code, 'msg': msg}]
                        break

                    elif code == 1000 and try_times_limit > 0:
                        try_times_limit -= 1
                        # need vc code
                        vc_code = self.get_verifycode(imageUrl=self.a_task.CURRENT_URL['verifycode_page'])
                        # self.feedback += '验证码为:' + str(vc_code) + '' + '\n'
                        # self.trace_dct_ls[-1]['msg'] += '验证码为:' + str(vc_code) + '' + '\n'
                        # msg += '验证码为:' + str(vc_code) + '' + '\n'
                    else:
                        #
                        break

                # success  or   fialed but completed
                completed_flag = self.check_msg(self.tmp_trace_dct.get('msg', '没有合适的'))

                self.tmp_trace_dct['completed_flag'] = completed_flag

                # deep copy
                self.trace_dct_ls += [dict(self.tmp_trace_dct.items())]
                # refresh
                self.tmp_trace_dct = {}

                # self.trace_dct_ls[-1]['completed_flag'] = int(completed_flag)
                if code == 0 or completed_flag:
                    # completed, task done, discard second candidate seat
                    return True
        # normal done, failed reserve a seat, completed_flag = 'continue'
        # failed and try reserve next candidate seat,
        # if 'seat_num' not in self.tmp_trace_dct:
        self.tmp_trace_dct['clssrm'] = self.tmp_trace_dct.get('clssrm', '没有合适的')
        self.tmp_trace_dct['seat_num'] = self.tmp_trace_dct.get('seat_num', '没有合适的')
        self.tmp_trace_dct['completed_flag'] = self.tmp_trace_dct.get('completed_flag', 'continue')
        # task continue
        return False

    '''
    task_ending:
    handle db and refresh memcache
    '''
    def task_ending(self, task):
        func_name = '[task_ending]'
        none_value = '-'
        succ_failed = 'FAILED' if self.trace_dct_ls[-1].get('code', none_value) != 0 else 'SUCC'


        # '{try_cnt}.{emoji} {exe_time}\n[{classroom_name}]-[{seat_num}]号座位 {feedback}\n'
        # trace_format = CF.TRACE_FORMAT
        try_times = len(self.mc_task_trace['exe_trace']) + 1

        debug_p(func_name, 'trace_dct_ls=', self.trace_dct_ls, ' \ntask=', str(task)[:36])

        # trace_str_ls = []
        # for trace_dct in self.trace_dct_ls:
        #     trace_str_ls += trace_format.format(
        #         try_cnt=try_times, exe_time=trace_dct.get('exe_time', none_value), classroom_name=trace_dct.get('clssrm', none_value),
        #         seat_num=trace_dct.get('seat_num', none_value), feedback=trace_dct.get('msg', none_value),
        #         emoji=['😏 😏 ','😱 😱 '][1 if trace_dct.get('code', none_value) != 0 else 0]
        #     )
        #     try_times += 1

        self.mc_task_trace['exe_trace'] += self.trace_dct_ls
        # limit exe trace number
        if len(self.mc_task_trace['exe_trace']) > Reserve.TRACE_LIMIT:
            self.mc_task_trace['exe_trace'] = [{}] + self.mc_task_trace['exe_trace'][-1*Reserve.TRACE_LIMIT : ]
        # id maybe be replaced by user
        self.mc_task_trace['task_id'] = task['task_id']

        task['succ_failed'] = succ_failed
        task['detail_info'] = json.dumps(self.mc_task_trace)

        if task['task_kind'] == CF.TASK_KIND['reserve']:
            # reserve
            # del task in datebase
            # sqlact.del_task(userid=task['userid'], task_kind=task['task_kind'], wechat_sess_id=task['wechat_sess_id'])
            # add a task into task_result table
            sqlact.add_task_result(task)

        else:
            # realtime
            # check if task is over
            completed_flag = False
            if try_times >= self.try_limit or 'completed' == self.trace_dct_ls[-1].get('completed_flag', 'completed'):
                # completed
                # if
                # def del_task(self, userid, task_kind, wechat_sess_id):
                sqlact.del_task(userid=task['userid'], task_kind=task['task_kind'], wechat_sess_id=task['wechat_sess_id'])
                sqlact.add_task_result(task)
            else:
                # continue
                pass
        # refresh memcache
        key = task['task_kind'] + '_' + task['userid']
        debug_p(func_name, 'refersh memchcae, key=', key)
        self.mc.set_value(key=key, value=self.mc_task_trace)

    '''
    thread run
    '''
    @utils.catch_exception
    def run(self):
        func_name = '[run] ' + str(self.thread_name)
        debug_p(func_name, 'thread start run')

        for task in self.task_info_ls:
            # a task, a a_task

            # debug_p('\n\n### test', task['platform'])
            # exe log for two candidate seat, [{}, {}, ... ]
            self.trace_dct_ls = []
            # discard libid of all_lib_clssrm    if libid in task[] < 0
            all_lib_clssrm = json.loads(task['others_info'])['all_lib_clssrm']
            all_lib_clssrm.pop(task['libid1'] if int(task['libid1']) < 0 else 'default_key', 'default_value')
            all_lib_clssrm.pop(task['libid2'] if int(task['libid2']) < 0 else 'default_key', 'default_value')

            # init task result
            CF.TASK_RESULT['school_name'] = task['school_name']
            CF.TASK_RESULT['schl_abbr'] = task['schl_abbr']
            CF.TASK_RESULT['task_id'] = task['task_id']
            CF.TASK_RESULT['submit_time'] = task['submit_time']

            # get history exe trace, if none then creat a task_result
            if task['task_kind'] == CF.TASK_KIND['realtime']:
                tmp_mc_trace = self.mc.get_value(key=task['task_kind']+'_'+task['userid'], default=CF.TASK_RESULT)
                if task['task_id'] == tmp_mc_trace['task_id']:
                    self.mc_task_trace = tmp_mc_trace
                else:
                    self.mc_task_trace = CF.TASK_RESULT
                debug_p(func_name, 'self.mc_task_trace=', self.mc_task_trace, 'key=', task['task_kind']+'_'+task['userid'])
            else:
                self.mc_task_trace = CF.TASK_RESULT

            # self.task_result = ''
            self.a_task = utils.Atask(platform=task['platform'], pattern=task['pattern'])

            # open_time_ts and cookies
            task = self.task_prepare(task)
            # debug_p(func_name, 'after prepare task=', task)

            # EXE_TRACE = '{try_cnt}.{emoji} {exe_time}\n[{classroom_name}]-[{seat_num}]号座位-{feedback}\n'

            # a task exe info record
            self.exe_time = '00'

            debug_p(func_name, 'task_info=', task)
            # check time if equal open_time then start
            advance_ts = 50
            while int(time.time()*1000) + advance_ts < task['open_time_ts']*1000:
                delay = utils.get_sleep_time(start_time=task['open_time_ts']*1000) / 1000
                debug_p(func_name, 'task-start=' + task['open_time'], 'delay=', delay, 's,', 'threadID=',
                        self.threadID)
                time.sleep(delay)

            # libid in all_lib_clssrm is str;  libid in task is int
            # print('###', task['libid1'], type(task['libid1']))#json.loads(task['others_info'])['all_lib_clssrm'].keys(), type(list(json.loads(task['others_info'])['all_lib_clssrm'].keys())[0]), )

            # first try
            lib_seat_info1 = '候选一:['+str(task['classroom_name1'])+']的['+str(task['seat_num1'])+']号座位:'
            debug_p(func_name, 'try', lib_seat_info1)
            status = self.reserve_a_seat(m_libid=str(task['libid1']), m_seat_num=str(task['seat_num1']),
                                         m_clssrm=task['classroom_name1'], m_coordinate=task['coordinate1'],
                                         all_lib_clssrm=all_lib_clssrm,
                                         get_hexcodejs_from_url=self.a_task.CURRENT_URL['seatmap_page'],
                                         verify_key=self.a_task.VERIFYKEY_OF_SEATMAP,
                                         reserve_url_prefix=self.a_task.CURRENT_URL['reserve_prefix'],
                                         lib_seat_info=lib_seat_info1)
            # if reserve() breakdown(the server no response--> task continue
            if status not in {True, False}:
                self.tmp_trace_dct['code'] = -1
                self.tmp_trace_dct['msg'] = '致命错误, 服务器无响应导致退出'
                self.tmp_trace_dct['completed_flag'] = 'continue'
            # self.tmp_trace_dct not empty
            if self.tmp_trace_dct:
                self.trace_dct_ls += [dict(self.tmp_trace_dct.items())]
                self.tmp_trace_dct = {}
            # time.sleep(5)
            # True mean completed, maybe succ maybe failed
            if status != True and (task['libid1'] != task['libid2'] or task['seat_num1'] != task['seat_num2']):
                ### test
                time.sleep(5)

                # second try
                lib_seat_info2 = '候选二:[' + str(task['classroom_name2']) + ']的[' + str(task['seat_num2']) + ']号座位:'
                # self.task_result += lib_seat_info2
                debug_p(func_name, 'try', lib_seat_info2)
                status = self.reserve_a_seat(m_libid=str(task['libid2']), m_seat_num=str(task['seat_num2']),
                                             m_clssrm=task['classroom_name2'], m_coordinate=task['coordinate2'],
                                             all_lib_clssrm=all_lib_clssrm,
                                             get_hexcodejs_from_url=self.a_task.CURRENT_URL['seatmap_page'],
                                             verify_key=self.a_task.VERIFYKEY_OF_SEATMAP,
                                             reserve_url_prefix=self.a_task.CURRENT_URL['reserve_prefix'],
                                             lib_seat_info=lib_seat_info2)

            # if reserve() breakdown(the server no response--> task continue
            if status not in {True, False}:
                self.tmp_trace_dct['code'] = -1
                self.tmp_trace_dct['msg'] = '致命错误, 服务器无响应导致退出'
                self.tmp_trace_dct['completed_flag'] = 'continue'
            # self.tmp_trace_dct not empty
            if self.tmp_trace_dct:
                self.trace_dct_ls += [dict(self.tmp_trace_dct.items())]
                self.tmp_trace_dct = {}

            # delay
            delaytime = random.randint(8, 20) if task['task_kind'] == CF.TASK_KIND['reserve'] else random.randint(2, 10)/10.0
            debug_p(func_name, 'delaytime=', delaytime)
            time.sleep(delaytime)
            # handle database
            self.task_ending(task)

        # close memcache
        self.mc.client_close()
        debug_p(func_name, 'Done')
        return True

'''
start
'''
if __name__ == '__main__':

    try:
        thread_reserve = Reserve(threadID=1, thread_name='bjtu' + '_' + '10001',
                                         counter=2,
#        # 'qz, bjtu, 323,80,324,81,wechatSESS_ID=4185e7c7e3319057aff90fb8f200c4c27053059385958c25 SERVERID=d3936289adfff6c3874a2579058ac651|1566046348|1566045792'
#wechatSESS_ID=ace8f707fcc11a26490bce8b1c1f4ff922cb4e8d35132c8d
# SERVERID=b9fc7bd86d2eed91b23d7347e0ee995e|1566050853|1566050848

#wechatSESS_ID=b6cd4473f9611ceba357201b54e4cc15654a2c00dccfa708
# SERVERID=d3936289adfff6c3874a2579058ac651|1566307450|1566307447
# "#抢座;      ecut;    1144;   70;  1144;   69;    wechatSESS_ID=4185e7c7e3319057aff90fb8f200c4c27053059385958c25; SERVERID=d3936289adfff6c3874a2579058ac651|1563802927|1563802772"
                                         sessionid='43311c5dcceb6a2fad7d2753e4ec97cf43a96457d3f2d85f',
                                         serverid='d3936289adfff6c3874a2579058ac651|1563621816|1563621727',
                                         libid1='20164', coordinate1='14,24',
                                         libid2='20164', coordinate2='15,19',
                                 userid='userid_test',#task['userid'],
                                 classroom_name1='第一自习室',#task['classroom_name1'],
                                 seat_num1='179',#task['seat_num1'],
                                 classroom_name2='第二自习室',#task['classroom_name2'],
                                 seat_num2='81',#task['seat_num2'],
                                 submit_time='20190817200005',#task['timestamp'],

                                         start_time=int(time.time()*1000)+5*1000, today_or_pre='pre')
        print(thread_reserve.pattern)
        thread_reserve.start()
    except Exception as e:
        debug_p('[E]: action [start] failed, exception is %s' % (repr(e)))
    debug_p('#completed!')


