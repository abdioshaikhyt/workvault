from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Job
from django.core.serializers.json import DjangoJSONEncoder
import logging
logger = logging.getLogger("django.channels")

class UserJobsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close()
            return

        self.group_name = f"userb1_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_initial_jobs()

    @database_sync_to_async
    def get_user_jobs(self, user):
        jobs_qs = Job.objects.filter(task_with_staff=user.id, job_selection="CT_compliance").order_by('client__company_name')
        return list(jobs_qs.values(
        'id',
        'alt_description',
        'comp_stage',
        'job_selection',
        'period_start',
        'period_end',
        'practice_id',
        'client__company_name',
        
    ))

    async def send_initial_jobs(self):
        user = self.scope.get("user")
        jobs = await self.get_user_jobs(user)
        for job in jobs:
            if 'period_start' in job and job['period_start']:
                job['period_start'] = job['period_start'].strftime('%d/%m/%Y')
            if 'period_end' in job and job['period_end']:
                job['period_end'] = job['period_end'].strftime('%d/%m/%Y')
        await self.send(text_data=json.dumps({
            "type": "job_list",
            "event": "initial_load",
            "jobs": jobs,
        }, cls=DjangoJSONEncoder))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def job_list(self, event):
        event_type = event.get("event", "")
        user = self.scope.get("user")
        jobs = await self.get_user_jobs(user)

        if event_type == "userjob_updated":
            # Format dates before sending
            for job in jobs:
                if 'period_start' in job and job['period_start']:
                    job['period_start'] = job['period_start'].strftime('%d/%m/%Y')
                if 'period_end' in job and job['period_end']:
                    job['period_end'] = job['period_end'].strftime('%d/%m/%Y') 
            payload = {
                "type": "job_list",
                "event": "userjob_updated",
                "jobs": jobs,
            }
        elif event_type == "userjob_removed":
            # event['jobs'] holds dict with single job id or list of job ids
            jobs_data = event.get("jobs", None)

            if isinstance(jobs_data, dict):  # single job dict
                job_ids = [jobs_data.get("id")] if jobs_data.get("id") else []
            elif isinstance(jobs_data, list):
                job_ids = [j.get("id") for j in jobs_data if "id" in j]
            else:
                job_ids = []

            payload = {
                "type": "job_list",
                "event": "userjob_removed",
                "job_ids": job_ids,
            }
        else:

            payload = {
                "type": "job_list",
                "event": event_type,
                "jobs": jobs,
            }

        await self.send(text_data=json.dumps(payload, cls=DjangoJSONEncoder))