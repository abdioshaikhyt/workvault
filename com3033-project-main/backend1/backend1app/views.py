from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Job
from .serializers import JobCreateSerializer
from .producer import send_job_to_backend2
from .producer import send_job_to_backend3

class JobCreateView(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        job_instance = serializer.save()

        print(job_instance.practice_id)

        job_data_for_backend2 = {
            "job_id": job_instance.id,
            "company_name": job_instance.client.company_name,
            "job_selection": job_instance.job_selection,
            "alt_description": job_instance.alt_description,
            "period_end": job_instance.period_end.isoformat() if job_instance.period_end else None,
            "comp_stage": job_instance.comp_stage,
            "practice_id": job_instance.practice_id,
        }

        send_job_to_backend2(job_data_for_backend2, event_type="job_created")

        userjob_data = JobCreateSerializer(job_instance).data

        # Get user ID from task_with_staff if set
        task_with_staff_user = job_instance.task_with_staff
        if task_with_staff_user:
            user_id = task_with_staff_user.staff_id

            # Notify user's websocket group
            notify_jobuser_about_job_change(userjob_data, event="userjob_created", user_id=user_id)

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_jobuser_about_job_change(userjob_data, event, user_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"userb1_{user_id}",
        {
            "type": "job_list",  # this matches consumer async method `send_job_list`
            "jobs": [userjob_data],   # sending a list for consistency, can adjust as needed
            "event": event,
        },
    )



from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Staff
from datetime import datetime

class JobAdvanceStageAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        try:
            job = Job.objects.get(pk=pk, practice_id=request.user.practice_id)
        except Job.DoesNotExist:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        old_task_with_staff = job.task_with_staff
        
        editable_fields = [
            'alt_description',
            'period_start',
            'period_end',
            'partner_staff',
            'reviewer_staff',
            'preparer_staff'
        ]

        updated_fields = {}

        for field in editable_fields:
            if field in request.data:
                value = request.data[field]
                if value == "" or value is None:
                    setattr(job, field, None)
                    updated_fields[field] = None
                elif field.endswith('_staff'):
                    try:
                        staff = Staff.objects.get(staff_id=value)
                        setattr(job, field, staff)
                        updated_fields[field] = value
                    except Staff.DoesNotExist:
                        return Response({"detail": f"Staff id {value} not found."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    setattr(job, field, value)
                    updated_fields[field] = value

        stage_order = [
            Job.StageChoices.NA,
            Job.StageChoices.PLANNING_DRAFT,
            Job.StageChoices.PLANNING_REVIEW,
            Job.StageChoices.COMP_DRAFT,
            Job.StageChoices.COMP_REVIEW,
            Job.StageChoices.TAX_ACCOUNTING_APPROVED,
            Job.StageChoices.FINALISATION_PREP,
            Job.StageChoices.FINALISATION_REVIEW,
            Job.StageChoices.WITH_CLIENT_FOR_APPROVAL,
            Job.StageChoices.APPROVED,
            Job.StageChoices.SUBMITTED,
        ]
        current_index = stage_order.index(job.comp_stage)
        direction = request.data.get('direction', 'forward')
        if direction == 'forward':
            next_index = current_index + 1
        elif direction == 'backward':
            next_index = current_index - 1
        elif direction == 'nochange':
            next_index = current_index
        else:
            return Response({'detail': 'Invalid direction'}, status=status.HTTP_400_BAD_REQUEST)

        if not (0 <= next_index < len(stage_order)):
            return Response({"detail": "Cannot move further in this direction."}, status=status.HTTP_400_BAD_REQUEST)

        new_stage = stage_order[next_index]
        job.comp_stage = new_stage
        updated_fields['comp_stage'] = new_stage

        if new_stage in [
            Job.StageChoices.PLANNING_DRAFT, Job.StageChoices.COMP_DRAFT, Job.StageChoices.FINALISATION_PREP]:
            new_task_with_staff = job.preparer_staff
        else:
            new_task_with_staff = job.reviewer_staff

        job.task_with_staff = new_task_with_staff
       
        if old_task_with_staff != new_task_with_staff:
            
            updated_fields['task_with_staff'] = new_task_with_staff.display_name if new_task_with_staff else None

        job.save()
        
        allowed_fields = {"job_selection", "alt_description", "period_end", "comp_stage"}

        job_data_for_backend2 = {"job_id": job.id, "company_name": job.client.company_name}

        for field in allowed_fields:
            if field in updated_fields:
                value = getattr(job, field, None)
                if field == "period_end":
                    period_end_date = datetime.fromisoformat(value).date()
                    job_data_for_backend2["period_end"] = period_end_date.isoformat() if period_end_date else None
                else:
                    job_data_for_backend2[field] = value
        
        send_job_to_backend2(job_data_for_backend2, event_type="job_updated")

        if direction != 'nochange':
            job_data_for_backend3 = {"job_id": job.id, "new_stage": new_stage, "direction": direction}
            send_job_to_backend3(job_data_for_backend3, event_type="job_updated_for_stage")
        
        userjob_data = JobCreateSerializer(job).data

        new_user = job.task_with_staff
        if new_user:
            notify_jobuser_about_job_change(userjob_data, event="userjob_updated", user_id=new_user.staff_id)

        if old_task_with_staff and (old_task_with_staff != new_user):
            notify_jobuser_about_job_change({"id": job.id}, event="userjob_removed", user_id=old_task_with_staff.staff_id)

        response_data = {"id": job.id}
        response_data.update(updated_fields)

        return Response(response_data)



from .models import Client
from .serializers import ClientSerializer
from rest_framework.pagination import PageNumberPagination

class ClientCreateView(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]


from .serializers import ClientDropdownSerializer, StaffDropdownSerializer
from rest_framework import filters


class ClientResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ClientListAPI(generics.ListAPIView):
    serializer_class = ClientDropdownSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['company_name']  

    def get_queryset(self):
        user = self.request.user
        queryset = Client.objects.filter(practice_id=user.practice_id)
        return queryset


class StaffResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class StaffListAPI(generics.ListAPIView):
    serializer_class = StaffDropdownSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StaffResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['display_name']  

    def get_queryset(self):
        user = self.request.user
        queryset = Staff.objects.filter(practice_id=user.practice_id)
        return queryset
    


class JobChoicesAPI(APIView):
    def get(self, request):
        job_categories = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Job.JobCategory.choices
        ]
        stage_choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Job.StageChoices.choices
        ]
        return Response({
            'job_categories': job_categories,
            'stage_choices': stage_choices,
        })
    

import asyncpg
import asyncio
from asgiref.sync import async_to_sync, sync_to_async
from django.conf import settings
import time
import random
from contextlib import asynccontextmanager

async_pool = None

async def get_pool():
    global async_pool
    if async_pool is None:
        async_pool = await asyncpg.create_pool(
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database=settings.DATABASES['default']['NAME'],
            host=settings.DATABASES['default']['HOST'],
            
            max_size=20,
        )
    return async_pool

@asynccontextmanager
async def acquire_connection_with_retry(pool, max_retries=5, base_delay=0.1):
    delay = base_delay
    connection = None
    try:
        for attempt in range(max_retries):
            try:
                connection = await pool.acquire()
                break
            except (asyncpg.exceptions.TooManyConnectionsError, ConnectionError) as e:
                if attempt == max_retries - 1:
                    raise
                jitter = random.uniform(0, 0.1)
                await asyncio.sleep(delay + jitter)
                delay *= 2
        yield connection
    finally:
        if connection:
            await pool.release(connection)

async def is_token_blacklisted(token: str) -> bool:
    pool = await get_pool()
    async with acquire_connection_with_retry(pool) as connection:
        async with connection.transaction():
            row = await connection.fetchrow(
                "SELECT 1 FROM backend1app_logoutaccesstoken WHERE token = $1 LIMIT 1",
                token
            )
            return row is not None

from rest_framework.permissions import AllowAny
from .models import LogoutAccessToken

class LogoutAndStoreTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return async_to_sync(self.async_get)(request)

    async def async_get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'No access token provided.'}, status=status.HTTP_400_BAD_REQUEST)

        token = auth_header.split('Bearer ')[1]

        #await sync_to_async(LogoutAccessToken.objects.create)(token=token)
        await LogoutAccessToken.objects.acreate(token=token)

        return Response({'detail': 'Access token stored successfully.'}, status=status.HTTP_200_OK)
    



