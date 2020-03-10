
import djcelery
import pytz
from celery import platforms
from celery.schedules import crontab
from datetime import timedelta

djcelery.setup_loader()

# CELERY_TIMEZONE = 'UTC'

# CELERY_ENABLE_UTC = False

DJANGO_CELERY_BEAT_TZ_AWARE = False

CELERY_IGNORE_RESULT = True

CELERYD_TASK_TIME_LIMIT = 10

BROKER_URL = 'redis://127.0.0.1:6379/6'  # Docker Config

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
# 导入任务
CELERY_IMPORTS = ('SCUKiller.tasks',)

# 设置队列
CELERY_QUEUES = {
    'beat_tasks': {
        'exchange': 'beat_tasks',
        'exchange_type': 'direct',
        'binding_key': 'beat_tasks'
    },
    'work_queue': {
        'exchange': 'work_queue',
        'exchange_type': 'direct',
        'binding_key': 'work_queue'
    }
}
# 设置默认列队,不符合其他队列的任务放在默认队列
CELERY_DEFAULT_QUEUE = 'work_queue'

# 有些情况下可以防止死锁
CELERYD_FORCE_EXECV = True

# 设置并发数量
CELERYD_CONCURRENCY = 4

platforms.C_FORCE_ROOT = True

# 每个worker最多执行100个任务，防止泄露内存
CELERYD_MAX_TASKS_PER_CHILD = 5

# 设置定时执行
CELERYBEAT_SCHEDULE = {
    'watchUserCourses': {
        'task': 'SCUKiller.tasks.watchUserCourses',
        # 'task': 'SCUKiller.tasks.watchUserCours',
        'schedule': timedelta(milliseconds=1000),
        'options': {
            'queue': 'beat_tasks'
        }
    }
}
