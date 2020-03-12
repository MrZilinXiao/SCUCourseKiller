# SCUCourseKiller
A web app powered by Django, helping SCU students to monitor their courses status.

**Attention: Some parts of this README were written in Simplified Chinese.**

## What For?

此项目本为个人学习Django开发时的练习，随后便突发奇想，在本项目中引入了监控课程的功能。通过多次版本迭代，目前本项目采用Celery作为消息队列能够实现高效、顺畅的多用户课程监控功能。

用户管理、支付系统、冲突检查和选课过程中的异常处理也在本项目中有所体现。

**本人没有经历成体系的软件工程培训，也无中小型Python项目开发经验，部分代码仅做到了“能用就行”的水准，欢迎您随时提出PR。**

## Features
- Docker-compose部署，开箱即用
- 现代化的前端交互逻辑
- 使用Celery确保高效的监控频率
- 较为完善的异常处理机制

## Demo
![demo](https://raw.githubusercontent.com/MrZilinXiao/SCUCourseKiller/master/repo/1.png "demo")
![demo2](https://raw.githubusercontent.com/MrZilinXiao/SCUCourseKiller/master/repo/2.png "demo2")

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