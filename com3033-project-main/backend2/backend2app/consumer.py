import django
import pika
import json
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend2.settings")


django.setup()
from backend2app.models import JobSearch

print("Django setup completed.")

print("Connecting to RabbitMQ...")
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='job_queue')
print("Connected and queue declared.")
# A consumer is used to receive messages from RabbitMQ sent by the other backends


def callback(ch, method, properties, body):
    print(f"Received message: {body}")
    # Attempts to read the message received
    try:
        data = json.loads(body.decode())
    except Exception as e:
        print(f"Failed to decode JSON: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Exracts the type of request and the job data for it
    event_type = data.get("event_type")
    job_data = data.get("job")

    print(f"Event type: {event_type}")
    print(f"Job data: {job_data}")

    # If told to create a job, attempts to create a job
    if event_type == "job_created":
        try:
            period_end_str = job_data.get("period_end")
            # Attempts to parse the end of the job into the date format
            if period_end_str:
                try:
                    job_data["period_end"] = datetime.fromisoformat(
                        period_end_str).date()
                except Exception as e:
                    print(f"Failed to parse period_end: {e}")
                    job_data["period_end"] = None

            # Attempts to create a job object
            job = JobSearch.objects.create(**job_data)
            print(f"Created Job object with ID: {job.job_id}")
        except Exception as e:
            print(f"Failed to create book record: {e}")

    # If told to update a job, attempts to update the job with the specified ID
    elif event_type == "job_updated":
        try:
            # Checks to see if a job ID was given
            job_id = job_data.get("job_id")
            if not job_id:
                print("job_id missing in job_updated event")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Attempts to parse the end of the job into the date format
            period_end_str = job_data.get("period_end")
            if period_end_str:
                try:
                    job_data["period_end"] = datetime.fromisoformat(
                        period_end_str).date()
                except Exception as e:
                    print(f"Failed to parse period_end: {e}")
                    job_data["period_end"] = None

            # Finds the fields that need to be updated
            fields_to_update = {k: v for k,
                                v in job_data.items() if k != "job_id"}

            # Checks to see if a job with the given ID exists, and updates the job with the new data
            try:
                job_instance = JobSearch.objects.get(job_id=job_id)
                for k, v in fields_to_update.items():
                    setattr(job_instance, k, v)
                job_instance.save()

            except JobSearch.DoesNotExist:
                print(f"No job found with job_id={job_id} to update")

        except Exception as e:
            print(f"Failed to update job record: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue='job_queue', on_message_callback=callback)

print("Starting to consume...")
channel.start_consuming()
