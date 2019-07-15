from django.shortcuts import render
from django.http import HttpResponse


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


def register(request):
    if request.method == 'GET':
        request.session['login_from'] = request.META.get('HTTP_REFERER',
                                                         '/')
        return render(request, 'register.html', locals())
