import SCUKiller.utils as utils
from .config import *
from .models import UserProfile, User, notification as noti, courses
import json

from urllib import error, parse, request
from django.db.models import Q
from . import jwcAccount as jwcVal
from .views import CreateNotification


def specificWatch(opener, keyword, kch, kxh, type, term):
    #  根据课程类型构造POST数据
    if type == '自由选课':
        if keyword == '':
            post_params = {'searchtj': kch, 'xq': '0', 'jc': '0', 'kclbdm': ''}
        else:
            post_params = {'searchtj': keyword, 'xq': '0', 'jc': '0', 'kclbdm': ''}
        watch_data_parsed = parse.urlencode(post_params).encode('utf-8')
        Request = request.Request(query_url, watch_data_parsed, headers=headers)
    elif type == '方案选课':
        if keyword == '':
            post_params = {'kch': kch, 'xq': '0', 'jc': '0', 'kclbdm': '', 'jhxn': term}
        else:
            post_params = {'kch': keyword, 'xq': '0', 'jc': '0', 'kclbdm': '', 'jhxn': term}  # TODO:验证POST数据是否正确构造
        watch_data_parsed = parse.urlencode(post_params).encode('utf-8')
        Request = request.Request(planCourse_url, watch_data_parsed, headers=headers)
    Response = opener.open(Request)
    req = Response.read().decode('utf-8')
    dic = json.loads(req)
    selectList = []
    if type == '自由选课':
        parser = json.loads(dic['rwRxkZlList'])
    elif type == '方案选课':
        parser = json.loads(dic['rwfalist'])
    if len(parser) == 0:
        raise Exception("找不到提供的课程信息所对应的课程！")
    for i in range(len(parser)):
        if parser[i]['bkskyl'] > 0:
            if kxh == '' or kxh == parser[i]['kxh']:
                if kch == '' or kch == parser[i]['kch']:
                    selectList.append(parser[i])

    return selectList  # 没有watch到仍有课余量的课程 返回空List

    # 返回数据示例
    # {'bkskrl': 416, 'bkskyl': 0, 'cxjc': '3', 'id': '4077', 'jasm': '水上报告厅', 'jxlm': '一教A座', 'kc
    # h': '999005030', 'kclbdm': '700', 'kclbmc': '人文艺术与中华文化传承', 'kcm': '中华文化（历史篇）', 'k
    # kxqh': '03', 'kkxqm': '江安', 'kkxsh': '106', 'kkxsjc': '历史文化学院（旅游学院）', 'kslxdm': '02', '
    # kslxmc': '考查', 'kxh': '01', 'sflbdm': '', 'sfxzskyz': '', 'sfxzxdlx': '否', 'sfxzxslx': '', 'sfxzxs
    # nj': '', 'sfxzxsxs': '', 'sfxzxxkc': '', 'sjdd': [{'cxjc': '3', 'jasm': '水上报告厅', 'jxlm': '一教A
    # 座', 'skjc': '10', 'skxq': '1', 'skzc': '111111111111111110000000', 'xqm': '江安', 'zcsm': '1-17周'}]
    # , 'skjc': '10', 'skjs': '李晓宇* ', 'skxq': '1', 'skzc': '111111111111111110000000', 'xf': 3, 'xkbz':
    #  '', 'xkkzdm': '01', 'xkkzh': '', 'xkkzsm': '可选可退', 'xkmsdm': '01', 'xkmssm': '直选式', 'xkxzsm':
    #  ';', 'xqm': '江安', 'xs': 48, 'zcsm': '1-17周', 'zxjxjhh': '2019-2020-1-1'}


