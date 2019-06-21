from urllib import parse
from urllib import request
import json
from config import *


def course_watch(course_id, opener, course_kxh='-1'):
    from main import watch_logger
    # keyword = parse.quote(course_keyword)  # 编码

    # req = process._request(session, 'POST', 'http://zhjw.scu.edu.cn/student/courseSelect/freeCourse/courseList',
    #                params=post_params, data=None)

    # Request = request.Request(query_url, watch_data_parsed, headers=headers)
    if Course_Type == 'freeCourse':
        post_params = {'searchtj': str(course_id), 'xq': '0', 'jc': '0', 'kclbdm': ''}
        watch_data_parsed = parse.urlencode(post_params).encode('utf-8')
        Request = request.Request(query_url, watch_data_parsed, headers=headers)
    elif Course_Type == 'planCourse':
        post_params = {'kch': str(course_id), 'xq': '0', 'jc': '0', 'kclbdm': '', 'jhxn': str(wantSelect[0]['zxjxjhh'])}
        watch_data_parsed = parse.urlencode(post_params).encode('utf-8')
        Request = request.Request(planCourse_url, watch_data_parsed, headers=headers)
    Response = opener.open(Request)
    req = Response.read().decode('utf-8')
    # watch_logger.info(req)
    dic = json.loads(req)
    if Course_Type == 'freeCourse':
        parser = json.loads(dic['rwRxkZlList'])
    elif Course_Type == 'planCourse':
        parser = json.loads(dic['rwfalist'])
    if len(parser) == 0:
        return 'No Search Results'
    watch_logger.info(str(parser))
    for i in range(len(parser)):
        if parser[i]['bkskyl'] > 0:
            if course_kxh == '-1' or course_kxh == parser[i]['kxh']:
                return parser[i]  # return data example:
            else:
                continue
        # {'bkskrl': 416, 'bkskyl': 0, 'cxjc': '3', 'id': '4077', 'jasm': '水上报告厅', 'jxlm': '一教A座', 'kc
        # h': '999005030', 'kclbdm': '700', 'kclbmc': '人文艺术与中华文化传承', 'kcm': '中华文化（历史篇）', 'k
        # kxqh': '03', 'kkxqm': '江安', 'kkxsh': '106', 'kkxsjc': '历史文化学院（旅游学院）', 'kslxdm': '02', '
        # kslxmc': '考查', 'kxh': '01', 'sflbdm': '', 'sfxzskyz': '', 'sfxzxdlx': '否', 'sfxzxslx': '', 'sfxzxs
        # nj': '', 'sfxzxsxs': '', 'sfxzxxkc': '', 'sjdd': [{'cxjc': '3', 'jasm': '水上报告厅', 'jxlm': '一教A
        # 座', 'skjc': '10', 'skxq': '1', 'skzc': '111111111111111110000000', 'xqm': '江安', 'zcsm': '1-17周'}]
        # , 'skjc': '10', 'skjs': '李晓宇* ', 'skxq': '1', 'skzc': '111111111111111110000000', 'xf': 3, 'xkbz':
        #  '', 'xkkzdm': '01', 'xkkzh': '', 'xkkzsm': '可选可退', 'xkmsdm': '01', 'xkmssm': '直选式', 'xkxzsm':
        #  ';', 'xqm': '江安', 'xs': 48, 'zcsm': '1-17周', 'zxjxjhh': '2019-2020-1-1'}
    return 'No Courses Available'
