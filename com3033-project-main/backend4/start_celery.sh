#!/bin/bash
#daphne -b 0.0.0.0 -p 8000 backend1.asgi:application &
sleep 60
celery -A backend4 worker -l info --pool threads -Q backend4 --max-tasks-per-child=1 --concurrency=1 -n backend4@mycustomhost &
celery -A backend4 beat -l info -s /celery/celerybeat-schedule
wait -n
exit $?