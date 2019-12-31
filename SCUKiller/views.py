# coding=utf-8
import os
import queue
import threading
import time
import re
import json

import requests
from django.db import transaction
from django.views import View

import SCUKiller.pay as pay

from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, QuerySet, F
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt

from . import jwcAccount as jwcVal
from .forms import RegForm, LoginForm, AddCourseForm, AddjwcAccount
from .jwcCourse import courseid2courses
from .models import UserProfile, User, notification as noti, courses, codes, Orders, EmailVerifyRecord
from .models import jwcAccount as jwcModel
from .storeBack import generate_code, utc2local
from .config import *
from .utils import CreateNotification

logger = jwcVal.logger


# Create your views here.
def check_captcha(request):
    import io
    from . import check_captcha as CheckCode
    stream = io.BytesIO()
    # img 图片对象, code 在图像中写的内容
    img, code = CheckCode.create_validate_code()
    img.save(stream, "png")
    # 图片页面中显示, 立即把 session 中的 CheckCode 更改为目前的随机字符串值
    request.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())


def checkUsername(request):
    user_name = request.GET.get('userName')
    if User.objects.filter(username=user_name).exists():
        return HttpResponse(1)
    else:
        return HttpResponse(0)


def checkEmail(request):
    email = request.GET.get('email')
    if User.objects.filter(email=email).exists():
        return HttpResponse(1)
    else:
        return HttpResponse(0)


def page_not_found(request, exception):
    return render(request, '404.html', status=404)


def page_error(request):
    return render(request, '500.html', status=500)


def register(request):
    if request.method == 'GET':
        form = RegForm()
        request.session['login_from'] = request.META.get('HTTP_REFERER',
                                                         '/')
        return render(request, 'register.html', locals())
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            form = RegForm(request.POST)
            errormsg = ''
            if form.is_valid():
                username = form.cleaned_data['userName']
                phoneNumber = form.cleaned_data['phoneNumber']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                captcha = form.cleaned_data['captcha']
                if username != '' and password != '' and captcha == request.session['CheckCode'].lower():
                    if User.objects.filter(username=username).exists():
                        errormsg = '用户名已存在'
                    elif User.objects.filter(email=email).exists():
                        errormsg = '电子邮箱已存在'
                    else:
                        user = User.objects.create_user(username=username, email=email, password=password)
                        userProfile = UserProfile(user=user, telephone=phoneNumber)
                        userProfile.save()
                        user.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, user)

                        CreateNotification(username, "恭喜您！", "您已经成功注册SCUCourseKiller！")
                        return redirect('index')
                elif captcha != request.session['CheckCode'].lower():
                    errormsg = '验证码错误'
                return render(request, 'register.html', locals(), {'form': form})
            else:
                return render(request, 'register.html', {'form': form})
        else:
            return redirect('index')


class ActiveUserView(View):
    """
    验证注册码，并激活用户
    """

    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, '500.html', status=500)
        return render(request, 'login.html', {'errormsg': '激活成功！请重新登录'})


def logIn(request):
    if request.user.is_authenticated:
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if request.method == 'GET':
        form = LoginForm()
        request.session['login_from'] = request.META.get('HTTP_REFERER',
                                                         '/')
        return render(request, 'login.html', locals())
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        errormsg = ''
        if form.is_valid():
            username = form.cleaned_data['userName'].strip()
            password = form.cleaned_data['password']
            captcha = form.cleaned_data['captcha'].strip()
            if username != '' and password != '' and captcha == request.session['CheckCode'].lower():
                user = authenticate(username=username, password=password)
                if user is not None:
                    UserQ = User.objects.get(username=username)
                    # if UserQ.UserProfile.is_active:
                    login(request, user)  # 调用login方法登陆账号
                    logger.info("登录成功！")
                    return redirect(request.session['login_from'])
                    # else:
                    #     errormsg = "用户未激活！"
                elif captcha != request.session['CheckCode'].lower():
                    errormsg = "验证码错误"
                else:
                    errormsg = "用户名或密码错误"
            elif username == '' or password == '':
                errormsg = "用户名或密码不能为空"
            else:
                errormsg = "其他错误"
        return render(request, 'login.html', locals())


@login_required
def logOut(request):
    try:
        logout(request)
    except Exception as e:
        print(e)
    return redirect(request.META['HTTP_REFERER'])


