from urllib import parse
from urllib import request
import json
from config import *
from main import *
import re
import process

if __name__ == '__main__':
    def course_watch(course_keyword, opener):
        keyword = parse.quote(course_keyword)   # 编码
        post_params = {'searchtj': keyword, 'xq': '0', 'jc': '0', 'kclbdm': ''}
        # req = process._request(session, 'POST', 'http://zhjw.scu.edu.cn/student/courseSelect/freeCourse/courseList',
        #                params=post_params, data=None)
        watch_data_parsed = parse.urlencode(post_params).encode('utf-8')
        Request = request.Request(select_url, watch_data_parsed, headers=headers)
        Response = opener.open(Request)
        #
        req = Response.read().decode('utf-8')
        watching_logger.debug(req)
        parser = []
        for line in req.readlines():
            dic = json.loads(line)
            parser.append(dic)
        for i in range(len(parser[0])):
            if parser[0][i]['bkskyl'] > 0:
                return parser[0][i]   # return data example:
# {'bkskrl': 416, 'bkskyl': 0, 'cxjc': '3', 'id': '4077', 'jasm': '水上报告厅', 'jxlm': '一教A座', 'kc
# h': '999005030', 'kclbdm': '700', 'kclbmc': '人文艺术与中华文化传承', 'kcm': '中华文化（历史篇）', 'k
# kxqh': '03', 'kkxqm': '江安', 'kkxsh': '106', 'kkxsjc': '历史文化学院（旅游学院）', 'kslxdm': '02', '
# kslxmc': '考查', 'kxh': '01', 'sflbdm': '', 'sfxzskyz': '', 'sfxzxdlx': '否', 'sfxzxslx': '', 'sfxzxs
# nj': '', 'sfxzxsxs': '', 'sfxzxxkc': '', 'sjdd': [{'cxjc': '3', 'jasm': '水上报告厅', 'jxlm': '一教A
# 座', 'skjc': '10', 'skxq': '1', 'skzc': '111111111111111110000000', 'xqm': '江安', 'zcsm': '1-17周'}]
# , 'skjc': '10', 'skjs': '李晓宇* ', 'skxq': '1', 'skzc': '111111111111111110000000', 'xf': 3, 'xkbz':
#  '', 'xkkzdm': '01', 'xkkzh': '', 'xkkzsm': '可选可退', 'xkmsdm': '01', 'xkmssm': '直选式', 'xkxzsm':
#  ';', 'xqm': '江安', 'xs': 48, 'zcsm': '1-17周', 'zxjxjhh': '2019-2020-1-1'}
            else:
                return 'No Courses Available'


    # def course_select(session, dealType, course_inf):
    #     kcIds = course_inf['kch'] + '_' + course_inf['kxh'] + '_' + course_inf['zxjxjhh']
    #     temp_kcms = course_inf['kcm'] + '_' + course_inf['kxh']
    #     kcms = ''
    #     for ch in temp_kcms:
    #         kcms += str(ord(ch)) + ','
    #     fajhh = '4386'  # For what use?
    #     sj = '0_0'
    #     kclbdm = ''
    #     inputCode = ''
    #     tokenValue = ''  # wait to be fixed
    #     post_params = {'dealType': dealType, 'kcIds': kcIds, 'kcms': kcms, 'fajhh': fajhh, 'sj': sj, 'kclbdm': kclbdm,
    #                    'inputCode': inputCode, 'tokenValue': tokenValue}
