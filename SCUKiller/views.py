# coding=utf-8

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

from django.contrib.auth import login, logout
from .models import UserProfile, User, notification as noti, courses
from .forms import RegForm, LoginForm, AddCourseForm, AddjwcAccount
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

from . import jwcAccount as jwcVal
from .models import jwcAccount as jwcModel
from .jwcCourse import courseid2courses

from django.db.models import Q

import logging
import json

logger = logging.getLogger(__name__)


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
                print(user)
                if user is not None:
                    login(request, user)
                    print(u"登录成功！")
                    return redirect(request.session['login_from'])
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
                # notice = '剩余课程权限不足！'
                # return render(request, 'courseManagement.html', locals())
            try:
                jwcaccount = userprofile.jwcHost
            except Exception as e:
                print(e)
                jwcaccount = None
            if jwcaccount is None:
                raise Exception('您尚未绑定教务处账号！')
                # notice = '您尚未绑定教务处账号！'
                # return render(request, 'courseManagement.html', locals())
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
                find_same = courses.objects.filter(kch=kch, kxh=kxh)
                if find_same:
                    for item in find_same:
                        if item.status != '已完成':
                            Courses = UserQ.UserProfile.coursesHost.all()
                            raise Exception("系统中有相同的课程未完成！")
                host = UserQ.UserProfile
                # DONE: 加入课程时验证课程是否存在
                # DOING:如果课程号与课序号都给出则关闭关键词模式
                # DOING: 在前端可视化返回符合要求的课程列表

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
                    # TODO:都给出时需要获取课程名
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
                        request.session["courseList"] = rows
                        raise Exception("请在右侧的课程列表中选择需要监控的课程并提交！")
                UserQ.UserProfile.courseRemainingCnt -= 1
                UserQ.UserProfile.courseCnt += 1
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
    if request.user.is_authenticated:
        if request.method == 'GET':
            UserQ = User.objects.get(username=request.user.username)
            # get返回单对象 反向查询需要try 当找不到或找到多个时报错
            # filter返回QuerySet，直接if判断是否为空
            userprofile = UserQ.UserProfile
            try:
                jwcaccount = userprofile.jwcHost
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
                        cookie_dict = jwcVal.valjwcAccount(stuID, stuPass)
                        user = User.objects.get(username=request.user.username)
                        jwc = jwcModel(jwcNumber=stuID, jwcPasswd=stuPass, userprofile=user.UserProfile,
                                       jwcCookie=str(cookie_dict))
                        jwc.save()  # TODO: verify if this is working
                        CreateNotification(username=request.user.username, title="教务处账号绑定成功",
                                           content="您已经成功绑定学号为" + str(stuID) + "的教务处账号！")
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
                valid = jwcVal.valCookie(cookieStr)
                errormsg = "Cookie有效！"
            except Exception as e:
                errormsg = e  # HTTPError500（Invaild Session) 或者
        except Exception as e:
            errormsg = e  # 恶意请求 或 Cookie Invaild Session
        if str(errormsg) == "Cookie已经失效！已经更新为最新的Cookie！" or str(errormsg) == "HTTP Error 500: Internal Server Error":
            jwcaccount.jwcCookie = str(jwcVal.valjwcAccount(jwcaccount.jwcNumber, jwcaccount.jwcPasswd))
            jwcaccount.save()
            errormsg = "Cookie已经失效！已经更新为最新的Cookie！"
        return render(request, "jwcAccount.html", locals())


@login_required
def courseManagement(request):
    if request.user.is_authenticated:
        UserQ = User.objects.get(username=request.user.username)
        form = AddCourseForm()
        cidDel = request.GET.get("del")
        notice = ''
        if cidDel is not None:
            CourseQ = courses.objects.get(cid=cidDel)
            notice = "课程《" + CourseQ.kcm + "》已被成功删除"
            CourseQ.delete()
            CreateNotification(username=request.user.username, title="课程删除成功",
                               content="课程《" + CourseQ.kcm + "》已被成功删除")
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

            else:
                res['msg'] = '两次密码输入不一致'
                CreateNotification(username=request.user.username, title="密码修改成功",
                                   content="您已经成功修改密码！")

        else:
            res['msg'] = '原密码错误'
        return JsonResponse(res)


def CreateNotification(username, title, content):
    UserQ = User.objects.get(username=username)
    notifi = noti(host=UserQ, title=title, content=content)
    notifi.save()
    print("[%s][%s]%s" % (username, title, content))


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
        for id in idList:
            kcm = request.session["courseList"][id - 1]['kcm']
            kch = request.session["courseList"][id - 1]['kch']
            kxh = request.session["courseList"][id - 1]['kxh']
            kcm = request.session["courseList"][id - 1]['kcm']
            term = request.session["courseList"][id - 1]['term']
            type = request.session["courseList"][id - 1]['type']
            teacher = request.session["courseList"][id - 1]['teacher']
            opener, _ = jwcVal.InitOpener()
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
                             teacher=teacher, campus=campus, location=location)
            course.save()
            CreateNotification(username=request.user.username, title="批量课程添加成功",
                               content="您已经成功通过多选课程的方式，添加课程号为" + str(kch) + "，课序号为" + str(kxh) + "的课程《" + kcm + "》！")

        UserQ.UserProfile.courseRemainingCnt -= 1
        UserQ.UserProfile.courseCnt += 1
        UserQ.UserProfile.save()
        del request.session["courseList"]
        return HttpResponse('success')