@login_required
def notification(request):
    if request.user.is_authenticated:
        user = request.user
        username = user.username
        UserQ = User.objects.get(username=username)
        notifications = noti.objects.filter(host=user)
        notificationsCnt = len(notifications)
        if request.method == 'GET':
            return render(request, 'notification.html', locals())
        elif request.method == 'POST':
            MarkAsRead(request)
            return redirect('notification')
    else:
        return redirect('login')


@login_required
def index(request):
    if request.user.is_authenticated:
        user = request.user
        username = user.username
        UserQ = User.objects.get(username=username)
        notificationsCnt = len(UserQ.notificationHost.filter(isRead=False))
        isNotified = False
        if notificationsCnt != 0:
            isNotified = True

        return render(request, 'index.html', locals())
    else:
        return redirect('login')


@login_required
def inner_index(request):
    if request.user.is_authenticated:
        # user = request.user
        # username = user.username
        UserQ = User.objects.get(username=request.user.username)
        points = UserQ.UserProfile.points
        courseCnt = UserQ.UserProfile.courseCnt
        courseRemainingCnt = UserQ.UserProfile.courseRemainingCnt
        Courses = courses.objects.filter(host=UserQ.UserProfile).order_by('addTime')[:4]
        return render(request, 'index_v1.html', locals())
    else:
        return redirect('login')


