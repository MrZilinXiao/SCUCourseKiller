# -*- encoding: utf-8 -*-
"""
@File    : jwcCourse.py
@Time    : 2019/8/11 15:29
@Author  : MrZilinXiao
@Email   : me@mrxiao.net
@Software: PyCharm
"""
from urllib import error, parse, request
from .config import *
import json


def courseid2courses(opener, kcm='', kch='', kxh='', term=''):
    # 根据课程号、课序号获取具体课程信息

    # post 参数样例：zxjxjhh=2019-2020-1-1&kch=999008030&kcm=&js=&kkxs=&skxq=&skjc=&xq=&jxl=&jas=&pageNum=1&pageSize=30&kclb=
    post_params = {
        'zxjxjhh': term,
        'kch': kch,
        'kcm': kcm,
        'js': '',
        'kkxs': '',
        'skxq': '',
        'xq': '',
        'jxl': '',
        'jas': '',
        'pageNum': '1',
        'pageSize': '300',  # 可能30遍历不完
        'kclb': ''
    }
    data_parsed = parse.urlencode(post_params).encode('utf-8')
    Request = request.Request(courseQuery_url, data_parsed, headers=headers)
    Response = opener.open(Request)
    req = Response.read().decode('utf-8')
    # 样例输出：{
    # 	"pfcx": 0,
    # 	"list": {
    # 		"pageSize": 30,
    # 		"pageNum": 1,
    # 		"pageContext": {
    # 			"totalCount": 1
    # 		},
    # 		"records": [{
    # 			"id": "2019-2020-1-1999008030011111111111111111100000003103",
    # 			"zxjxjhh": "2019-2020-1-1",
    # 			"kch": "999008030",
    # 			"kxh": "01",
    # 			"kcm": "中华文化（艺术篇）",
    # 			"xf": "3",
    # 			"xs": "48",
    # 			"kkxsh": "101",
    # 			"kkxsjc": "艺术学院",
    # 			"kslxdm": "01",
    # 			"kslxmc": "考试",
    # 			"skjs": "黄宗贤* 吴永强 李振宇 汪燕翎 赵志红 李艳 ",
    # 			"bkskrl": 416,
    # 			"bkskyl": 0,
    # 			"xkmsdm": "01",
    # 			"xkmssm": "直选式",
    # 			"xkkzdm": "01",
    # 			"xkkzsm": "可选可退",
    # 			"xkkzh": null,
    # 			"xkxzsm": ";",
    # 			"kkxqh": "03",
    # 			"kkxqm": "江安",
    # 			"sfxzxslx": null,
    # 			"sfxzxsnj": null,
    # 			"sfxzxsxs": "否",
    # 			"sfxzxxkc": null,
    # 			"sfxzxdlx": "否",
    # 			"xqh": "03",
    # 			"jxlh": "301",
    # 			"jash": "水上报告厅",
    # 			"jclxdm": "01",
    # 			"skzc": "111111111111111110000000",
    # 			"skxq": 3,
    # 			"skjc": 10,
    # 			"cxjc": 3,
    # 			"xqlxdm": "1",
    # 			"xqdm": "1",
    # 			"xss": 416,
    # 			"zcsm": "1-17周",
    # 			"kclbdm": "700",
    # 			"kclbmc": "人文艺术与中华文化传承",
    # 			"xkbz": null,
    # 			"xqm": "江安",
    # 			"jxlm": "一教A座",
    # 			"jasm": "水上报告厅"
    # 		}]
    # 	}
    # }
    dic = json.loads(req)
    if dic['pfcx'] == 0:
        courses = dic['list']['records']
        if kxh != '':
            for i in range(len(courses)-1, -1, -1):
                if courses[i]['kxh'] != kxh:
                    courses.pop(i)
        return courses
    else:
        raise Exception("频繁查询，请5秒后再试")
