from django.contrib.auth.models import User

from SCUKiller.send_email import send_html_email
from SCUKiller.jwcAccount import logger
from .config import *
from .models import notification as noti
from urllib import parse
from urllib import request
import json
import re


def CreateNotification(username, title, content):
    UserQ = get(username=username)
    notifi = noti(host=UserQ, title=title, content=content)
    notifi.save()
    EmailAddress = UserQ.email
    send_mail([EmailAddress], title, content)
    print("[%s][%s]%s" % (username, title, content))
    logger.info("[%s][%s]%s" % (username, title, content))


def send_mail(receive_email_addr, title, text):
    """
        发送邮件
        parameter:
            receive_email_addr: 邮箱地址list    ['***@163.com','***@qq.com',...]
    """
    logger.info('************邮件已经加入发送队列*******************')
    send_html_email("[SCUCourseKiller]" + title, text, receive_email_addr)


def getToken(opener):
    req = request.Request(token_url, headers=headers)
    rep = opener.open(req)

    re1q = request.Request(captcha_url, headers=headers)
    re1p = opener.open(re1q)

    token_pattern = re.compile(token_key)

    token_rep = rep.read().decode("utf-8")

    try:
        token = token_pattern.findall(token_rep)[0][44:76]
    except Exception as e:
        print(e)
        print('Getting Token Error')
    return token


def convertSelectData(wantSelect):  # 课程列表转 kcIds 和 kcms
    temp_kcIds = []
    temp_kcms = []
    for course in wantSelect:
        temp_kcIds.append(course['kch'] + '_' + course['kxh'] + '_' + course['zxjxjhh'])
        temp_kcms.append(course['kcm'] + '_' + course['kxh'])
    kcIds = ','.join(temp_kcIds)
    t_kcms = ','.join(temp_kcms)
    kcms = ''
    for ch in t_kcms:
        kcms += str(ord(ch)) + ','
    return {
        'kcIds': kcIds,
        'kcms': kcms
    }


def checkResult(result_data, opener):  # 检查结果界面
    global success
    success = False

    try:
        result_data_parsed = parse.urlencode(result_data).encode('utf-8')
        resultRequest = request.Request(result_url, result_data_parsed, headers=headers)

        for i in range(1, checkResultAttempt):
            resultResponse = opener.open(resultRequest)
            result = json.loads(resultResponse.read().decode('utf-8'))
            print(result)
            if result['isFinish'] == True and result['result'][0].find('成功') != -1:
                #     print("Success select or you've alredy selected")
                #     success = True
                # if (result['isFinish'].find("成功") != -1):
                success = 'success'
                break
            if result['result'][0].find('没有课余量') != -1:
                success = 'No Available Courses'
                break
            if result['result'][0].find('冲突') != -1:
                success = 'Conflict'
            # else:
            #     print("Error")
    except Exception as e:
        print(e)
        print("Error get result page")
    return success


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
    except Exception as e:
        print(e)
        print("Getting Result Key Error")

    return result_data, success


def getSelectData(token, wantSelect):
    select_data = {
        'dealType': '5',
        'kcIds': '',
        'kcms': '',
        'fajhh': '4263',
        'sj': '0_0',
        'kclbdm': '',
        'inputCode': '',
        'tokenValue': str(token)
    }

    # Get data ready

    data = convertSelectData(wantSelect)
    select_data['kcIds'] = data['kcIds']
    select_data['kcms'] = data['kcms']

    return select_data  # select_data 字典


def postSelect(select_data, opener):
    # Post!

    select_data_parsed = parse.urlencode(select_data).encode('utf-8')
    selectRequest = request.Request(select_url, select_data_parsed, headers=headers)
    selectResponse = opener.open(selectRequest)

    # printResponse(selectResponse)

    return selectResponse


def postToken(token, wantSelect, opener):
    select_data = {'dealType': '5', 'kcIds': '', 'kcms': '', 'fajhh': '4263', 'sj': '0_0', 'kclbdm': '',
                   'inputCode': '', 'tokenValue': str(token)}

    # Get data ready

    data = convertSelectData(wantSelect)
    select_data['kcIds'] = data['kcIds']
    select_data['kcms'] = data['kcms']

    select_data_parsed = parse.urlencode(select_data).encode('utf-8')
    selectRequest = request.Request(postToken_url, select_data_parsed, headers=headers)
    selectResponse = opener.open(selectRequest)

    printResponse(selectResponse)


def printResponse(someStrangeResponse):
    content = someStrangeResponse.read().decode('utf-8')
    print(content)


def postSelect(select_data, opener):  # select_data 字典
    # Post!

    select_data_parsed = parse.urlencode(select_data).encode('utf-8')
    selectRequest = request.Request(select_url, select_data_parsed, headers=headers)
    selectResponse = opener.open(selectRequest)

    # printResponse(selectResponse)

    return selectResponse