@login_required
def addCourse(request):
    if request.method == 'POST':
        try:
            form = AddCourseForm(request.POST)
            UserQ = User.objects.get(username=request.user.username)
            userprofile = UserQ.UserProfile
            if userprofile.courseRemainingCnt <= 0:
                raise Exception('剩余课程权限不足！')
            try:
                jwcaccount = userprofile.jwcaccount
            except Exception as e:
                print(e)
                jwcaccount = None
            if jwcaccount is None:
                raise Exception('您尚未绑定教务处账号！')
            if form.is_valid():
                UserQ = User.objects.get(username=request.user.username)
                keyword = form.cleaned_data['keyword']
                kch = form.cleaned_data['kch']
                kxh = form.cleaned_data['kxh']
                type = form.cleaned_data['type']
                term = form.cleaned_data['term']
                if type == '1':
                    ctype = "自由选课"
                elif type == '2':
                    ctype = "方案选课"
                else:
                    ctype = "其他选课"
                if kch != '' and kxh != '' and keyword == '':
                    find_same = courses.objects.filter(kch=kch, kxh=kxh)
                    if find_same:
                        for item in find_same:
                            if item.status != '已完成':
                                Courses = UserQ.UserProfile.coursesHost.all()  # 报错还是要列出课程
                                raise Exception("系统中有相同的课程未完成！")
                host = UserQ.UserProfile
                # DONE: 加入课程时验证课程是否存在
                # DONE:如果课程号与课序号都给出则关闭关键词模式
                # DONE: 在前端可视化返回符合要求的课程列表

                # 监控方式归纳
                # 1、纯关键词抢课，不能指定课程号与课序号。（例如抢中华文化）（已实现）
                # 2、单纯指定课程号，不指定课序号与关键词。（如抢不指定节次的课程，可能中途出现与已有课程冲突）（没有必要指定关键词，单一课程号对应单一的课程名）
                # 这里可以扩展为多选框抢指定课程号，人工舍去不符合要求的课程后提交，避免了通过教务处奇怪的命名方式检查是否课程冲突（无聊的时候去扒一下前端如何实现）
                # 3、指定课程号和课序号，需要提前查询好自己课表是否与此课程冲突（这种情况一旦发现冲突系统就应停止监控）

                # 以下是可能的默认值
                kcm = ''
                teacher = ''
                campus = ''
                location = ''
                if kch != '':  # 有无课序号影响的是courseList长度是否为1
                    if keyword != '':
                        raise Exception("已经指定课程号的情况下请将关键词留空！")
                    opener, _ = jwcVal.InitOpener()
                    try:
                        courseList = courseid2courses(opener, '', kch, kxh, term)
                    except Exception as e:
                        logger.error(str(e))
                        print(e)
                        raise Exception(e)
                    # DONE:都给出时需要获取课程名
                    if len(courseList) == 0:
                        raise Exception("由你提供的课程号与课序号无法查找到对应的课程，请检查输入是否正确！")
                    # elif len(courseList) == 1:  # 注意courseList的查询结果是按一周上课节次来的，可能重复
                    #     kcm = courseList[0]['kcm']
                    #     teacher = courseList[0]['skjs']
                    #     campus = courseList[0]['xqm']
                    #     location = courseList[0]['jxlm'] + " " + courseList[0]['jasm']
                    else:
                        if kxh == '':  # 仅课程号进入前端选择模式
                            for i in range(len(courseList) - 1, -1, -1):
                                if i > 0 and courseList[i]['kch'] == courseList[i - 1]['kch'] and courseList[i][
                                    'kxh'] == courseList[i - 1]['kxh']:  # 去除有多节课的单一课程
                                    courseList.pop(i)
                            rows = []
                            for j in range(1, len(courseList) + 1):
                                rows.append({})
                                rows[j - 1]['id'] = j
                                rows[j - 1]['kcm'] = courseList[j - 1]['kcm']
                                rows[j - 1]['kch'] = courseList[j - 1]['kch']
                                rows[j - 1]['kxh'] = courseList[j - 1]['kxh']
                                rows[j - 1]['term'] = courseList[j - 1]['zxjxjhh']
                                rows[j - 1]['teacher'] = courseList[j - 1]['skjs']
                                rows[j - 1]['type'] = ctype
                            request.session["courseList"] = rows
                            raise Exception("请在右侧的课程列表中选择需要监控的课程并提交！")
                        else:  # 整合信息
                            # 下面是给定课程号 课序号的业务逻辑
                            kcm = courseList[0]['kcm']
                            teacher = courseList[0]['skjs']
                            campus = courseList[0]['xqm']
                            for i, c in enumerate(courseList):
                                location += (str(i + 1) + "：" + c['jxlm'] + " " + c['jasm'] + "\n")
                elif keyword != '':
                    if kch != '' or kxh != '':
                        raise Exception("指定关键词时无法指定课程号与课序号！")
                    opener, _ = jwcVal.InitOpener()
                    try:
                        courseList = courseid2courses(opener, keyword, '', '', term)
                    except Exception as e:
                        logger.error(str(e))
                        print(e)
                        raise Exception(e)
                    if len(courseList) == 0:
                        raise Exception("由你提供的课程号与课序号无法查找到对应的课程，请检查输入是否正确！")
                    else:
                        for i in range(len(courseList) - 1, -1, -1):
                            if i > 0 and courseList[i]['kch'] == courseList[i - 1]['kch'] and courseList[i]['kxh'] == \
                                    courseList[i - 1]['kxh']:  # 去除有多节课的单一课程
                                courseList.pop(i)
                        rows = []
                        for j in range(1, len(courseList) + 1):
                            rows.append({})
                            rows[j - 1]['id'] = j
                            rows[j - 1]['kcm'] = courseList[j - 1]['kcm']
                            rows[j - 1]['kch'] = courseList[j - 1]['kch']
                            rows[j - 1]['kxh'] = courseList[j - 1]['kxh']
                            rows[j - 1]['term'] = courseList[j - 1]['zxjxjhh']
                            rows[j - 1]['teacher'] = courseList[j - 1]['skjs']
                            rows[j - 1]['type'] = ctype
                            rows[j - 1]['keyword'] = keyword
                        request.session["courseList"] = rows
                        raise Exception("请在右侧的课程列表中选择需要监控的课程并提交！")
                # 下面是给定课程号 课序号的业务逻辑 其他业务逻辑全部放到except中作为异常

                # UserQ.UserProfile.courseRemainingCnt -= 1  # TODO: 验证减1不生效的逻辑 Solved Solution: F() 看看是否有效
                # UserQ.UserProfile.courseCnt += 1
                UserQ.UserProfile.courseRemainingCnt = F('courseRemainingCnt') - 1
                UserQ.UserProfile.courseCnt = F('courseCnt') + 1
                UserQ.UserProfile.save()

                course = courses(kch=kch, kxh=kxh, kcm=kcm, keyword=keyword, host=host, type=ctype, term=term,
                                 teacher=teacher, campus=campus, location=location)
                course.save()
                Courses = UserQ.UserProfile.coursesHost.all()
                CreateNotification(username=request.user.username, title="课程添加成功",
                                   content="您已经成功添加课程号为" + str(kch) + "，课序号为" + str(kxh) + "的课程《" + kcm + "》！")
                notice = '课程添加成功！'
            else:
                notice = '提交的课程信息不合法！'
        except Exception as e:
            notice = str(e)
        return render(request, 'courseManagement.html', locals())


