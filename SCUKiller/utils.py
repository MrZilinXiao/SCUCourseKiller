import datetime

from django.db import transaction

from SCUKiller.send_email import send_html_email
from SCUKiller.jwcAccount import logger
from .config import *
from .models import UserProfile, User, notification as noti, courses
from urllib import parse
from urllib import request
from django.db.models import Q
from . import jwcAccount as jwcVal
import SCUKiller.watcher as watcher
import json
import re

# 这里用事务锁
def watchCourses():
    d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:31', '%Y-%m-%d%H:%M')
    d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '21:59', '%Y-%m-%d%H:%M')
    n_time = datetime.datetime.now()

    if not d_time < n_time < d_time1:
        logger.info("Not in Choosing Time!")
        return
    attempts = 0
    success_cnt = 0
    coursesPending = courses.objects.filter(~Q(isSuccess=1))  # 这里用select for update 会导致锁住所有未成功课程
    for course in coursesPending:
        availCourse = []
        success = ''
        if course.status == '等待中':
            course.status = '运行中'
            course.save()
        if course.isSuccess == -1:  # 跳过异常课程
            continue
        jwc = course.host.jwcaccount
        try:  # 检查Cookie或账号是否失效
            jwcVal.valCookie(jwc.jwcCookie, course.host.user.username)
        except Exception as e:
            print(e, jwc.jwcNumber)
            if str(e) == 'Cookie已经失效！已经更新为最新的Cookie！' or str(
                    e) == "HTTP Error 500: Internal Server Error" or str(
                e) == "HTTP Error 302: Moved Temporarily":
                try:
                    jwc.jwcCookie = str(jwcVal.valjwcAccount(jwc.jwcNumber, jwc.jwcPasswd, course.host.user.username))
                    jwc.save()
                    CreateNotification(course.host.user.username, "Cookie更新提示",
                                       "在一次监测中发现您的Cookie已经失效，已经成功为您更新Cookie，请确保在未选中心仪的课程之前不要登录教务处网站！")
                    continue  # 更新Cookie后此轮不watch 等下一轮
                except Exception as e:
                    logger.error(str(e) + str(jwc.jwcNumber))
                    invalidCourses = course.objects.filter(host=course.host)
                    for item in invalidCourses:
                        item.isSuccess = -1  # 教务处密码错误 此用户所有课程设为异常
                        item.status = '出错'
                        item.save()
                    CreateNotification(course.host.user.username, "教务处账号失效提示",
                                       "在一次监测中发现无法登录您的教务处账号，请前去删除您的所有课程并重新绑定教务处账号！")
                    continue

        (opener, cookie) = jwcVal.InitOpener('', jwc.jwcCookie)  # 先不使用代理
        try:  # 在函数内部判断是关键词模式还是指定课程模式
            availCourse = watcher.specificWatch(opener, course.keyword, course.kch, course.kxh, course.type,
                                                course.term)  # 返回一个可选课程列表
            course.attempts += 1
            attempts += 1
            course.save()
        except Exception as e:
            logger.error(e)
            if str(e) == '找不到提供的课程信息所对应的课程！':  # 找不到是因为已经选择了同类课程
                course.status = '出错'
                course.isSuccess = -1
                course.save()  # TODO: 通知重复，cookie更新后提交 但本次查询结果未变
                CreateNotification(course.host.user.username, "课程信息出错提示",
                                   "您提供的课程信息《" + course.kcm + "》由于找不到对应课程（可能是因为已经选择了同类课程），课程已被列入出错课程停止监测。")
                continue
        if availCourse:  # 列表不为空
            for avail in availCourse:
                _avail = [avail]
                success = watcher.postCourse(opener, _avail)  # 一个一个POST避免冲突，一个成功就break
                if success == 'success':
                    success_cnt += 1
                    break
        if success == 'success':
            course.status = '已完成'
            course.isSuccess = 1
            course.save()
            if course.gid != '':
                courses.objects.filter(gid=course.gid).update(status='已完成', isSuccess=1)
                CreateNotification(course.host.user.username, "课程选择成功",
                                   "系统已经成功选中了您的课程《" + course.kcm + "》，请登录教务处网站核实。由于您是批量添加的课程，当其中一门课程完成后，其他课程将也标记为已完成状态。")
            else:
                CreateNotification(course.host.user.username, "课程选择成功",
                                   "系统已经成功选中了您的课程《" + course.kcm + "》，请登录教务处网站核实。")
        elif success == 'Conflict':
            course.status = '课程冲突'
            course.isSuccess = -1
            course.save()
            CreateNotification(course.host.user.username, "课程冲突提示",
                               "系统在选择您的课程《" + course.kcm + "》时，发生了课程冲突。在课表空余不足时，请尽量使用指定课程模式而非关键字模式。")
        elif success == 'No Available Courses':  # 运气不好，没抢过其他人
            pass

    # return HttpResponse("Attempts on this watch: " + str(attempts) + " Success Attempts: " + str(success_cnt))
    logger.info("Attempts on this watch: " + str(attempts) + " Success Attempts: " + str(success_cnt))


def CreateNotification(username, title, content):
    UserQ = User.objects.get(username=username)
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
