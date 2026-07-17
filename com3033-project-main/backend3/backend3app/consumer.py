import pika
import json
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend3.settings")


import django
django.setup()

from backend3app.models import File

print("Django setup completed.")

print("Connecting to RabbitMQ...")
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='file_queue')
print("Connected and queue declared.")

FORWARD_FIELD_MAPPING = {
    "PLANNING_REVIEW": "planning_draft_version",
    "COMP_DRAFT": "planning_review_version",
    "COMP_REVIEW": "comp_draft_version",
    "TAX_ACCOUNTING_APPROVED": "comp_review_version",
    "FINALISATION_PREP": "tax_accounting_approved_version",
    "FINALISATION_REVIEW": "finalisation_prep_version",
    "WITH_CLIENT_FOR_APPROVAL": "finalisation_review_version",
    "APPROVED": "approved_version",
    "SUBMITTED": "submitted_version"
}

BACKWARD_FIELD_MAPPING = {
    "PLANNING_DRAFT": "planning_draft_version",
    "PLANNING_REVIEW": "planning_review_version",
    "COMP_DRAFT": "comp_draft_version",
    "COMP_REVIEW": "comp_review_version",
    "TAX_ACCOUNTING_APPROVED": "tax_accounting_approved_version",
    "FINALISATION_PREP": "finalisation_prep_version",
    "FINALISATION_REVIEW": "finalisation_review_version",
    "WITH_CLIENT_FOR_APPROVAL": "approved_version",
    "APPROVED": "approved_version",
    "APPROVED": "submitted_version",
}


def set_version_flag(job_id, new_stage, direction):
    print(f"DEBUG: job_id={job_id}, new_stage={new_stage}, direction={direction}")
    if direction == "forward":
        field = FORWARD_FIELD_MAPPING.get(new_stage.upper())
        value = True
    elif direction == "backward":
        field = BACKWARD_FIELD_MAPPING.get(new_stage.upper())
        value = False
    else:
        print("DEBUG: direction did not match forward/backward")
        return

    print(f"DEBUG: selected field: {field}, value to set: {value}")
    if field is None:
        print("DEBUG: Field mapping not found for given stage/direction.")
        return

    if direction == "backward":
        # Set all files' specified field to False in backward direction
        files_to_update = File.objects.filter(job_id=job_id)
        print(f"DEBUG: number of files to update: {files_to_update.count()}")
        for file_obj in files_to_update:
            print(f"DEBUG: Before update {field} for file {file_obj.name}: {getattr(file_obj, field)}")
            setattr(file_obj, field, value)
            file_obj.save()
            file_obj.refresh_from_db()
            print(f"DEBUG: After update {field} for file {file_obj.name}: {getattr(file_obj, field)}")
    else:
        # For forward direction, update only latest files (as original)
        from django.db.models import Max
        latest_files = (
            File.objects
            .filter(job_id=job_id)
            .values('name')
            .annotate(latest_upload=Max('uploaded_at'))
        )
    print(f"DEBUG: latest_files queryset: {list(latest_files)}") 
    for entry in latest_files:
        print(f"DEBUG: entry: {entry}")
        file_obj = File.objects.filter(
            job_id=job_id,
            name=entry['name'],
            uploaded_at=entry['latest_upload']
        ).first()
        if file_obj:
            print(f"DEBUG: Before update {field}: {getattr(file_obj, field)}")
            setattr(file_obj, field, value)
            file_obj.save()
            # Reload from DB to check persisted value
            file_obj.refresh_from_db()
            print(f"DEBUG: After update {field}: {getattr(file_obj, field)}")
        else:
            print(f"DEBUG: No File instance for: job_id={job_id}, name={entry['name']}, uploaded_at={entry['latest_upload']}")


def callback(ch, method, properties, body):
    print(f"Received message: {body}")
    try:
        data = json.loads(body.decode())
    except Exception as e:
        print(f"Failed to decode JSON: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    event_type = data.get("event_type")
    file_data = data.get("file")

    print(f"Event type: {event_type}")
    print(f"File data: {file_data}")

    if event_type == "job_updated_for_stage":
        try:
            job_id = file_data.get("job_id")
            new_stage = file_data.get("new_stage")
            direction = file_data.get("direction")
            if job_id and new_stage and direction:
                set_version_flag(job_id, new_stage, direction)
                print(f"Updated Job FILES objects with ID: {job_id}")
        except Exception as e:
            print(f"Failed to update version flags: {e}")
        

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='file_queue', on_message_callback=callback)

print("Starting to consume...")
channel.start_consuming()