@login_required
def jwcAccount(request):
    print("Adding Jwc Account")
    if request.user.is_authenticated:
        if request.method == 'GET':
            UserQ = User.objects.get(username=request.user.username)
            # get返回单对象 反向查询需要try 当找不到或找到多个时报错
            # filter返回QuerySet，直接if判断是否为空
            userprofile = UserQ.UserProfile
            try:
                jwcaccount = userprofile.jwcaccount
            except Exception as e:
                print(e)
                jwcaccount = None
            if jwcaccount is None:  # 尚未绑定教务处账号
                form = AddjwcAccount(request.POST)
                return render(request, 'bindjwcAccount.html', locals())
            else:  # 已绑定教务处账号
                return render(request, 'jwcAccount.html', locals())
        elif request.method == 'POST':
            form = AddjwcAccount(request.POST)
            if form.is_valid():
                try:
                    stuID = form.cleaned_data["stuID"].strip()
                    stuPass = form.cleaned_data["stuPass"].strip()
                    if len(stuID) != 13:
                        raise Exception("学号不足13位！")
                    stuQuery = jwcModel.objects.filter(jwcNumber=stuID)
                    if stuQuery:
                        raise Exception("学号已存在！")
                    try:
                        cookie_dict = jwcVal.valjwcAccount(stuID, stuPass)  # 没有添加教务处账户之前先不用代理
                        user = User.objects.get(username=request.user.username)
                        jwc = jwcModel(jwcNumber=stuID, jwcPasswd=stuPass, userprofile=user.UserProfile,
                                       jwcCookie=str(cookie_dict))
                        jwc.save()
                        CreateNotification(username=request.user.username, title="教务处账号绑定成功",
                                           content="您已经成功绑定学号为" + str(stuID) + "的教务处账号！（每个学号只能享受一个体验课程量！）")
                        return redirect('jwcAccount')
                    except Exception as e:
                        errormsg = "学号或密码错误！"
                except Exception as e:
                    errormsg = e
                return render(request, 'bindjwcAccount.html', locals())
            else:
                errormsg = "表单验证未通过！"
                return render(request, 'bindjwcAccount.html', {'form': form, 'errormsg': errormsg})  # 表单clean验证未通过
    else:
        return redirect('login')


@login_required
def checkCookie(request):
    if request.method == 'POST':
        checkNumber = request.POST.get('delNumber')
        jwcaccount = jwcModel.objects.get(jwcNumber=checkNumber)
        try:
            if not jwcaccount:
                raise Exception("查询的学号不存在！")
            if request.user.username != jwcaccount.userprofile.user.username:
                raise Exception("你欲验证的学号不属于你！")
            cookieStr = jwcaccount.jwcCookie
            try:
                valid = jwcVal.valCookie(cookieStr, request.user.username)
                errormsg = "Cookie有效！"
            except Exception as e:
                errormsg = e  # HTTP Error 500（Invaild Session) 或者 HTTP Error 302: Moved Temporarily
        except Exception as e:
            errormsg = e  # 恶意请求 或 Cookie Invaild Session
        if str(errormsg) == "Cookie已经失效！已经更新为最新的Cookie！" or str(
                errormsg) == "HTTP Error 500: Internal Server Error" or str(
            errormsg) == "HTTP Error 302: Moved Temporarily":
            try:
                jwcaccount.jwcCookie = str(
                    jwcVal.valjwcAccount(jwcaccount.jwcNumber, jwcaccount.jwcPasswd,
                                         request.user.username))  # 可能遇见：1.密码已被修改 需要抛出密码错误 2.用账密登陆时的未知错误
                jwcaccount.save()
                errormsg = "Cookie已经失效！已经更新为最新的Cookie！"
                jwcaccount = jwcModel.objects.get(jwcNumber=checkNumber)
            except Exception as e:
                errormsg = str(e)
        return render(request, "jwcAccount.html", locals())


