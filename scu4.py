from time import sleep

from urllib import request
from urllib import parse
from urllib import error
import json

import http.cookiejar
import re
import sys

checkResultAttempt = 500
postSelectAttempt = 200

proxy = {
    # 'http':'http://127.0.0.1:8888'
}

login_url = "http://zhjw.scu.edu.cn/login/j_spring_security_check"
query_url = "http://zhjw.scu.edu.cn/student/courseSelect/freeCourse/courseList"
token_url = "http://zhjw.scu.edu.cn/student/courseSelect/courseSelect/index"
postToken_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/checkInputCodeAndSubmit"
captcha_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/getYzmPic?time=233"
select_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourses/waitingfor"
result_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectResult/query"

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"

token_key = r"""<input type="hidden" id="tokenValue" value=".+"\/>"""
kcNum_key = "kcNum = \".+\""
redisKey_Key = "redisKey = \".+\""

headers = {
    'User-Agent': user_agent,
    'Referer': 'http://zhjw.scu.edu.cn/student/courseSelect/courseSelect/index'
}

login_data = {
    'j_username': '2018141451134',
    'j_password': '140502Xyan',
    'j_captcha': 'error',
}

wantSelect = []

# For test
wantSelect.append({
    "kch": "999005030",
    "kxh": "04",
    "kcm": "中华文化（历史篇）",
    "zxjxjhh": "2019-2020-1-1",
})


def printResponse(someStrangeResponse):
    content = someStrangeResponse.read().decode('utf-8')
    print(content)


# Convert select data to post

def convertSelectData(wantSelect):
    temp_kcIds = []
    temp_kcms = []
    for course in wantSelect:
        temp_kcIds.append(course['kch'] + '_' + course['kxh'] + '_' + course['zxjxjhh'])
        temp_kcms.append(course['kcm'] + '_' + course['kxh'])
    kcIds = ','.join(temp_kcIds)
    t_kcms = ','.join(temp_kcms)
    kcms = ''
    for x in t_kcms:
        kcms += str(ord(x)) + ','
    return {
        'kcIds': kcIds,
        'kcms': kcms
    }


# Check select result (need processed result data)

def checkResult(result_data):
    success = False

    try:
        result_data_parsed = parse.urlencode(result_data).encode('utf-8')
        resultRequest = request.Request(result_url, result_data_parsed, headers=headers)

        for i in range(1, checkResultAttempt):
            resultResponse = opener.open(resultRequest)
            result = json.loads(resultResponse.read().decode('utf-8'))
            print(result)
            if result['isFinish'] == True:
                #     print("Success select or you've alredy selected")
                #     success = True
                # if (result['isFinish'].find("成功") != -1):
                break
            # else:
            #     print("Error")
    except:
        print("Error get result page")

    return False


def getResultData(selectResponse):
    success = False
    result_data = {}

    try:
        selectContent = selectResponse.read().decode('utf-8')
    except:
        return result_data, success

    kcNum_pattern = re.compile(kcNum_key)
    redisKey_pattern = re.compile(redisKey_Key)

    try:
        result_data['kcNum'] = kcNum_pattern.findall(selectContent)[0][9:10]
        result_data['redisKey'] = redisKey_pattern.findall(selectContent)[0][12:26]
        success = True
        print(result_data)
    except:
        print("Getting Result Key Error")

    return result_data, success


def postSelect(select_data):  # select_data 字典
    # Post!

    select_data_parsed = parse.urlencode(select_data).encode('utf-8')
    selectRequest = request.Request(select_url, select_data_parsed, headers=headers)
    selectResponse = opener.open(selectRequest)

    # printResponse(selectResponse)

    return selectResponse


def getSelectData(wantSelect):
    select_data = {
        'dealType': '5',
        'kcIds': '',
        'kcms': '',
        'fajhh': '4263',
        'sj': '0_0',
        'kclbdm': ''
    }

    # Get data ready

    data = convertSelectData(wantSelect)
    select_data['kcIds'] = data['kcIds']
    select_data['kcms'] = data['kcms']

    return select_data, True  # select_data 字典


def getToken():
    req = request.Request(token_url, headers=headers)
    rep = opener.open(req)

    re1q = request.Request(captcha_url, headers=headers)
    re1p = opener.open(re1q)

    token_pattern = re.compile(token_key)

    token_rep = rep.read().decode("utf-8")

    try:
        token = token_pattern.findall(token_rep)[0][44:76]
        print(token)
    except:
        print("Get token error")

    return token


def postToken(token, wantSelect):
    select_data = {
        'dealType': '5',
        'kcIds': '',
        'kcms': '',
        'fajhh': '4263',
        'sj': '0_0',
        'kclbdm': '',
        'inputCode': '',
        'tokenValue': ''
    }

    select_data['tokenValue'] = str(token)

    # Get data ready

    data = convertSelectData(wantSelect)
    select_data['kcIds'] = data['kcIds']
    select_data['kcms'] = data['kcms']

    select_data_parsed = parse.urlencode(select_data).encode('utf-8')
    selectRequest = request.Request(postToken_url, select_data_parsed, headers=headers)
    selectResponse = opener.open(selectRequest)

    print(select_data)

    printResponse(selectResponse)


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

print("Logging...")

try:
    loginResponse = opener.open(loginRequest)
    print("Logging successfully")
except error.HTTPError as e:
    print("Wrong Username or Password")
    exit()

for i in range(1, postSelectAttempt):  # 选课循环
    print(str(i) + " attempts...")
    selectData, success = getSelectData(wantSelect)  # 获取
    token = getToken()
    postToken(token, wantSelect)  # 验证码不能为空在这里出现
    if not success:
        print("Getting token error")
        continue
    # print(str(i)+" attempts post...")
    try:
        selectResponse = postSelect(selectData)  # Post选课 selectResponse回复
    except error.HTTPError as e:
        print("Failed..." + str(e))
        continue
    result_data, success = getResultData(selectResponse)  # 解析selectResponse
    if not success:
        continue
    print("Checking Result...")
    success = checkResult(result_data)  # 查询选课结果 查询失败将会循环
    if not success:
        continue
    else:
        break
