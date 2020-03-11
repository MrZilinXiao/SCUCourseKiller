FROM centos:7
MAINTAINER MrZilinXiao <xiaozilin1@gmail.com>
ENV TZ "Asia/Shanghai"
ENV DOCKER_SRC=SCUCourseKiller
ENV DOCKER_HOME=/root
ENV DOCKER_PROJECT=/root/SCUCourseKiller
WORKDIR $DOCKER_HOME
RUN mkdir SCUCourseKiller
RUN yum -y install epel-release yum-utils && \
    yum -y install git nginx gcc gcc-c++ && \
	yum -y install python36 python36-devel python36-pip && \
    yum clean all
RUN yum -y install mariadb-devel mysql-devel
WORKDIR $DOCKER_PROJECT
COPY ./ ./
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --default-timeout=100
EXPOSE 8000
RUN chmod u+x start_script
ENTRYPOINT ["./start_script"]