@login_required
@transaction.atomic
def courseManagement(request):
    if request.user.is_authenticated:
        UserQ = User.objects.get(username=request.user.username)
        UserP = UserQ.UserProfile
        form = AddCourseForm()
        cidDel = request.GET.get("del")
        notice = ''
        if cidDel is not None:
            CourseQ = courses.objects.get(cid=cidDel)
            if CourseQ.gid != '':  # 按分组添加的课程
                delCourses = courses.objects.filter(gid=CourseQ.gid)
                with transaction.atomic():
                    delCourses.delete()  # 数据变化时，本事务会回滚 https://www.jianshu.com/p/5150010a08c5
                # TODO: 解决删除回滚 Solution: transaction.atomic()
                notice = "课程《" + CourseQ.kcm + "》已被成功删除，与其一起添加的课程也被成功删除。"
            else:
                with transaction.atomic():
                    CourseQ.delete()
                notice = "课程《" + CourseQ.kcm + "》已被成功删除"
            if CourseQ.status != 1:
                UserP.courseRemainingCnt = F("courseRemainingCnt") + 1  # #TODO:删除非成功课程时课程量有问题
                UserP.save()
            CreateNotification(username=request.user.username, title="课程删除成功",
                               content=notice)
            Courses = UserQ.UserProfile.coursesHost.all()
            UserQ.UserProfile.courseCnt = len(Courses)
            UserQ.UserProfile.save()
            return render(request, 'courseManagement.html', locals())
        Courses = UserQ.UserProfile.coursesHost.all()
        return render(request, 'courseManagement.html', locals())
    else:
        return redirect('login')


