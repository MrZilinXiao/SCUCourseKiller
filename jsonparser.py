import json
from urllib import parse

if __name__ == '__main__':

    def _request(session, method, url, params=None, data=None):
        if method not in ['POST', 'GET'] or not session:
            raise ConnectionError

        req = session.request(method, url, params=params, data=data)
        print(req.text + '\n')  # for debug
        return req.text


    def course_watch(session, course_keyword):
        course_keyword = parse.quote(course_keyword)
        post_params = {'searchtj': course_keyword, 'xq': '0', 'jc': '0', 'kclbdm': ''}
        req = _request(session, 'POST', 'http://zhjw.scu.edu.cn/student/courseSelect/freeCourse/courseList',
                       params=post_params, data=None)
        parser = []
        for line in req.readlines():
            dic = json.loads(line)
            parser.append(dic)
        for i in range(len(parser[0])):
            if parser[0][i]['bkskyl'] > 0:
                return parser[0][i]
            else:
                return 'No Courses Available'


    def course_select(session, dealType, course_inf):
        kcIds = course_inf['kch'] + '_' + course_inf['kxh'] + '_' + course_inf['zxjxjhh']
        temp_kcms = course_inf['kcm'] + '_' + course_inf['kxh']
        kcms = ''
        for ch in temp_kcms:
            kcms += str(ord(ch)) + ','
        fajhh = '4386'  # For what use?
        sj = '0_0'
        kclbdm = ''
        inputCode = ''
        tokenValue = ''  # wait to be fixed
        post_params = {'dealType': dealType, 'kcIds': kcIds, 'kcms': kcms, 'fajhh': fajhh, 'sj': sj, 'kclbdm': kclbdm,
                       'inputCode': inputCode, 'tokenValue': tokenValue}

