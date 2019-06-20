from config import *
from urllib import parse
from urllib import request
import json
import re


# def _request(session, method, url, params=None, data=None):
#     if method not in ['POST', 'GET'] or not session:
#         raise ConnectionError
#
#     req = session.request(method, url, params=params, data=data)
#     print(req.text + '\n')  # for debug
#     return req.text


def getToken(opener):
    req = request.Request(token_url, headers=headers)
    rep = opener.open(req)

    re1q = request.Request(captcha_url, headers=headers)
    re1p = opener.open(re1q)

    token_pattern = re.compile(token_key)

    token_rep = rep.read().decode("utf-8")

    try:
        token = token_pattern.findall(token_rep)[0][44:76]
        print('Token:' + str(token))
    except:
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
                success = True
                break
            # else:
            #     print("Error")
    except:
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
        print(result_data)
    except:
        print("Getting Result Key Error")

    return result_data, success


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

    print(select_data)

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