from django.http import Http404
from .serializers import JobSerializer

class JobDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Job.objects.get(pk=pk, practice_id=user.practice_id)
        except Job.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        job = self.get_object(pk, request.user)
        serializer = JobSerializer(job)
        return Response(serializer.data)
    
   
from .serializers import JobSerializer2
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

class JobListView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated] 

    class CustomResultsPagination(PageNumberPagination):
        page_size = 2  
        page_size_query_param = 'page_size'  
        max_page_size = 100  
    
    pagination_class = CustomResultsPagination  

    def list(self, request, *args, **kwargs):
        return async_to_sync(self.async_list)(request, *args, **kwargs)

    async def async_list(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'No access token provided.'}, status=status.HTTP_400_BAD_REQUEST)
        token = auth_header.split('Bearer ')[1]

        if await is_token_blacklisted(token):
            return Response({'detail': 'This token has been logged out.'}, status=status.HTTP_401_UNAUTHORIZED)
               
        auth = JWTStatelessUserAuthentication()

        raw_token = auth.get_raw_token(auth.get_header(request))
        if raw_token is None:
            return Response({"detail": "Authorization header missing or invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            validated_token = auth.get_validated_token(raw_token)
        except InvalidToken:
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = int(validated_token.payload.get('user_id'))
        
        staff_level = request.query_params.get('staff_level')
        if staff_level not in ['reviewer_staff', 'preparer_staff', 'partner_staff']:
            return Response({'detail': 'Invalid staff_level parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pool = await get_pool()
            async with acquire_connection_with_retry(pool) as connection:
                async with connection.transaction():
                    query = f"""
                        SELECT j.id as job_id, j.period_end, j.job_selection, j.comp_stage,
                        c.id, c.company_name
                        FROM backend1app_job j
                        JOIN backend1app_client c ON j.client_id = c.id
                        WHERE j.{staff_level}_id = $1
                    """
                    rows = await connection.fetch(query, user_id)
                    if not rows:
                        return Response({"detail": "No jobs found."}, status=status.HTTP_404_NOT_FOUND)
                    
                    jobs = []
                    for row in rows:
                        period_end = row['period_end']
                        if isinstance(period_end, (str, bytes)):
                            period_end = datetime.strptime(period_end, "%Y-%m-%d").date()
                        formatted_period_end = period_end.strftime("%d/%m/%Y")
                        jobs.append({
                            'id': row['job_id'],
                            'period_end': formatted_period_end,
                            'job_selection': row['job_selection'],
                            'comp_stage': row['comp_stage'],
                            'client': {
                                
                                'company_name': row['company_name'],
                                
                            },
                        })
                    
                    page = self.paginate_queryset(jobs)
                    
                    if page is not None:
                        serializer = JobSerializer2(page, many=True)
                        return self.get_paginated_response(serializer.data)
                    serializer = JobSerializer2(jobs, many=True)
                    return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ClientListView(generics.ListAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated] 
    pagination_class = ClientPagination

    def get_queryset(self):
        user = self.request.user
        return Client.objects.filter(practice_id=user.practice_id)

    def list(self, request, *args, **kwargs):
        return async_to_sync(self.async_list)(request, *args, **kwargs)

    async def async_list(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'No access token provided.'}, status=status.HTTP_400_BAD_REQUEST)
        token = auth_header.split('Bearer ')[1]

        if await is_token_blacklisted(token):
            return Response({'detail': 'This token has been logged out.'}, status=status.HTTP_401_UNAUTHORIZED)
    
        response = await sync_to_async(super().list)(request, *args, **kwargs)
        return response