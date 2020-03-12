from __future__ import absolute_import

import datetime
import time

import celery
from urllib import error
from celery import task
from .models import courses, jwcAccount
from SCUKiller.jwcAccount import logger
from .utils import CreateNotification
from django.db.models import F
from . import jwcAccount as jwcVal
import SCUKiller.watcher as watcher
from .exceptions import *
from .config import *


class MyTask(celery.Task):
    def __init__(self):
        super().__init__()

    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print("FUCK")  # FOR DEBUG
        # for q in args[0]:  # update会导致QuerySet不可用
        args[0].inq = False
        args[0].save(update_fields=['inq'])


@task(base=MyTask)
def watchList(course):
    try:
        d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:31', '%Y-%m-%d%H:%M')
        d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '21:59', '%Y-%m-%d%H:%M')
        n_time = datetime.datetime.now()
        attempts = 0
        success_cnt = 0
        username = ''
        # print("DEBUG")

        if not d_time < n_time < d_time1:
            raise Exception("Not in Choosing Time!")
        # print(cList)
        username = course.host.user.username
        availCourse = []
        success = ''
        if course.status == '等待中':
            course.status = '运行中'
            course.save()
        jwc = course.host.jwcaccount
        (opener, _) = jwcVal.InitOpener('', jwc.jwcCookie)  # 先不使用代理
        try:  # 在函数内部判断是关键词模式还是指定课程模式
            # 下面进行：检查本地课程状态、Cookie是否失效、教务处账号是否失效
            (availCourse, course.latestRemaining) = watcher.specificWatch(opener, course.keyword, course.kch,
                                                                          course.kxh, course.type,
                                                                          course.term)  # 返回一个可选课程列表

            course.attempts = F('attempts') + 1
            attempts += 1

        except (CookieInvalidException, error.HTTPError) as e:
            try:
                jwc.jwcCookie = str(jwcVal.valjwcAccount(jwc.jwcNumber, jwc.jwcPasswd, course.host.user.username))
                jwc.save()
                CreateNotification(course.host.user.username, "Cookie更新提示",
                                   "在一次监测中发现您的Cookie已经失效，已经成功为您更新Cookie"
                                   "，通常情况下此提醒会出现在您首次添加课程时，请确保在未选中心仪的课程之前不要登录教务处网站！")
                return "Cookie失效"
            except PasswordInvalidException as e:
                logger.error(str(e) + str(jwc.jwcNumber))
                invalidCourses = courses.objects.filter(isSuccess=0, host=course.host)
                invalidCourses.update(isSuccess=-1, status='出错')
                CreateNotification(course.host.user.username, "教务处账号失效提示",
                                   "在一次监测中发现无法登录您的教务处账号，请前去删除您的所有课程并重新绑定教务处账号！")
                return "账号失效"

        except NoSuchCourseException as e:
            logger.error(e)
            CreateNotification(course.host.user.username, "课程信息出错提示",
                               "您提供的课程信息《" + course.kcm + "》由于找不到对应课程（可能是因为已经选择了同类课程），课程已被列入出错课程停止监测。")
            course.status = '出错'
            course.isSuccess = -1
            course.save()

            return str(e)
        except Exception as e:
            logger.error(course.host.user.username + "遇到了未知错误")
            return str(e)

        if availCourse:  # 列表不为空  # TODO(Solved): 多线程时，此处将有多个线程同时不为空，如何实现只post一个 引发的问题：成功后，后一个线程的失败操作，将导致数据库被覆盖为失败
            logger.info("开始拿取最新Cookie...")
            jwc.jwcCookie = str(jwcVal.valjwcAccount(jwc.jwcNumber, jwc.jwcPasswd, course.host.user.username))
            jwc.save()
            (opener, _) = jwcVal.InitOpener('', jwc.jwcCookie)
            # 通过后马上拿最新Cookie 免得被系统logout
            for avail in availCourse:
                _avail = [avail]
                success = watcher.postCourse(opener, _avail)  # 一个一个POST避免冲突，一个成功就break
                if success == 'success':  # 此处逻辑有误，还好一般availCourse不多
                    success_cnt += 1
                    break
            # except Exception as e:
            #     logger.error("二次确认时遇见错误：" + str(e))

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
            logger.info(course.kcm + "没能抢过……")

        elif success == '验证码':
            logger.info("此用户选课出现了验证码，需要随后再试")
            invalidCourses = courses.objects.filter(isSuccess=0, host=course.host)
            invalidCourses.update(isSuccess=-1, status='出错')
            CreateNotification(course.host.user.username, "验证码提示",
                               "在一次抢课中发现您的账号出现了验证码，请您随后再试，目前已将您账号所有课程设为失败。")
        course.save()
        logger.info("Attempts for " + username + " on this watch: " + str(attempts) + " Success Attempts: " + str(success_cnt))
        return "For " + course.kcm + " try one, success: " + str(success_cnt)
    except Exception as err:
        logger.error(err)
    finally:  # 可能的异常：超时、未在指定时间
        course.inq = False
        course.save(update_fields=['inq'])


@task()
def watchUserCourses(request=None):
    print("Watch All Courses Now...")
    courseList = courses.objects.filter(isSuccess=0, inq=False)
    for c in courseList:
        c.inq = True
        c.save(update_fields=['inq'])
        watchList.apply_async(args=(c,), queue='work_queue')

    time.sleep(watchGap)  # Celery最短时间是1秒，这里曲线救国

    courseList = courses.objects.filter(isSuccess=0, inq=False)
    for c in courseList:
        c.inq = True
        c.save(update_fields=['inq'])
        watchList.apply_async(args=(c,), queue='work_queue')
