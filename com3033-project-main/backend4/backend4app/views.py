from django.shortcuts import render

# Create your views here.
from asgiref.sync import async_to_sync, sync_to_async
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
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

        await LogoutAccessToken.objects.acreate(token=token)

        return Response({'detail': 'Access token stored successfully.'}, status=status.HTTP_200_OK)
    

import asyncpg
import asyncio
from asgiref.sync import async_to_sync, sync_to_async
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
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
    attempt = 0
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
                "SELECT 1 FROM backend4app_logoutaccesstoken WHERE token = $1 LIMIT 1",
                token
            )
            return row is not None

from .serializers import CoursesSerializer                              
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination                

class CoursesAPIView(APIView, LimitOffsetPagination):                                          
    serializer_class = CoursesSerializer                                
    permission_classes = [IsAuthenticated]                              

    def get(self, request):                                             
        return async_to_sync(self.async_get)(request)                   

    async def async_get(self, request):                                 
        auth_header = request.headers.get('Authorization')              

        if not auth_header or not auth_header.startswith('Bearer '):                                         
            return Response({'detail': 'No access token provided.'}, status=status.HTTP_400_BAD_REQUEST)     
        token = auth_header.split('Bearer ')[1]                                                              

        if await is_token_blacklisted(token):                                                                    
            return Response({'detail': 'This token has been logged out.'}, status=status.HTTP_401_UNAUTHORIZED)  

        try: 
            offset = int(request.GET.get('offset', 0))                
            limit = int(request.GET.get('limit', 5)) 
                                                             
            ordering = request.GET.get('ordering', 'date')                  
            if ordering not in ['date', '-date']:                           
                ordering = 'date'                                           

            if ordering == 'date':                                          
                order_sql = 'date ASC NULLS LAST'                           
            else:                                                           
                order_sql = 'date DESC NULLS LAST'                          

            pool = await get_pool()                                            
            async with acquire_connection_with_retry(pool) as connection:      
                async with connection.transaction(): 
                    
                    total_count_result = await connection.fetchrow('SELECT COUNT(*) FROM backend4app_course') 
                    total_count = total_count_result['count']
          
                    courses = await connection.fetch(f'''                            
                        SELECT id, title, date, date_special, link, cpd_hours, course_type
                        FROM backend4app_course
                        ORDER BY {order_sql}
                        OFFSET $1 LIMIT $2 
                    ''', offset, limit)                                                      

            courses_list = [dict(course) for course in courses]               

            serializer = self.serializer_class(courses_list, many=True)       
            return Response({                                                 
                'count': total_count,                                         
                'offset': offset,                                             
                'limit': limit,                                               
                'results': serializer.data,                                   
            })                                                                

        except Exception as e:                                                
            return Response({'detail': str(e)}, status=500)                   
