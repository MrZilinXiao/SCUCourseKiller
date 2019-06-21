import http.cookiejar
import logging
import time
from urllib import error
from urllib import parse
from urllib import request

import keyword_mode
import process
import specific_mode
from config import *


# Initializing Loggers

def get_logger(logger_name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s : %(message)s', "%Y-%m-%d %H:%M:%S")
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(formatter)

    vlog = logging.getLogger(logger_name)
    vlog.setLevel(level)
    vlog.addHandler(fileHandler)
    vlog.addHandler(streamhandler)

    return vlog


select_logfile = 'log/select.log'
watch_logfile = 'log/watch.log'
account_logfile = 'log/account.log'

select_logger = get_logger('select', select_logfile)
watch_logger = get_logger('watch', watch_logfile)
account_logger = get_logger('account', account_logfile)

select_logger.setLevel(logging.DEBUG)
watch_logger.setLevel(logging.DEBUG)
account_logger.setLevel(logging.DEBUG)

if __name__ == '__main__':

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

    account_logger.info("Logging for " + login_data['j_username'])

    try:
        loginResponse = opener.open(loginRequest)
        account_logger.info("Logging successfully for " + login_data['j_username'])
    except error.HTTPError as e:
        account_logger.info(e)
        exit()

    if MODE == 'Keyword':
        token = process.getToken(opener)
        for i in range(1, watchAttempt):
            global course
            course = keyword_mode.course_watch(Course_Keyword, opener)
            if course == 'No Search Results':
                watch_logger.info("No Searching Results, Please Check Your Configuration!")
                exit()
            if course != 'No Courses Available':
                wantSelect.clear()
                wantSelect.append({
                    "kch": course['kch'],
                    "kxh": course['kxh'],
                    "kcm": course['kcm'],
                    "zxjxjhh": course['zxjxjhh'],
                })
                watch_logger.info(
                    "Watching Attempt #" + str(i) + ", Available Course Found! Course Info:" + str(course))
                break
            else:
                watch_logger.info("Watching Attempt #" + str(i) + ", No Matching For " + Course_Keyword)
                time.sleep(watchInterval)
        for j in range(1, postSelectAttempt):
            select_logger.info(
                "Posting Attempt #" + str(j) + ", for " + str(course['kcm']) + ',' + str(course['kch']) + '_' + str(
                    course['kxh']))
            # selectData, success = process.getSelectData(wantSelect)  # 获取
            selectData = process.getSelectData(wantSelect)
            token = process.getToken(opener)
            process.postToken(token, wantSelect, opener)  # 验证码不能为空在这里出现
            # if not success:
            #     print("Getting token error")
            #     continue
            try:
                selectResponse = process.postSelect(selectData, opener)  # Post选课 selectResponse回复
            except error.HTTPError as e:
                select_logger.info("Failed..." + str(e))
                continue
            result_data, success = process.getResultData(selectResponse)  # 解析selectResponse
            if not success:
                continue
            select_logger.info("Checking Result...")
            success = process.checkResult(result_data, opener)  # 查询选课结果 查询失败将会循环
            if success == 'Conflict':
                select_logger.info('Selection Conflicts!' + str(course['kcm']) + ',' + str(course['kch']) + '_' + str(
                    course['kxh']))
                break
            elif success == 'No Available Courses':
                select_logger.info('No Available Courses ' + str(course['kcm']) + ',' + str(course['kch']) + '_' + str(
                    course['kxh']))
                break

            elif not success:
                continue
            else:
                select_logger.info('Select Successful' + str(course['kcm']) + ',' + str(course['kch']) + '_' + str(
                    course['kxh']))
                break

    if MODE == 'Specific':
        token = process.getToken(opener)
        for i in range(1, watchAttempt):
            # global course
            course = specific_mode.course_watch(wantSelect[0]['kch'], opener)
            if course == 'No Search Results':
                watch_logger.info("No Searching Results, Please Check Your Configuration!")
                exit()
            if course != 'No Courses Available':
                # wantSelect.clear()
                # wantSelect.append({
                #     "kch": course['kch'],
                #     "kxh": course['kxh'],
                #     "kcm": course['kcm'],
                #     "zxjxjhh": course['zxjxjhh'],
                # })
                if course['kch'] == wantSelect[0]['kch'] and course['kxh'] == wantSelect[0]['kxh']:
                    watch_logger.info(
                        "Watching Attempt #" + str(i) + ", Available Course Found! Course Info:" + str(course))
                    break
                # else:
                #     print("")
            else:
                watch_logger.info(
                    "Watching Attempt #" + str(i) + ", No Matching For " + wantSelect[0]['kcm'] + wantSelect[0]['kch'])
                time.sleep(watchInterval)

        for j in range(1, postSelectAttempt):
            select_logger.info(
                "Posting Attempt #" + str(j) + ", for " + str(course['kcm']) + ',' + str(course['kch']) + '_' + str(
                    course['kxh']))
            # selectData, success = process.getSelectData(wantSelect)  # 获取
            selectData = process.getSelectData(wantSelect)
            token = process.getToken(opener)
            process.postToken(token, wantSelect, opener)  # 验证码不能为空在这里出现
            # if not success:
            #     print("Getting token error")
            #     continue
            try:
                selectResponse = process.postSelect(selectData, opener)  # Post选课 selectResponse回复
            except error.HTTPError as e:
                select_logger.info("Failed..." + str(e))
                continue
            result_data, success = process.getResultData(selectResponse)  # 解析selectResponse
            if not success:
                continue
            select_logger.info("Checking Result...")
            success = process.checkResult(result_data, opener)  # 查询选课结果 查询失败将会循环
            if success == 'Conflict':
                select_logger.info('Selection Conflicts!' + str(course['kcm']) + ',' + str(course['kch']) + '_' + str(
                    course['kxh']))
                break
            elif success == 'No Available Courses':
                select_logger.info('No Available Courses ' + str(course['kcm']) + ',' + str(course['kch']) + '_' + str(
                    course['kxh']))
                break

            elif not success:
                continue
            else:
                select_logger.info('Select Successful' + str(course['kcm']) + ',' + str(course['kch']) + '_' + str(
                    course['kxh']))
                break
