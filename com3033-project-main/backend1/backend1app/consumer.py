import pika
import json
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend1.settings")

import django
django.setup()

from backend1app.models import Staff

print("Django setup completed.")

print("Connecting to RabbitMQ...")
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='staff_queue')
print("Connected and queue declared.")

def callback(ch, method, properties, body):
    print(f"Received message: {body}")
    try:
        data = json.loads(body.decode())
    except Exception as e:
        print(f"Failed to decode JSON: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    event_type = data.get("event_type")
    staff_data = data.get("staff")

    print(f"Event type: {event_type}")
    print(f"Staff data: {staff_data}")

    if event_type == "create":
        try:
            staff = Staff.objects.create(**staff_data)
            print(f"Created Book object with ID: {staff.staff_id}")
        except Exception as e:
            print(f"Failed to create book record: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='staff_queue', on_message_callback=callback)

print("Starting to consume...")
channel.start_consuming()