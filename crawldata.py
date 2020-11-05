# -*- coding: UTF-8 -*-
'''
filename: crawldata.py
user: wheee/qmppz
time: 20190707
description: get seat map
'''

import json, time, re, traceback
from bs4 import BeautifulSoup

import utils
debug_p = utils.debug_p

'''
get open time
format in database is hh:mm:ss
'''
def get_opentime(html_rules):
    """
    Get the rules from the html page

    Args:
        html_rules: (str): write your description
    """
    if not html_rules:
        return ''
    soup = BeautifulSoup(html_rules, 'html.parser')
    td_list = soup.find_all(name='td', attrs={'class':'multi-contents'})
    for td in td_list:
        # 20:10点-23:59点开放
        pattern = re.compile(r'\d{1,2}:\d{1,2}点-\d{1,2}:\d{1,2}点开放')
        time_group = pattern.search(td.get_text().replace(' ', ''))
        if time_group:
            open_time = time_group.group(0).replace('点', '')[:-2]
            # 20:10-23:59 -->  20:10
            open_time = open_time.split('-')[0]
            # 20:10 --> 20:10:00
            if open_time.count(':') == 1:
                open_time += ':00'
            # hh:mm:ss
            return open_time
    # hh:mm:ss
    return '00:00:00'

'''
get user_name and school_name 
'''
def get_name(html_homepage):
    """
    Get user name of the user.

    Args:
        html_homepage: (str): write your description
    """
    if not html_homepage:
        return '', ''
    soup = BeautifulSoup(html_homepage, 'html.parser')
    user_title = soup.find(name='div', attrs={'class': 'user-title'})
    user_name = user_title.contents[0].strip()[3:]
    school_name = user_title.span.get_text().strip()
    # debug_p(user_name,school_name)
    # {'user_name':user_name, 'school_name':school_name}
    return user_name, school_name

'''
get classroom info;
return clssrm:list[dict]
        [{'name':classroom_name,'libid':libid, 'path':classroom_path},{}]
'''
@utils.catch_exception
def get_classroom(html_homepage) -> list :
    """
    Parse classroom. html page.

    Args:
        html_homepage: (str): write your description
    """
    if not html_homepage:
        return []
    clssrm = []
    try:
        soup = BeautifulSoup(html_homepage, 'html.parser')
        # classroom
        list_group = soup.find(name='div', attrs={'class': 'list-group'})
        a_herf_s = list_group.find_all(name='a', attrs={'href': 'javascript:;',
                                                        'data-url': re.compile(r'/index\.php/reserve/layout/libid=\d{1,9}\.html\&\d*')})
        for a in a_herf_s:
            classroom_name = a.h4.contents[0].strip()
            classroom_path = a['data-url'].strip()
            pattern = re.compile(r'(?<=/index\.php/reserve/layout/libid=)\d{1,9}(?=\.html\&\d+)')
            libid = pattern.search(classroom_path).group(0)

            # debug_p(classroom_name, libid, classroom_path)
            clssrm.append({'classroom_name': classroom_name, 'libid': str(libid), 'path': classroom_path})
        return clssrm
    except Exception as e:
        debug_p('[get_classroom] [E]:', traceback.format_exc())
        return []


'''
get seat map from one of clssrm['path']
return seat_map : dict
        seat_map = {seat_num : coordinate, seat_num2 : coordinate2, }

seat_status = {
    # <div class="grid_cell  grid_1" data-key="25,23" style="left:840px;top:910px;">
    'kongxian': 'grid_cell  grid_1',
    
    # <div class="grid_cell  grid_active grid_status3" data-key="25,21" style="left:770px;top:910px;">
    'youren': 'grid_cell  grid_active grid_status3',
    
    'zanli': '',
    
    'jiandu': '',
    
    # <div class="grid_cell grid_2" data-key="6,23" style="left:840px;top:245px;">
    'desk': 'grid_cell grid_2',
    
    # <div class="grid_cell grid_3" data-key="40,7" style="left:280px;top:1435px;">
    'door': 'grid_cell grid_3',
    
}
'''
@utils.catch_exception
def get_seatmap(html_seatmap, return_empty_seat=False) -> dict:
    """
    Return a dictionary of all cells in - placemap

    Args:
        html_seatmap: (str): write your description
        return_empty_seat: (bool): write your description
    """
    # debug_p('html_seatmap=', html_seatmap)
    seat_map = {}
    try:

        soup = BeautifulSoup(html_seatmap, 'html.parser')
        # seat_map
        layout_grid = soup.find(name='div', attrs={'class': 'layout_grid', 'id': 'content-container'})
        if return_empty_seat:
            reg_expression = 'grid_cell[ ]{1,2}grid_1'
            div_grid_cell_s = layout_grid.find_all(name='div', attrs={'class': re.compile(reg_expression)})
        else:
            reg_expression = 'grid_cell.*?'
            div_grid_cell_s = layout_grid.find_all(name='div', attrs={'class': re.compile(reg_expression)})
        # print('layout_grid', div_grid_cell_s)
        # div_grid_cell_s = layout_grid.find_all(name='div', attrs={'class': re.compile(reg_expression)})
        for grid_cell in div_grid_cell_s:
            coordinate = grid_cell['data-key'].strip()
            seat_num = grid_cell.get_text().strip()
            # debug_p(seat_num, coordinate)
            if seat_num:
                # seat_map: {str : str } ; possible get '柱'、'门'
                seat_map[str(seat_num)] = coordinate
        return seat_map
    except Exception as e:
        debug_p('[get_seatmap] [E]:', traceback.format_exc())
        return {}



