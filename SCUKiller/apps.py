import threading
import time
import random
from django.apps import AppConfig
from SCUKiller.config import watch_interval


def watchLoop():
    pass
    from SCUKiller import utils
    lock = threading.Lock()
    while True:  # watch将导致数据库不同步 很烦
        t = threading.Thread(target=utils.watchCourses, args=(None, lock))
        t.start()
        time.sleep(random.random() + watch_interval)


class SCUKillerConfig(AppConfig):
    name = 'SCUKiller'

    def ready(self):
        from .models import courses
        courses.objects.all().update(inq=0)  # 启动时清空了队列
        # 考虑使用celery
        # watch_Loop = threading.Thread(target=watchLoop)
        # watch_Loop.setDaemon(True)
        # watch_Loop.start()
