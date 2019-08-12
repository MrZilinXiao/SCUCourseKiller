import http.cookiejar
from urllib import error
from urllib import parse
from urllib import request
import requests
from .config import *
from retrying import retry
from .models import User


@retry(stop_max_attempt_number=3)
def getProxy(username):
    UserQ = User.objects.get(username=username)
    proxy_text = UserQ.UserProfile.jwcaccount.proxy
    try:
        if checkProxy(proxy_text):
            Proxy = {'http': proxy_text}
        else:
            r = requests.get(proxy_pool_url)
            Proxy = {'http': r.text}
            UserQ.UserProfile.jwcaccount.proxy = r.text
            UserQ.UserProfile.jwcaccount.save()
        return Proxy
    except:
        print("Getting Proxy from pool Error...")


@retry(stop_max_attempt_number=3)
def checkProxy(proxy_text):
    try:
        if proxy_text:
            proxy = {'http': proxy_text}
            requests.get('http://wenshu.court.gov.cn/', proxies=proxy)
            return True
        else:
            return False
    except:
        print("Connection Failed while using proxy:" + proxy_text)


def InitOpener(username='', cookie=None):
    if cookie is None:
        cookie = http.cookiejar.CookieJar()
    cookie_support = request.HTTPCookieProcessor(cookie)
    # For Proxy
    if username == '':
        proxy = {}
    else:
        proxy = getProxy(username)
    proxy_handler = request.ProxyHandler(proxy)
    # Get Latest Proxy every time?
    opener = request.build_opener(cookie_support, proxy_handler)
    return opener, cookie


def valCookie(cookieStr, username=''):
    cookie_dict = eval(cookieStr)
    cookieJar = requests.utils.cookiejar_from_dict(cookie_dict)
    # cookie_support = request.HTTPCookieProcessor(cookieJar)
    # proxy_handler = request.ProxyHandler(proxy)
    (opener, _) = InitOpener(username, cookieJar)
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


def valjwcAccount(stuID, stuPass, username=''):  # 可以更新Cookie
    login_data = {
        'j_username': stuID,
        'j_password': stuPass,
        'j_captcha': 'error',
    }
    [opener, cookie] = InitOpener(username=username)
    # Login
    opener.open(request.Request(login_page_url, headers=headers))  # Get cookie
    login_data_parsed = parse.urlencode(login_data).encode("utf-8")
    loginRequest = request.Request(login_url, login_data_parsed, headers=headers)
    try:
        loginResponse = opener.open(loginRequest)
        cookie_dict = requests.utils.dict_from_cookiejar(cookie)
        return cookie_dict
    except error.HTTPError as e:
        print(e)
        raise Exception("Invalid Login Info")
