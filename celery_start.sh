cd /root/SCUCourseKiller/ && python3 manage.py celery worker -B -l info > celery.log 2>&1 &
python3 manage.py celery flower --address=0.0.0.0 --port=5555 > flower.log 2>&1 &