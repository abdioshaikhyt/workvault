#!/bin/bash
#daphne -b 0.0.0.0 -p 8000 backend3.asgi:application &
sleep 60
celery -A backend3 worker -l info --pool threads -Q backend3 --max-tasks-per-child=1 --concurrency=1 -n backend3@mycustomhost &
celery -A backend3 beat -l info -s /celery/celerybeat-schedule
wait -n
exit $?