#!/bin/bash
#uvicorn backend3.asgi:application --host 0.0.0.0 --port 8002 &
sleep 60
python backend3app/consumer.py
wait -n
exit $?