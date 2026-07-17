#!/bin/bash
#daphne -b 0.0.0.0 -p 8000 backend1.asgi:application &
sleep 60
python backend1app/consumer.py
wait -n
exit $?