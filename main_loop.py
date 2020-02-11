#!/usr/bin/python
# -*- coding: UTF-8 -*-
#@filename: main_loop.py
#@author: wheee/qmppz
#@time:20190710
#@description:   main loop

import os, sys, json, time, traceback, threading
import utils, reserve

debug_p = utils.debug_p
CF = utils.GBCF()
sqlact = utils.SqlAct()

'''
start grab seat py
'''
@utils.catch_exception
def start_grab_thread(thread_cnt, task_info_ls=[], task_kind=CF.TASK_KIND['reserve']):
    # os.system("python  ocr_number.py "+ str(p))
    func_name = '[main_loop.start_grab]'

    thread_name = 'thread_name'
    if task_kind == CF.TASK_KIND['realtime']:
        task_info_list = [task_info_ls]
        task_id_ls = [int(_['task_id']) for _ in task_info_ls]
        thread_name = task_kind + '_' + str(len(task_id_ls)) + '_' + str(min(task_id_ls)) + '_' + str(max(task_id_ls))

    for task in task_info_list:
        try:
            thread_name = task['schl_abbr'] + '_' + str(task['task_id']) if task_kind == CF.TASK_KIND['reserve'] else thread_name
            thread_reserve = reserve.Reserve(threadID=thread_cnt, thread_name=thread_name,
                                             task_info_ls=task)
            thread_reserve.start()
            thread_cnt += 1
            debug_p(func_name, 'threadID=', thread_cnt, 'thread_name=', thread_name)
        except Exception as e:
            debug_p(func_name, 'threadID=', thread_cnt, 'thread_name=', thread_name,
                    'start thread error', repr(e), traceback.format_exc())
            debug_p(func_name, traceback.format_exc())
            continue
    return thread_cnt

'''
check if need dormancy
return millisecond
'''
def check_dormancy(next_awaken=0, dormancy_s_str='01:00:00', dormancy_e_str='05:00:00'):
    func_name = '[mainloop.check_dormancy]'
    # unit is millisecond
    now_time = int(time.time() * 1000)

    # judge if at 02:00-04:00
    delay_time = 0
    today_s_timestamp = int(time.mktime(
        time.strptime(utils.get_date(format='%Y%m%d ') + ' ' + dormancy_s_str, "%Y%m%d %H:%M:%S"))) * 1000
    today_e_timestamp = int(time.mktime(
        time.strptime(utils.get_date(format='%Y%m%d ') + ' ' + dormancy_e_str, "%Y%m%d %H:%M:%S"))) * 1000
    if now_time >= today_s_timestamp and now_time <= today_e_timestamp:
        delay_time = (today_e_timestamp - now_time) / 1000
        sqlact.del_todaytask()
    else:
        delay_time = int(next_awaken - now_time) / 1000
    #
    debug_p(func_name, 'delay=', delay_time)
    time.sleep(delay_time + 1)
    return 0

'''
millisecond
get_next_awaken , 
return millisecond 
'''
def get_next_awaken(offset = 60 * 3, init_time='00:00:30'):
    # unit second
    today_00_00_30_ts = int(time.mktime(time.strptime(utils.get_date(format='%Y%m%d ') + init_time, "%Y%m%d %H:%M:%S")))
    # offset = 60 * 4
    now_ts = int(time.time())
    next_ts = ((now_ts - today_00_00_30_ts)//offset + 1) * offset + today_00_00_30_ts

    # return millisecond
    # debug_p(str(time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime(now_ts))),
    #         str(time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime(next_ts))))
    return next_ts * 1000



'''
main loop
'''
def main_loop():
    func_name = '[main_loop]'
    debug_p(func_name, 'start main loop...')

    # millisecond
    window_len = 60 * 2 * 1000
    # the timestamp of next check time, millisecond
    next_awaken = get_next_awaken()
    # thread_cnt = 0
    thread_cnt = 1

    ### test
    # next_awaken = 0

    while True:
        debug_p()
        # debug_p(func_name, '#'+'<'*10+'check school if meets the requirements')
        debug_p(func_name, '#'+'<'*10+'satrt check', 'thread_cnt=', thread_cnt)
        debug_p('    threading.active_count()=', threading.active_count())
        debug_p('    threading.enumerate()=', threading.enumerate())
        debug_p('    threading.current_thread()=', threading.current_thread())
        debug_p(func_name, '>'*10+'#')
        debug_p()

        #  check_dormancy and delay
        check_dormancy(next_awaken)
        # start_ts = int(time.time() * 1000)
        start_ts = next_awaken
        next_awaken = get_next_awaken()

        # get ready-task  , [{}, {}, ...]
        ready_task_list = sqlact.get_ready_task(start_ts, next_awaken)

        # three part:  normal reserve task,    realtime task of first execute   AND   rest of realtime task
        reserve_task, realtime_fst_task, other_realtime_task = [], [], []
        for task in ready_task_list:
            task['open_time'] = task['open_time'].split('-')[0]
            if task['open_time'].count(':') == 1:
                task['open_time'] += ':00'
            # open_time format is hh:mm:ss
            open_time_ts = int(time.mktime(time.strptime(utils.get_date(format='%Y-%m-%d ') + task['open_time'], "%Y-%m-%d %H:%M:%S")))
            if open_time_ts >= start_ts and open_time_ts < next_awaken:
                if task['task_kind'] == CF.TASK_KIND['reserve']:
                    reserve_task.append(task)
                else:
                    realtime_fst_task.append(task)
            other_realtime_task.append(task)

        if len(reserve_task + realtime_fst_task) > 0:
            thread_cnt = start_grab_thread(thread_cnt, task_info_ls=reserve_task + realtime_fst_task, task_kind=CF.TASK_KIND['reserve'])
            debug_p(func_name, 'start start_grab_thread task_kind=reserve')

        elif len(other_realtime_task) > 0:
            # reserve_task + realtime_fst_task is  empty
            thread_cnt = start_grab_thread(thread_cnt, task_info_ls=other_realtime_task, task_kind=CF.TASK_KIND['realtime'])
            debug_p(func_name, 'start start_grab_thread task_kind=realtime')
        else:
            debug_p(func_name, 'empty task list, sleep until next awaken')
            pass

        ### test
        # break
'''
start test
'''
if __name__ == '__main__':
    try:
        main_loop()
    except Exception as e:
        debug_p('[E]: 致命错误，mainloop 崩溃退出\n', traceback.format_exc())
    print('Done')
    # start_grab(10000)
    # start_grab(1)
'''
'''

    #
    # now_time = int(time.time() * 1000)
    # # judge if at 02:00-03:00
    # today_02_timestamp = int(time.mktime(
    #     time.strptime(utils.get_date(format='%Y%m%d', hms=False) + ' ' + '02:00:00', "%Y%m%d %H:%M:%S"))) * 1000
    # today_03_timestamp = int(time.mktime(
    #     time.strptime(utils.get_date(format='%Y%m%d', hms=False) + ' ' + '12:09:00', "%Y%m%d %H:%M:%S"))) * 1000
    # print('today_02_timestamp=', today_02_timestamp,'today_03_timestamp=',today_03_timestamp,'now=',now_time)
    #
    # if now_time > today_02_timestamp and now_time < today_03_timestamp:
    #     print("ok!")
    # print("complete!")
