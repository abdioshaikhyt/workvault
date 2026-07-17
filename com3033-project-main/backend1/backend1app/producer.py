import pika
import uuid
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend1.settings")

import django
django.setup()

def send_job_to_backend2(data, event_type):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='job_queue')

    corr_id = str(uuid.uuid4())
    message_data = {
        "event_type": event_type,
        "job": data
    }
    message = json.dumps(message_data)

    channel.basic_publish(
        exchange='',
        routing_key='job_queue',
        properties=pika.BasicProperties(
            correlation_id=corr_id,
        ),
        body=message
    )
    print("Sent:", message)
    connection.close()


def send_job_to_backend3(data, event_type):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='file_queue')

    corr_id = str(uuid.uuid4())
    message_data = {
        "event_type": event_type,
        "file": data
    }
    message = json.dumps(message_data)

    channel.basic_publish(
        exchange='',
        routing_key='file_queue',
        properties=pika.BasicProperties(
            correlation_id=corr_id,
        ),
        body=message
    )
    print("Sent:", message)
    connection.close()