def postCourse(opener, availCourse):
    for j in range(1, postSelectAttempt):
        # print("Posting Attempt #" + str(j) + ", for " + str(course.kcm) + ',' + str(course.kch) + '_' + str(
        #     course.kxh))
        token = utils.getToken(opener)
        selectData = utils.getSelectData(token,
                                         availCourse)  # TODO: postToken和postSelect 后者带了inputCode和tokenValue 这里进行改动 看看只post一遍是否可行

        # utils.postToken(token, availCourse, opener)  # 验证码不能为空在这里出现，提交了选课信息
        try:
            selectResponse = utils.postSelect(selectData, opener)  # Post选课 selectResponse回复 没带token inputCode
        except error.HTTPError as e:
            print("Failed..." + str(e))
            continue
        result_data, success = utils.getResultData(selectResponse)  # 解析selectResponse
        success = utils.checkResult(result_data, opener)  # 查询选课结果 查询失败将会循环
        if success == 'Conflict' or success == 'No Available Courses':
            break  # 课被抢完了 或者 课程冲突
        elif not success:  # 验证码问题
            continue
        else:  # 成功 success为'success'
            return success

    return success  # 循环完成也返回


def watchCourses():
    coursesPending = courses.objects.filter(~Q(isSuccess=1))
    for course in coursesPending:
        if course.status == '等待中':
            course.status = '运行中'
            course.save()
        if course.isSuccess == -1:  # 跳过异常课程
            continue
        jwc = course.host.jwcHost
        try:  # 检查Cookie或账号是否失效
            jwcVal.valCookie(jwc.jwcCookie, course.host.user.username)
        except Exception as e:
            print(e, jwc.jwcNumber)
            if str(e) == 'Cookie已经失效！已经更新为最新的Cookie！':
                try:
                    jwc.jwcCookie = str(jwcVal.valjwcAccount(jwc.jwcNumber, jwc.jwcPasswd, course.host.user.username))
                    jwc.save()
                    CreateNotification(course.host.user.username, "Cookie更新提示",
                                       "在一次监测中发现您的Cookie已经失效，已经成功为您更新Cookie，请确保在未选中心仪的课程之前不要登录教务处网站！")
                    continue  # 更新Cookie后此轮不watch 等下一轮
                except Exception as e:
                    print(e, jwc.jwcNumber)
                    invaildCourses = course.objects.filter(host=course.host)
                    for item in invaildCourses:
                        item.isSuccess = -1  # 教务处密码错误 此用户所有课程设为异常
                        item.status = '出错'
                        item.save()
                    CreateNotification(course.host.user.username, "教务处账号失效提示",
                                       "在一次监测中发现无法登录您的教务处账号，请前去删除您的所有课程并重新绑定教务处账号！")
                    continue
        (opener, cookie) = jwcVal.InitOpener(course.host.user.username, jwc.jwcCookie)
        try:  # 在函数内部判断是关键词模式还是指定课程模式
            availCourse = specificWatch(opener, course.keyword, course.kch, course.kxh, course.type,
                                        course.term)  # 返回一个可选课程列表
            course.attempts += 1
            course.save()
        except Exception as e:
            print(e)
            if str(e) == '找不到提供的课程信息所对应的课程！':
                course.status = '出错'
                course.isSuccess = -1
                course.save()
                CreateNotification(course.host.user.username, "课程信息出错提示",
                                   "您提供的课程信息《" + course.kcm + "》由于找不到对应课程，课程已被列入出错课程停止监测。")
                continue
        if availCourse:  # 列表不为空
            for avail in availCourse:
                _avail = [avail]
                success = postCourse(opener, _avail)  # 一个一个POST避免冲突，一个成功就break
                if success == 'success':
                    break
        if success == 'success':
            course.status = '已完成'
            course.isSuccess = 1
            course.save()
            CreateNotification(course.host.user.username, "课程选择成功",
                               "系统已经成功选中了您的课程《" + course.kcm + "》，请登录教务处网站核实。")
        elif success == 'Conflict':
            CreateNotification(course.host.user.username, "课程冲突提示",
                               "系统在选择您的课程《" + course.kcm + "》时，发生了课程冲突。在课表空余不足时，请尽量使用指定课程模式而非关键字模式。")
        elif success == 'No Available Courses':  # 运气不好，没抢过其他人
            pass
