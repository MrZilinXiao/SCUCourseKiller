from log import Log
import process
import time
from config import *

from urllib import request
from urllib import parse
from urllib import error
import keyword_mode

import http.cookiejar
import re

select_logger = Log('select').getlog()
watching_logger = Log('watching').getlog()
account_logger = Log('account').getlog()

# select_logger.setLevel(Log('select').logging.DEBUG)
# watching_logger.setLevel(Log('select').logging.DEBUG)
# account_logger.setLevel(Log('select').logging.DEBUG)

if __name__ == '__main__':
    # Initializing Loggers

    # Create opener which store cookie
    cookie = http.cookiejar.CookieJar()
    cookie_support = request.HTTPCookieProcessor(cookie)
    # For Proxy
    proxy_handler = request.ProxyHandler(proxy)
    opener = request.build_opener(cookie_support, proxy_handler)

    # Login
    opener.open(request.Request("http://zhjw.scu.edu.cn/login", headers=headers))  # Get cookie (Don't know why)
    login_data_parsed = parse.urlencode(login_data).encode("utf-8")
    loginRequest = request.Request(login_url, login_data_parsed, headers=headers)

    print("Logging for " + login_data['j_username'])

    try:
        loginResponse = opener.open(loginRequest)
        print("Logging successfully for " + login_data['j_username'])
    except error.HTTPError as e:
        print("Wrong Username or Password")
        exit()

    if MODE == 'Keyword':
        token = process.getToken(opener)

        for i in range(1, watchAttempt):
            global course
            course = keyword_mode.course_watch(Course_Keyword, opener)
            if course != 'No Courses Available':
                wantSelect.clear()
                wantSelect.append({
                    "kch": course['kch'],
                    "kxh": course['kxh'],
                    "kcm": course['kcm'],
                    "zxjxjhh": course['zxjxjhh'],
                })
                print("Watching Attempt #" + str(i) + ", Available Course Found! Course Info:" + str(course))
                break
            else:
                print("Watching Attempt #" + str(i) + "No Matching For " + Course_Keyword)
                time.sleep(watchInterval)
        for j in range(1, postSelectAttempt):
            print("Posting Attempt #" + str(j) + ", for " + str(course['kcm'])+','+str(course['kch'])+'_'+str(course['kxh']))
            selectData, success = process.getSelectData(wantSelect)  # 获取
            token = process.getToken(opener)
            process.postToken(token, wantSelect, opener)  # 验证码不能为空在这里出现
            if not success:
                print("Getting token error")
                continue
            try:
                selectResponse = process.postSelect(selectData,opener)  # Post选课 selectResponse回复
            except error.HTTPError as e:
                print("Failed..." + str(e))
                continue
            result_data, success = process.getResultData(selectResponse)  # 解析selectResponse
            if not success:
                continue
                print("Checking Result...")
            success = process.checkResult(result_data, opener)  # 查询选课结果 查询失败将会循环
            if not success:
                continue
            else:
                break
