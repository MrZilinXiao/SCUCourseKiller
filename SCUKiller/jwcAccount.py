import http.cookiejar
import logging
import time
from urllib import error
from urllib import parse
from urllib import request
from .config import *


def valjwcAccount(stuID, stuPass):
    login_data = {
        'j_username': stuID,
        'j_password': stuPass,
        'j_captcha': 'error',
    }
    cookie = http.cookiejar.CookieJar()
    cookie_support = request.HTTPCookieProcessor(cookie)
    # For Proxy
    proxy_handler = request.ProxyHandler(proxy)
    opener = request.build_opener(cookie_support, proxy_handler)
    # Login
    opener.open(request.Request("http://zhjw.scu.edu.cn/login", headers=headers))  # Get cookie
    login_data_parsed = parse.urlencode(login_data).encode("utf-8")
    loginRequest = request.Request(login_url, login_data_parsed, headers=headers)
    try:
        loginResponse = opener.open(loginRequest)
        return str(cookie)
    except error.HTTPError as e:
        print(e)
        raise Exception("Invalid Login Info")