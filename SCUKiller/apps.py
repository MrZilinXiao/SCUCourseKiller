import threading
import time
import random
from django.apps import AppConfig
from SCUKiller.config import watch_interval


def watchLoop():
    # pass
    from SCUKiller import utils
    while True:  # watch将导致数据库不同步 很烦
        t = threading.Thread(target=utils.watchCourses)
        t.start()
        time.sleep(random.random() + watch_interval)


class SCUKillerConfig(AppConfig):
    name = 'SCUKiller'

    def ready(self):
        watch_Loop = threading.Thread(target=watchLoop)
        watch_Loop.setDaemon(True)
        watch_Loop.start()
