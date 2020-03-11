# SCUCourseKiller
A Website powered by Django which helps SCU students to monitor their courses status when selecting courses.

README.md waiting to be completed...

## Install
### Using Docker
```bash
git clone https://github.com/MrZilinXiao/SCUCourseKiller.git
docker build -t mrzilinxiao/scucoursekiller ./
docker run -d -p 8000:8000 --name=scucoursekiller mrzilinxiao/scucoursekiller
```
### Using docker-compose

```bash
docker-compose build # 构建容器
docker-compose start -d # 以daemon守护模式启动
docker-compose logs -f # 查看日志
```


### Manual Deployment (Not Recommended)
- git clone https://github.com/MrZilinXiao/SCUCourseKiller.git
