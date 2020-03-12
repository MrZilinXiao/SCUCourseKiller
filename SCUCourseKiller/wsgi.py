"""
WSGI config for SCUCourseKiller project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from .celeryconfig import *  # 导入Celery配置信息

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SCUCourseKiller.settings')

application = get_wsgi_application()
