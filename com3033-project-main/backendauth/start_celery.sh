#!/bin/bash
#daphne -b 0.0.0.0 -p 8000 backend1.asgi:application &
sleep 60
celery -A backendauth worker -l info --pool threads -Q backendauth --max-tasks-per-child=1 --concurrency=1 -n backendauth@mycustomhost &
celery -A backendauth beat -l info -s /celery/celerybeat-schedule
wait -n
exit $?