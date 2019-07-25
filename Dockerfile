FROM centos:7
#声明镜像制作者
MAINTAINER MrZilinXiao <xiaozilin1@gmail.com>
#设置时区
ENV TZ "Asia/Shanghai"

# 设置系统环境变量DOCKER_SRC 总项目文件
ENV DOCKER_SRC=SCUCourseKiller
# 设置系统环境变量DOCKER_HOME
ENV DOCKER_HOME=/root
# 设置系统环境变量DOCKER_PROJECT
ENV DOCKER_PROJECT=/root/SCUCourseKiller

#这句指令相当与：cd /root
WORKDIR $DOCKER_HOME
#紧接着在root目录下面创建了两个文件夹
RUN mkdir media static

#安装应用运行所需要的工具依赖pip，git好像没用上，mysql客户端，
RUN yum -y update && \
    yum -y install epel-release yum-utils && \
    yum -y install groupinstall development && \
    yum -y install git nginx gcc gcc-c++ python-devel && \
	yum -y install https://centos7.iuscommunity.org/ius-release.rpm && \
	yum -y install python36u python36u-devel python36u-pip && \
    yum clean all && \
	ln -s /usr/bin/python3.6 /usr/bin/python3 && \
	ln -s /usr/bin/pip3.6 /usr/bin/pip3 && \
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip

# cd $DOCKER_PROJECT
WORKDIR $DOCKER_PROJECT
# . 表示当前目录，一是Dockerfile所在的目录，二是刚刚设置的DOCKER_PROJECT目录，
#这一步操作将会把项目中application目录下的所有文件拷贝到镜像目录DOCKER_PROJECT=/root/project下面
COPY ./ ./
#这一步安装python依赖软件django、Pillow、mysql-python、uwsgi、django-ckeditor。
#补充，-i 是修改pip源，默认的源速度很慢，经常卡在这里。
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
#暴露端口8000，到时候执行docker run 的时候才好把宿主机端口映射到8000
EXPOSE 8000
#赋予start_script执行权限
RUN chmod u+x start_script
#容器启动后要执行的命令
ENTRYPOINT ["./start_script"]