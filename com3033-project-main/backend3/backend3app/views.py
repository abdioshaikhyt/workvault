from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import File
import boto3
from asgiref.sync import async_to_sync, sync_to_async                               
from rest_framework.permissions import AllowAny, IsAuthenticated                        
from rest_framework import status                                     
from .models import LogoutAccessToken 
import asyncpg                                                               
import asyncio 
import random 
from contextlib import asynccontextmanager


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk, format=None):
        return self._post(request, pk, format)
    
    def _post(self, request, pk, format=None):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=401)
        
        files = request.FILES.getlist('files')
        practice_id = request.data.get('practice_id', None)
        results = []

        if not files:
            return Response({'error': 'No files uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        if practice_id is None:
            return Response({'error': 'practice_id is required in form data'}, status=status.HTTP_400_BAD_REQUEST)

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_UPLOAD_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_UPLOAD_SECRET_KEY,
            region_name=settings.AWS_UPLOAD_REGION,
        )
        bucket = settings.AWS_UPLOAD_BUCKET
        
        for file_obj in files:
            s3_key = f'uploads/{pk}/{file_obj.name}'

            response = s3.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=file_obj
            )
            
            version_id = response.get('VersionId')

            # Save metadata in DB
            file_record = File.objects.create(
                name=file_obj.name,
                practice_id=practice_id,
                job_id=pk,
                s3_key=s3_key,
                s3_version_id=version_id,
                planning_draft_version=None,
                planning_review_version=None,
                comp_draft_version=None,
                comp_review_version=None,
                tax_accounting_approved_version=None,
                finalisation_prep_version=None,
                finalisation_review_version=None,
                with_client_for_approval_version=None,
                approved_version=None,
                submitted_version=None,
            )

            results.append({
                'id': file_record.id,
                'name': file_record.name,
                's3_key': file_record.s3_key,
                's3_version_id': file_record.s3_version_id,
            })
        
        return Response(
            {'message': 'Files uploaded successfully', 'files': results},
            status=status.HTTP_201_CREATED
        )

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
                "SELECT 1 FROM backend3app_logoutaccesstoken WHERE token = $1 LIMIT 1",      
                token                                                                   
            )                                                                          
            return row is not None  


from django.db.models import OuterRef, Subquery                                    

class FileListView(APIView):                                                         
    permission_classes = [IsAuthenticated]                                             

    def get(self, request, pk, format=None):                                           
        return async_to_sync(self.async_get)(request, pk, format)                     

    async def async_get(self, request, pk, format=None):                                       
        auth_header = request.headers.get('Authorization')                                      
        
        if not auth_header or not auth_header.startswith('Bearer '):                                      
            return Response({'detail': 'No access token provided.'}, status=status.HTTP_400_BAD_REQUEST)  
        token = auth_header.split('Bearer ')[1]                                                             

        if await is_token_blacklisted(token):                                                                
            return Response({'detail': 'This token has been logged out.'}, status=status.HTTP_401_UNAUTHORIZED)   
        
        s3 = boto3.client(                                                                      
            's3',                                                                              
            aws_access_key_id=settings.AWS_UPLOAD_ACCESS_KEY_ID,                                   
            aws_secret_access_key=settings.AWS_UPLOAD_SECRET_KEY,                         
            region_name=settings.AWS_UPLOAD_REGION,                                               
        )                                                                                    
        bucket = settings.AWS_UPLOAD_BUCKET                                                  
        
        latest_files_subquery = File.objects.filter(                                        
            name=OuterRef('name'),                                                         
            job_id=pk                                                             
        ).order_by('-uploaded_at').values('pk')[:1]                                         

        # Filter files to only those for this job and pick latest per name                                   
        files_qs = File.objects.filter(job_id=pk, pk__in=Subquery(latest_files_subquery))      
        files = await sync_to_async(list)(files_qs)                                       

        result = []                                                             
        for f in files:                                                     
            url = s3.generate_presigned_url(                                
                'get_object',                                                     
                Params={'Bucket': bucket, 'Key': f.s3_key, 'VersionId': f.s3_version_id},       
                ExpiresIn=86400                                                       
            )                                                                      
            result.append({'id': f.id, 'name': f.name, 'url': url})                
        return Response(result)                                                         



class FileStageListView(APIView):                   
    permission_classes = [IsAuthenticated]                            

    def get(self, request, pk, format=None):                                               
        stage_field = request.query_params.get('stage', '')                                 
        if not stage_field:                                                                    
            return Response({'detail': 'stage parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)     

        return async_to_sync(self.async_get)(request, pk, stage_field, format)                  

    async def async_get(self, request, pk, stage_field, format=None):                                
        auth_header = request.headers.get('Authorization')                                            

        if not auth_header or not auth_header.startswith('Bearer '):                                  
            return Response({'detail': 'No access token provided.'}, status=status.HTTP_400_BAD_REQUEST)    
        token = auth_header.split('Bearer ')[1]                                                          

        if await is_token_blacklisted(token):                                                      
            return Response({'detail': 'This token has been logged out.'}, status=status.HTTP_401_UNAUTHORIZED)  

        s3 = boto3.client(                                                                     
            's3',                                                                         
            aws_access_key_id=settings.AWS_UPLOAD_ACCESS_KEY_ID,                                
            aws_secret_access_key=settings.AWS_UPLOAD_SECRET_KEY,                  
            region_name=settings.AWS_UPLOAD_REGION,                               
        )                                                                               
        bucket = settings.AWS_UPLOAD_BUCKET                                        

        files_qs = File.objects.filter(                                                   
            job_id=pk,                                                                        
            **{stage_field: True}                                                            
        )                                                                                   

        files = await sync_to_async(list)(files_qs)                                               

        result = []                                                                             
        for f in files:                                                                             
            url = s3.generate_presigned_url(                                              
                'get_object',                                                                        
                Params={'Bucket': bucket, 'Key': f.s3_key, 'VersionId': f.s3_version_id},            
                ExpiresIn=86400                                                                   
            )                                                                              
            result.append({'id': f.id, 'name': f.name, 'url': url})                              

        return Response(result)   