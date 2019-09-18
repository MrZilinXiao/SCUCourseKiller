import http.cookiejar
from urllib import error
from urllib import parse
from urllib import request
import requests
import socket
import logging
from .config import *
from retrying import retry
from .models import User

logger = logging.getLogger(__name__)


# timeout = 3
# socket.setdefaulttimeout(timeout)


@retry(stop_max_attempt_number=3)
def getProxy(username):
    UserQ = get(username=username)
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
        logger.error("Getting Proxy from pool Error...")


@retry(stop_max_attempt_number=3)
def checkProxy(proxy_text):
    try:
        if proxy_text:
            proxy = {'http': proxy_text}
            requests.get('http://wenshu.court.gov.cn/', proxies=proxy, timeout=1)
            return True
        else:
            return False
    except:
        logger.error("Connection Failed while using proxy:" + proxy_text)


def InitOpener(username='', cookie=None):
    if cookie is None:
        cookieJar = http.cookiejar.CookieJar()
    elif isinstance(cookie, str):
        cookie_dict = eval(cookie)
        cookieJar = requests.utils.cookiejar_from_dict(cookie_dict)
    else:
        cookieJar = cookie
    cookie_support = request.HTTPCookieProcessor(cookieJar)
    # For Proxy
    if username == '':
        proxy = {}
    else:
        proxy = getProxy(username)
    proxy_handler = request.ProxyHandler(proxy)
    # Get Latest Proxy every time?
    opener = request.build_opener(cookie_support, proxy_handler)
    return opener, cookieJar


def valCookie(cookieStr, username=''):
    cookie_dict = eval(cookieStr)
    cookieJar = requests.utils.cookiejar_from_dict(cookie_dict)
    (opener, _) = InitOpener('', cookieJar)  # 先不使用代理
    testreq = request.Request(token_url, headers=headers)
    try:
        testVal = opener.open(testreq)
        if testVal.url == 'http://zhjw.scu.edu.cn/login':  # 如果指向登录页面 说明cookie过期或失效
            raise Exception("Cookie已经失效！已经更新为最新的Cookie！")
        return True
    except error.HTTPError as e:
        logger.error(e)  # HTTP 500 302 是未知类型的错误
        raise e
    except Exception as e:
        logger.error(e)
        raise e


def valjwcAccount(stuID, stuPass, username=''):  # 可以更新Cookie
    login_data = {
        'j_username': stuID,
        'j_password': stuPass,
        'j_captcha': 'error',
    }
    [opener, cookie] = InitOpener('')  # 先不用代理
    # Login
    opener.open(request.Request(login_page_url, headers=headers))  # Get cookie
    login_data_parsed = parse.urlencode(login_data).encode("utf-8")
    loginRequest = request.Request(login_url, login_data_parsed, headers=headers)
    try:
        loginResponse = opener.open(loginRequest)
        cookie_dict = requests.utils.dict_from_cookiejar(cookie)
        return cookie_dict
    except error.HTTPError as e:
        logger.error(e)
        if e.filename == 'http://zhjw.scu.edu.cn/login?errorCode=badCredentials':
            raise Exception("密码错误！请删除教务处账号后重新添加！在监控期间请不要修改教务处密码！")
        else:
            raise Exception("登陆时遭遇未知错误！")
