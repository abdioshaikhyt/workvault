#!/bin/bash
#daphne -b 0.0.0.0 -p 8000 backend2.asgi:application &
sleep 60
celery -A backend2 worker -l info -P prefork -Q backend2 --max-tasks-per-child=1 --concurrency=1 -n backend2@mycustomhost &
celery -A backend2 beat -l info -s /celery/celerybeat-schedule
wait -n
exit $?
