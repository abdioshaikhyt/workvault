#!/bin/bash
#daphne -b 0.0.0.0 -p 8000 backend1.asgi:application &
sleep 60
celery -A backend1 worker -l info --pool threads -Q backend1 --max-tasks-per-child=1 --concurrency=1 -n backend1@mycustomhost &
celery -A backend1 beat -l info -s /celery/celerybeat-schedule
wait -n
exit $?