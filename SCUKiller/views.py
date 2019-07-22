from django.shortcuts import render, HttpResponse, redirect

from django.contrib.auth import login, logout
from .models import UserProfile, User, notification as noti, courses
from .forms import RegForm, LoginForm, AddCourseForm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required


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
                    print("登录成功！")
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

        return render(request, 'notification.html', locals())
    else:
        return redirect('login')


@login_required
def index(request):
    if request.user.is_authenticated:
        user = request.user
        username = user.username
        UserQ = User.objects.get(username=username)
        notificationsCnt = len(UserQ.notificationHost.all())
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
        form = AddCourseForm(request.POST)
        if form.is_valid():
            UserQ = User.objects.get(username=request.user.username)
            keyword = form.cleaned_data['keyword']
            kch = form.cleaned_data['kch']
            kxh = form.cleaned_data['kxh']
            type = form.cleaned_data['type']
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
                        notice = '系统中有相同的课程未完成！'
                        Courses = UserQ.UserProfile.coursesHost.all()
                        return render(request, 'courseManagement.html', locals())
            host = UserQ.UserProfile
            notice = '课程添加成功！'  # TODO: Need to verify whether it is a vaild course
            course = courses(kch=kch, kxh=kxh, keyword=keyword, host=host, type=ctype)
            course.save()
            Courses = UserQ.UserProfile.coursesHost.all()
        else:
            notice = '提交的课程信息不合法！'
        return render(request, 'courseManagement.html', locals())


@login_required
def addjwcAccount(request):
    pass


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
            Courses = UserQ.UserProfile.coursesHost.all()
            return render(request, 'courseManagement.html', locals())

        Courses = UserQ.UserProfile.coursesHost.all()
        return render(request, 'courseManagement.html', locals())
    else:
        return redirect('login')


@login_required
def accountManagement(request):
    return None
