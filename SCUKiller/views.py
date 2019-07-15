from django.shortcuts import render, HttpResponse, redirect

from django.contrib.auth import login
from .models import UserProfile, User
from .forms import RegForm, LoginForm
from django.contrib.auth import authenticate


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
        return render(request, 'register.html', locals(), {'form': form})
    elif request.method == 'POST':
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
                    user.save()
                    userProfile = UserProfile(user=user, telephone=phoneNumber)
                    userProfile.save()
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    return redirect(request.session['login_from'], '/')
            elif captcha != request.session['CheckCode'].lower():
                errormsg = '验证码错误'
            return render(request, 'register.html', locals(), {'form': form})
        else:
            return render(request, 'register.html', {'form': form})


def logIn(request):
    if request.user.is_authenticated:
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if request.method == 'GET':
        form = LoginForm()
        request.session['login_from'] = request.META.get('HTTP_REFERER',
                                                         '/')
        return render(request, 'login.html', locals(), {'form': form})
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
