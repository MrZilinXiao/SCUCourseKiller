import http.cookiejar
from urllib import error
from urllib import parse
from urllib import request
import requests
from .config import *


def InitOpener(cookie=None):
    if cookie is None:
        cookie = http.cookiejar.CookieJar()
    cookie_support = request.HTTPCookieProcessor(cookie)
    # For Proxy
    proxy_handler = request.ProxyHandler(proxy)
    opener = request.build_opener(cookie_support, proxy_handler)
    return opener, cookie


def valCookie(cookieStr):
    cookie_dict = eval(cookieStr)
    cookieJar = requests.utils.cookiejar_from_dict(cookie_dict)
    # cookie_support = request.HTTPCookieProcessor(cookieJar)
    # proxy_handler = request.ProxyHandler(proxy)
    (opener, _) = InitOpener(cookieJar)
    testreq = request.Request(token_url, headers=headers)
    try:
        testVal = opener.open(testreq)
        if testVal.url == 'http://zhjw.scu.edu.cn/login':
            raise Exception("Cookie已经失效！已经更新为最新的Cookie！")
        return True
    except error.HTTPError as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        raise Exception(e)


def valjwcAccount(stuID, stuPass):  # 可以更新Cookie
    login_data = {
        'j_username': stuID,
        'j_password': stuPass,
        'j_captcha': 'error',
    }
    [opener, cookie] = InitOpener()
    # Login
    opener.open(request.Request("http://zhjw.scu.edu.cn/login", headers=headers))  # Get cookie
    login_data_parsed = parse.urlencode(login_data).encode("utf-8")
    loginRequest = request.Request(login_url, login_data_parsed, headers=headers)
    try:
        loginResponse = opener.open(loginRequest)
        cookie_dict = requests.utils.dict_from_cookiejar(cookie)
        return cookie_dict
    except error.HTTPError as e:
        print(e)
        raise Exception("Invalid Login Info")
