import pika
import uuid
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backendauth.settings")

import django
django.setup()

from backendauthapp.models import CustomUser, Practice

def send_user_to_backend1(data, event_type):
   
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='staff_queue')

    corr_id = str(uuid.uuid4())
    message_data = {
        "event_type": event_type,
        "staff": data
    }
    message = json.dumps(message_data)

    channel.basic_publish(
        exchange='',
        routing_key='staff_queue',
        properties=pika.BasicProperties(
            correlation_id=corr_id,
        ),
        body=message
    )
    print("Sent:", message)
    connection.close()