def deljwcAccount(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            delNumber = request.POST.get('delNumber')
            jwcaccount = jwcModel.objects.get(jwcNumber=delNumber)
            try:
                if not jwcaccount:
                    raise Exception("删除的学号不存在！")
                if request.user.username != jwcaccount.userprofile.user.username:
                    raise Exception("你欲删除的学号不属于你！")
                UserQ = User.objects.get(username=request.user.username)
                remainingCourses = courses.objects.filter(host=UserQ.UserProfile)
                remainingCourses = remainingCourses.filter(~Q(isSuccess=1))
                if remainingCourses:
                    raise Exception("你还有未完成的课程！")
                jwcaccount.delete()
                CreateNotification(username=request.user.username, title="教务处账号解绑成功",
                                   content="您已经成功解绑学号为" + str(delNumber) + "的教务处账号！")
                errormsg = "解绑成功！"
                form = AddjwcAccount()
                return render(request, 'bindjwcAccount.html', locals())
            except Exception as e:
                errormsg = e
                return render(request, 'jwcAccount.html', locals())
    else:
        return redirect('login')


@login_required
def alterUserinfo(request):
    if request.method == 'GET':
        username = request.user.username
        return render(request, 'AlterUserinfo.html', locals())
    elif request.is_ajax:
        res = {'status': None, 'msg': None}
        name = request.POST.get('name')
        npwd = request.POST.get('npwd')
        opwd = request.POST.get('opwd')
        repwd = request.POST.get('re_pwd')
        user = authenticate(request, username=name, password=opwd)
        if user:
            if npwd == repwd:
                logout(request)
                user.set_password(npwd)
                user.save()
                res['status'] = 200
                res['msg'] = '密码修改成功'
                CreateNotification(username=request.user.username, title="密码修改成功",
                                   content="您已经成功修改密码！")
            else:
                res['msg'] = '两次密码输入不一致'
        else:
            res['msg'] = '原密码错误'
        return JsonResponse(res)


@login_required
def MarkAsRead(request):
    nList = noti.objects.filter(host=request.user, isRead=False)
    for item in nList:
        if request.POST.get(str(item.id)) == str(item.id):
            item.isRead = True
            item.save()


@login_required
def delReadNotification(request):
    nList = noti.objects.filter(host=request.user, isRead=True)
    for item in nList:
        item.delete()
    return redirect('notification')


@login_required
def delNotification(request):
    nList = noti.objects.filter(host=request.user)
    for item in nList:
        item.delete()
    return JsonResponse({'msg': 'success'})


@login_required
@transaction.atomic
def getCourseList(request):
    if request.method == 'GET':
        try:
            page_course = []
            idExist = []
            search_kw = request.GET.get('search_kw', None)
            page = request.GET.get('page')
            num = request.GET.get('rows')
            right_boundary = int(page) * int(num)
            try:
                cList = request.session["courseList"]
            except KeyError as e:
                raise e
            for cour in cList:
                for value in cour.values():
                    if search_kw:
                        if search_kw in str(value) and cour['id'] not in idExist:
                            page_course.append(cour)
                            idExist.append(cour['id'])
                    else:
                        if cour['id'] not in idExist:
                            page_course.append(cour)
                            idExist.append(cour['id'])
            total = len(page_course)
            page_course = page_course[int(num) * (int(page) - 1):right_boundary]
            return JsonResponse({'total': total, 'rows': page_course})  # 一点骚操作，异步前端操作真的不熟
        except KeyError:
            return HttpResponse(1)  # 第一次还没有session
        except Exception as e:
            raise e

    if request.method == 'POST':
        UserQ = User.objects.get(username=request.user.username)
        host = UserQ.UserProfile
        ids = request.POST.get('ids')
        idList = []
        for id in ids.split(","):
            idList.append(int(id))
        gid = pay.random_str(10)
        for id in idList:
            if 'keyword' in request.session["courseList"][id - 1]:
                keyword = request.session["courseList"][id - 1]['keyword']
            else:
                keyword = ''
            kcm = request.session["courseList"][id - 1]['kcm']
            kch = request.session["courseList"][id - 1]['kch']
            kxh = request.session["courseList"][id - 1]['kxh']
            kcm = request.session["courseList"][id - 1]['kcm']
            term = request.session["courseList"][id - 1]['term']
            type = request.session["courseList"][id - 1]['type']
            teacher = request.session["courseList"][id - 1]['teacher']
            opener, _ = jwcVal.InitOpener()  # 公共查询不用代理
            find_same = courses.objects.filter(kch=kch, kxh=kxh)
            try:
                if find_same:
                    for item in find_same:
                        if item.status != '已完成':
                            CreateNotification(username=request.user.username, title="批量课程添加失败",
                                               content="在您通过多选课程时，课程号为" + str(kch) + "，课序号为" + str(
                                                   kxh) + "的课程《" + kcm + "》经系统检测，目前在系统中有相同课程未完成，请稍后再试！")
                            raise Exception("重复课程")
            except Exception as e:
                continue  # 跳过重复课程
            try:
                courseList = courseid2courses(opener, '', kch, kxh, term)
            except Exception as e:
                logger.error(str(e))
                print(e)
                raise Exception(e)
            campus = courseList[0]['xqm']
            location = ''
            for i, c in enumerate(courseList):
                location += (str(i + 1) + "：" + c['jxlm'] + " " + c['jasm'] + "\n")
            course = courses(kch=kch, kxh=kxh, kcm=kcm, host=host, type=type, term=term,
                             teacher=teacher, campus=campus, location=location, keyword=keyword, gid=gid)
            course.save()
            CreateNotification(username=request.user.username, title="批量课程添加成功",
                               content="您已经成功通过多选课程的方式，添加课程号为" + str(kch) + "，课序号为" + str(kxh) + "的课程《" + kcm + "》！")

        UserQ.UserProfile.courseRemainingCnt = F('courseRemainingCnt') - 1
        UserQ.UserProfile.courseCnt = F('courseCnt') + 1
        UserQ.UserProfile.save()
        del request.session["courseList"]
        return HttpResponse('success')


@login_required
def topup(request):
    if request.method == 'GET':
        points_per_course = 10.0
        UserQ = User.objects.get(username=request.user.username)
        points = UserQ.UserProfile.points
        availCourses = int(points / points_per_course)
        return render(request, 'store.html', locals())
    if request.method == 'POST':
        try:
            code = request.POST.get('code')
            try:
                founded = codes.objects.get(code=code)
                if founded.usedBy != '':
                    raise Exception("神秘代码已被使用！")
            except Exception:
                raise Exception("没有找到这串神秘代码！")

            UserQ = User.objects.get(username=request.user.username)
            userprofile = UserQ.UserProfile

            founded.usedBy = request.user.username
            founded.usedTime = time.strftime("%Y-%m-%d %H:%M:%S")
            userprofile.points += founded.points
            userprofile.save()
            founded.save()
            errormsg = "您已经成功通过神秘代码注入了" + str(founded.points) + "点数，您现在的点数为" + str(userprofile.points) + "！"
            CreateNotification(username=request.user.username, title="神秘力量注入成功",
                               content=errormsg)
        except Exception as e:
            errormsg = str(e)
        return render(request, 'store.html', locals())


@login_required
def addCodes(request):
    try:
        UserQ = User.objects.get(username=request.user.username)
        if UserQ.is_superuser == 0:
            raise Exception("死骗子！你不是管理员！")
        if request.method == 'POST':
            n = request.POST.get('number')
            points = request.POST.get('points')
            codeList = generate_code(16, int(n))
            for code in codeList:
                savecode = codes(code=code, points=float(points), addBy=request.user.username)
                savecode.save()
            errormsg = "神秘代码添加成功，你成功添加了" + str(n) + "条点数为" + str(points) + "的神秘代码！"
            CreateNotification(username=request.user.username, title="神秘代码添加成功",
                               content=errormsg)
            return render(request, 'addCodes.html', locals())
        if request.method == 'GET':
            return render(request, 'addCodes.html', locals())
    except Exception as e:
        errormsg = str(e)
        return render(request, 'store.html', locals())


@login_required
def storeExchange(request):
    points_per_course = 10.0
    UserQ = User.objects.get(username=request.user.username)
    points = UserQ.UserProfile.points
    availCourses = int(points / points_per_course)
    course_number = request.POST.get('course_number', None)
    if course_number:
        if int(course_number) <= availCourses:
            UserQ.UserProfile.points -= points_per_course * int(course_number)
            UserQ.UserProfile.courseRemainingCnt += int(course_number)
            UserQ.UserProfile.save()
            errormsg2 = "你成功使用了" + str(points_per_course * int(course_number)) + "个点数兑换了" + str(
                int(course_number)) + "个课程容量！"
            CreateNotification(username=request.user.username, title="课程容量兑换成功",
                               content=errormsg2)
        else:
            errormsg2 = "点数不足！你需要" + str(points_per_course * int(course_number)) + "个点数来完成此次兑换！"
    points = UserQ.UserProfile.points  # 查询新的
    availCourses = int(points / points_per_course)
    return render(request, 'store.html', locals())


@login_required
def getCodesList(request):
    if request.method == 'GET':
        try:
            page_codes = []
            page = request.GET.get('page')
            num = request.GET.get('rows')
            right_boundary = int(page) * int(num)
            codeSet: QuerySet[codes] = codes.objects.filter(addBy=request.user.username)
            for i, code in enumerate(codeSet):
                if code.usedBy == "":
                    usedBy = "未使用"
                else:
                    usedBy = code.usedBy
                local_time = utc2local(code.createTime)
                LOCAL_FORMAT = "%Y-%m-%d %H:%M:%S"
                create_time_str = local_time.strftime(LOCAL_FORMAT)
                single_code = {'id': i + 1, 'code': code.code, 'points': code.points, 'usedBy': usedBy,
                               'createTime': create_time_str}
                page_codes.append(single_code)
            total = len(codeSet)
            page_codes = page_codes[int(num) * (int(page) - 1):right_boundary]
            return JsonResponse({'total': total, 'rows': page_codes})  # 一点骚操作，异步前端操作真的不熟
        except Exception as e:
            raise e


# 支付相关
@login_required
def wxpay(request):
    response = Pay(request, 'WeChat')
    return response


@login_required
def alipay(request):
    response = Pay(request, 'AliPay')
    return response


def Pay(request, method):
    try:
        if request.method == 'POST':
            UserQ = User.objects.get(username=request.user.username)
            total_fee = request.POST['amount']
            fee_pattern = "(^[1-9](\d+)?(\.\d{1,2})?$)|(^0$)|(^\d\.\d{1,2}$)"  # 匹配金额正则
            pattern = re.compile(fee_pattern)
            match = pattern.match(total_fee)
            if match is None:
                raise Exception("金额不合法！")
            amount = int(float(total_fee) * 100)
            self_order_num = pay.order_num()
            body = '注入' + total_fee + '神秘点数'
            post_paras = {
                'mch_id': mch_id,
                'total_fee': amount,
                'out_trade_no': self_order_num,
                'body': body,
                'user_id': str(UserQ.UserProfile.uid)
            }
            sign = pay.get_sign(post_paras, secret_key)
            post_paras['sign'] = sign
            if method == 'WeChat':
                url = wxpay_url
            else:
                url = alipay_url
            response = requests.post(url=url, data=post_paras, timeout=3)
            response_dict = response.json()
            if response_dict['return_code'] != 0:
                raise Exception(
                    "请求错误，错误代码：" + response_dict['return_code'] + "，错误信息：" + response_dict['return_message'])
            else:
                qrcode = response_dict['qrcode']
                platform_order_no = response_dict['order_no']
                order = Orders(user=UserQ, method=method, trade_no=self_order_num, platform_no=platform_order_no,
                               body=body, total_fee=total_fee)
                order.save()
                return JsonResponse(
                    {'status': 200, 'qrcode': qrcode, 'amount': amount / 100, 'order_no': self_order_num})
    except Exception as e:
        errormsgpay = str(e)
        logger.error(errormsgpay)
        return JsonResponse({'status': 400, 'msg': errormsgpay})


@login_required
def check_pay(request):
    if request.is_ajax:
        order_num = request.POST.get('order_num')
        order = Orders.objects.get(trade_no=order_num)
        if order.status == 1:
            order.status = 2  # 2--通知已到位
            order.save()
        return HttpResponse(int(order.status))


@login_required
def cancel_order(request):
    if request.is_ajax:
        order_num = request.POST.get('order_num')
        order = Orders.objects.get(trade_no=order_num)  # 在知道订单号的情况下允许其他用户取消订单
        if order.status == 0:  # 只有等待中的订单才能取消
            post_paras = {
                'mch_id': mch_id,
                'order_no': order.platform_no,
            }
            sign = pay.get_sign(post_paras, secret_key)
            post_paras['sign'] = sign
            response = requests.post(url=cancel_url, data=post_paras)
            response_dict = response.json()
            if response_dict['return_code'] == 0:  # 出错不return
                order.status = -1
                order.save()
                CreateNotification(username=request.user.username, title="订单取消成功",
                                   content="您订单号为" + order.platform_no + "的注入" + str(order.total_fee) + "点数的订单已经成功取消！")
                return HttpResponse(int(order.status))


@csrf_exempt
def paycat_callback(request):  # 暂时支持支付通知 关闭通知  需要验签 验重
    try:
        if request.method == 'POST':
            data_dict = request.POST.dict()  # 商户号和金额为整数 注意转换否则签名错误
            data_dict['mch_id'] = int(data_dict['mch_id'])
            if data_dict['notify_type'] == 'order.succeeded':
                data_dict['total_fee'] = int(data_dict['total_fee'])
            sign = data_dict.pop('sign')
            back_sign = pay.get_sign(data_dict, secret_key)
            if sign == back_sign:
                out_trade_no = data_dict['out_trade_no']
                order = Orders.objects.get(trade_no=out_trade_no)
                if data_dict['notify_type'] == 'order.succeeded':
                    if order.status == 0:
                        total_fee = data_dict['total_fee']
                        transaction_id = data_dict['transaction_id']
                        payTime = data_dict['pay_at']
                        if total_fee == order.total_fee * 100:
                            order.payment_tool_no = transaction_id
                            order.payTime = payTime
                            order.status = 1
                            order.save()
                            userprofile = order.user.UserProfile
                            userprofile.points += order.total_fee
                            userprofile.save()
                            CreateNotification(username=order.user.username, title="点数注入成功",
                                               content="您订单号为" + order.trade_no + "的注入" + str(
                                                   order.total_fee) + "点数的订单已经完成支付！点数已经注入您的账户！")
                            return HttpResponse(1)
                        else:
                            CreateNotification(username=order.user.username, title="点数注入失败",
                                               content="您订单号为" + order.trade_no + "的注入" + str(
                                                   order.total_fee) + "点数的订单没有通过金额效验。")
                            raise Exception("金额效验失败！")
                    else:
                        raise Exception("支付成功回调提示：订单已经标记为完成！")
                elif data_dict['notify_type'] == 'order.closed':
                    if order.status == 0:
                        closedTime = data_dict['closed_at']
                        order.closedTime = closedTime
                        order.status = -1
                        order.save()
                        return HttpResponse(1)
                    else:
                        raise Exception("关闭订单回调提示：订单已经标记为完成！")
            else:
                raise Exception('签名效验失败！')
    except Exception as e:
        logger.error(str(e))
        return HttpResponse(status=200)
