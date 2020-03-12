from django.apps import AppConfig


class SCUKillerConfig(AppConfig):
    name = 'SCUKiller'

    def ready(self):
        from .models import courses
        courses.objects.filter(isSuccess=0).update(inq=False)  # 启动时清空了队列
        # 考虑使用celery
        # watch_Loop = threading.Thread(target=watchLoop)
        # watch_Loop.setDaemon(True)
        # watch_Loop.start()
