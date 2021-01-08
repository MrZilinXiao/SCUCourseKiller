# SCUCourseKiller

**Attention: Some parts of this README were written in Simplified Chinese.**

## What For?

此项目本为个人学习Django开发时的练习，随后便突发奇想，在本项目中引入了监控课程的功能。通过多次版本迭代，目前本项目采用Celery作为消息队列能够实现高效、顺畅的多用户课程监控功能。

用户管理、支付系统、冲突检查和选课过程中的异常处理也在本项目中有所体现。

**在本人完成本项目时尚未经历成体系的软件工程培训，代码整体布局、可重用性与可读性都不堪入目，各位在参考时只选取感兴趣的逻辑实现阅读即可。由于本人已没有选课需求，本项目将被暂时搁置。**

## Key Components

- 验证码模块：check_captcha.py
- 登录逻辑：jwcAccount.py
- Celery定时任务：tasks.py

## Features
- Docker-compose部署，开箱即用
- 现代化的前端交互逻辑
- 使用Celery确保高效的监控频率
- 较为完善的异常处理机制

## Demo
![demo2](https://upyun.mrxiao.net/img/2.png)
![demo1](https://upyun.mrxiao.net/img/1.png)
## Install
### Using Docker
While this repo configuration is for docker-compose, further change is needed about your MySQL and redis data source.

```bash
# Codes below only build web service container for you.
git clone https://github.com/MrZilinXiao/SCUCourseKiller.git
docker build -t mrzilinxiao/scucoursekiller ./
docker run -d -p 8000:8000 --name=scucoursekiller mrzilinxiao/scucoursekiller
```
### Using docker-compose

Docker-compose will build several containers: db, redis and web. 

The container web uses nginx as a middleware, which communicates with Django through WSGI.

```bash
git clone https://github.com/MrZilinXiao/SCUCourseKiller.git
cd SCUCourseKiller
docker-compose build # build all three containers, time consumption depending on device
docker-compose start -d # run containers in daemon mode
docker-compose logs -f # check logs
```

### Manual Deployment (Not Recommended)

```bash
- git clone https://github.com/MrZilinXiao/SCUCourseKiller.git
```

#### Recommended Environment
- Python 3.5+
- Django 2+

All other packages needed can be downloaded from PyPI using `pip3 install -r requirements.txt`.

In order to deploy manually, MySQL and redis data sources are needed and correctly configured in `SCUKiller/config.py` and `SCUCourseKiller/celeryconfig.py`.