'''
get and save school info ; include classroom and seatmap
entry homepage if homepage_response is none
parse homepage; entry seatmap_page, and then parse html data
at last, save and return libid_and_name if success else none
'''
@utils.catch_exception
def refresh_school_info(homepage_response='', a_task: utils.Atask = object(),
                        # homepage_response='',
                        sess=object, m_headers={}, m_cookies={},
                        schl_abbr='',
                        sql_conn=object,
                        # tb_schl_lib_stmp = 'schl_lib_stmp',
                        # platform=utils.GBCF.PLATFORM['IGTL'],
                        ) -> dict:
    """
    Refresh the home directory of the library information.

    Args:
        homepage_response: (str): write your description
        a_task: (str): write your description
        utils: (todo): write your description
        Atask: (array): write your description
        object: (todo): write your description
        sess: (todo): write your description
        object: (todo): write your description
        m_headers: (dict): write your description
        m_cookies: (int): write your description
        schl_abbr: (str): write your description
        sql_conn: (todo): write your description
        object: (todo): write your description
    """
    # info_dict for return
    user_conf_dict = {}
    libid_and_name = {}
    # sql_param example : (schl_abbr, schl_nm,open_time, libid, clssrm_nm, seatmap_json)
    sql_param = []

    # get open time
    # usage_rules_url = 'https://wechat.v2.traceint.com/index.php/center/rule.html'
    usage_rules_url = a_task.BASE_URL['rules']
    html_opentime = utils.get_response(url=usage_rules_url, sess=sess, m_headers=m_headers, m_cookies=m_cookies, verify_key='使用规则')

    # utils.debug_p('get_opentime=', html_opentime)

    open_time = get_opentime(html_opentime)
    user_conf_dict['open_time'] = open_time

    # url_host = 'https://wechat.v2.traceint.com'
    # path_homepage = '/index.php/reserve/index.html?f=wechat'
    # if not homepage_url:
    #     homepage_url = url_host + path_homepage
    homepage_url = a_task.BASE_URL['home_page']
    if not homepage_response:
        # homepage_response is none
        homepage_response = utils.get_response(url=homepage_url, sess=sess, m_headers=m_headers, m_cookies=m_cookies, verify_key='')

    # get_name
    user_name, school_name = get_name(homepage_response)
    user_conf_dict['user_name'] = user_name
    user_conf_dict['schl_abbr'] = schl_abbr.lower()
    user_conf_dict['school_name'] = school_name
    # get_classroom clssrm:list[dict{}]   [{'name':classroom_name,'libid':libid, 'path':classroom_path},{}]
    clssrm = get_classroom(homepage_response)
    # entry seat map page
    for i in range(len(clssrm)):
        try:
            time.sleep(0.2)
            # {'name':classroom_name,'libid':libid, 'path':classroom_path}
            cr = clssrm[i]
            libid_and_name[cr['libid']] = cr['classroom_name']
            path_seat_map_page = cr['path']
            # get seat page response
            seat_map_page = utils.get_response(url=a_task.BASE_URL['host'] + path_seat_map_page, sess=sess, m_headers=m_headers, m_cookies=m_cookies)
            if not seat_map_page:
                utils.debug_p('[E]: crawldata.py -> refresh_school_info() -> seat_map_page is none')
                return {}
            # parse, seat_map = {seat_num : coordinate, seat_num2 : coordinate2, }
            seat_map = get_seatmap(seat_map_page)
            if not seat_map:
                # get seat_map failed
                continue
            # cr: {'classroom_name':classroom_name,'libid':libid, 'path':classroom_path} + {seat_map:...}
            cr['seat_map'] = seat_map
            clssrm[i] = cr
            # (platform, schl_abbr, schl_nm, open_time, libid, clssrm_nm, seatmap_json)
            sql_param.append((a_task.platform, schl_abbr, school_name, open_time, int(cr['libid']), cr['classroom_name'], json.dumps(cr['seat_map'])))
        except Exception as e:
            utils.debug_p('refresh_school_info has a seat_map_page error; cr[\'classroom_name\']=', clssrm[i].get('classroom_name', 'null-classroom_name'), traceback.format_exc())

    debug_p('[refresh_school_info]', 'sql_param=', sql_param)
    if len(sql_param) == 0:
        user_conf_dict['classroom'] = []
        return user_conf_dict

    user_conf_dict['classroom'] = clssrm
    # insert/REPLACE into sqlite3
    insert_many_sql = 'REPLACE  INTO ' + utils.SqlAct.tb_schl_lib_stmp + \
                      '(platform, schl_abbr, schl_nm, open_time, libid, clssrm_nm, seatmap_json) ' + \
                      'VALUES(?, ?, ?, ?, ?, ?, ?);'
    cur = sql_conn.cursor()
    cur.executemany(insert_many_sql, sql_param)
    sql_conn.commit()
    #  {user_name:'',schl_abbr:'', school_name:'','open_time':'06:10', classroom:[{'classroom_name':classroom_name,'libid':libid, 'path':classroom_path,'seat_map':''},{},{}...]}
    ## {            ,schl_abbr:'', school_name:'','open_time':'06:10', classroom:[{'classroom_name':classroom_name,'libid':libid,                       'seat_map':''},{},{}...]}
    libid_set = set([str(_[4]) for _ in sql_param])
    user_conf_dict['classroom'] = [_ for _ in user_conf_dict['classroom'] if str(_['libid']) in libid_set]
    return user_conf_dict

'''
test start
'''
if __name__ == '__main__':

    html = open('./i_rules.html').read()
    d = get_opentime(html)
    print(d)