#!/bin/bash
#uvicorn backend2.asgi:application --host 0.0.0.0 --port 8001 &
sleep 60
python backend2app/consumer.py
wait -n
exit $?