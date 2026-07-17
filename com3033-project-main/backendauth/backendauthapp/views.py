from django.shortcuts import render
from rest_framework import generics
from .serializers import UserSerializer
from .serializers import PracticeSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Practice
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import asyncpg
import asyncio
from asgiref.sync import async_to_sync, sync_to_async
from contextlib import asynccontextmanager
import random  

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    def perform_create(self, serializer):
        instance = serializer.save()
        from .serializers import UserSerializer
        user_data = UserSerializer(instance).data
        notify_admins_about_user_change(user_data, event="user_created")
        
        data_to_send = {
        "display_name": f"{instance.first_name} {instance.last_name}".strip(),
        "staff_id": str(instance.id),
        "practice_id": instance.practice_id.id if instance.practice_id else None,
        "practice_name": instance.practice_id.practice_name if instance.practice_id else None,
        }

        from .producer import send_user_to_backend1
        send_user_to_backend1(data_to_send, event_type="create")
        
        subject = "Welcome to WorkVault!"
        body = "Hi {},\n\nThank you for registering with WorkVault.\n\nBest,\nThe WorkVault Team".format(instance.username)  
        html_content = """                   
        <html>
        <body>
            <p>Hi {},</p>
            <p>Thank you for registering with <strong>WorkVault</strong>.</p>
            <p>Best,<br>The WorkVault Team</p>
        </body>
        </html>          
        """.format(instance.username)        

        from_email = None                  
        to_email = [instance.email]        

        msg = EmailMultiAlternatives(subject, body, from_email, to_email)   
        msg.attach_alternative(html_content, "text/html")                   
        msg.send(fail_silently=False)                                        

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
                "SELECT 1 FROM backendauthapp_logoutaccesstoken WHERE token = $1 LIMIT 1",
                token
            )
            return row is not None
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .models import LogoutAccessToken

class LogoutAndBlacklistJWTTokens(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return async_to_sync(self.async_post)(request)

    async def async_post(self, request):

        print("received logout request")
        print("request.data:", request.data)
        refresh_token = request.data.get("refresh")
        auth_header = request.headers.get('Authorization')                                                           
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'No access token provided.'}, status=status.HTTP_400_BAD_REQUEST)

        token = auth_header.split('Bearer ')[1]
        await LogoutAccessToken.objects.acreate(token=token)

        if not refresh_token:
            return Response({"detail": "No refresh token provided, but logout successful."}, status=status.HTTP_200_OK)
    
        try:
            r_token = await sync_to_async(RefreshToken)(refresh_token)
            print("blacklisting try!")
            await sync_to_async(r_token.blacklist)()
            return Response({"detail": "Refresh token blacklisted."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication                    
from rest_framework_simplejwt.exceptions import InvalidToken                                          

class DisplayUsernameView(APIView):                                                   
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
        auth = JWTStatelessUserAuthentication()                                                  
        raw_token = auth.get_raw_token(auth.get_header(request))                                                          
        if raw_token is None:                                                                                             
            return Response({"detail": "Authorization header missing or invalid"}, status=status.HTTP_401_UNAUTHORIZED)   
        try:                                                                                     
            validated_token = auth.get_validated_token(raw_token)                                
        except InvalidToken:                                                                     
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)    
        user_id_token = int(validated_token.payload.get('user_id'))                            
        try:                                                                                    
            pool = await get_pool()                                                             
            async with acquire_connection_with_retry(pool) as connection:                        
                async with connection.transaction():                                             
                    row = await connection.fetchrow('SELECT first_name || \' \' || last_name AS display_name FROM backendauthapp_customuser WHERE id = $1', user_id_token)  
                    if not row:                                                                                      
                        return Response({"detail": "No books found."}, status=status.HTTP_404_NOT_FOUND)                          
            data = dict(row)                                                                                               
            return Response(data, status=status.HTTP_200_OK)                                                          
        except Exception as e:                                                                                         
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)                         


from .serializers import UserUpdateSerializer                       
from .permissions import IsStaffOrPracticeSuperuser                     
from rest_framework.pagination import PageNumberPagination              

class UserResultsSetPagination(PageNumberPagination):             
    page_size = 10                                            
    page_size_query_param = 'page_size'                         
    max_page_size = 100                                           
    
class UserListView(generics.ListAPIView):                      
    serializer_class = UserUpdateSerializer                        
    permission_classes = [IsStaffOrPracticeSuperuser]              
    pagination_class = UserResultsSetPagination                    
 
    def get_queryset(self):                                      
        user = self.request.user                                  
        queryset = User.objects.all()                            
        
        if not user.is_staff:                                             
            if getattr(user, 'practice_superuser', False):                 
                queryset = queryset.filter(practice_id=user.practice_id)   
            else:                                                          
                queryset = queryset.none()                                   
        return queryset                                                      

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
    

class UserUpdateView(generics.UpdateAPIView):                        
    queryset = User.objects.all()                                  
    serializer_class = UserUpdateSerializer                        
    permission_classes = [IsStaffOrPracticeSuperuser]               
    def perform_update(self, serializer):                         
        instance = self.get_object()                               
        original_data = UserUpdateSerializer(instance).data.copy()   

        updated_instance = serializer.save()                             
        updated_data = UserUpdateSerializer(updated_instance).data       

        changed_fields = {}                                   
        for key in updated_data:                                    
            if updated_data[key] != original_data[key]:             
                changed_fields[key] = updated_data[key]             

        changed_fields['id'] = updated_instance.id                    

        notify_admins_about_user_change(changed_fields, event="user_updated")    

        is_active_changed_to_false = (                          
            'is_active' in changed_fields                              
            and original_data.get('is_active') == True                 
            and updated_data['is_active'] == False                     
        )                                                              
        is_staff_changed_to_false = (                                  
            'is_staff' in changed_fields                            
            and original_data.get('is_staff') == True                 
            and updated_data['is_staff'] == False                   
        )                                                              

        requesting_user_id = self.request.user.id                                                 
        print(f"requesting user is {requesting_user_id} and updating is {updated_instance.id}")   

        if is_active_changed_to_false or is_staff_changed_to_false:                               
            if int(updated_instance.id) != int(requesting_user_id):                                                           
                print(f"[UserUpdateView] User {updated_instance.id} had is_active/is_staff unset - notifying force logout")   
                notify_force_logout(updated_instance.id)                                                                     



from channels.layers import get_channel_layer                               
from asgiref.sync import async_to_sync                                      

def notify_admins_about_user_change(user_data, event):               
    channel_layer = get_channel_layer()                              
    async_to_sync(channel_layer.group_send)(                       
        "users",                                                     
        {                                                          
            "type": "user_update",                              
            "data": {                                              
                "event": event,                                    
                "user": user_data,                                
            },                                                   
        },                                                         
    )                                                               

def notify_admins_about_practice_change(practice_data, event):             
    print("Notifying admins via websocket with:", practice_data, event)   
    channel_layer = get_channel_layer()                                  
    async_to_sync(channel_layer.group_send)(                             
        "users",                                                    
        {                                                          
            "type": "practice_update",                              
            "data": {                                                
                "event": event,                                     
                "practice": practice_data,                          
            },                                                        
        },                                                           
    )                                                                

from asgiref.sync import async_to_sync                                
from channels.layers import get_channel_layer                         

def notify_force_logout(user_id):                                     
    channel_layer = get_channel_layer()                                
    print(f"[notify_force_logout] Sending force_logout to user_id={user_id}")       
    async_to_sync(channel_layer.group_send)(                                        
        f"user_{user_id}",                                                                  
        {                                                                                   
            "type": "force_logout",                                                        
            "message": "Your account permissions have changed. You have been logged out.",   
            "user_id": user_id,                                                             
        },                                                                                  
    )                                                                                      
from django_rest_passwordreset.views import ResetPasswordRequestToken        
from django_rest_passwordreset.serializers import EmailSerializer           
from django_rest_passwordreset.signals import reset_password_token_created   

class CustomPasswordResetRequestView(ResetPasswordRequestToken):         
    def post(self, request, *args, **kwargs):                           
        serializer = EmailSerializer(data=request.data)               
        serializer.is_valid(raise_exception=True)                        

        email = serializer.validated_data['email']                      
        users = User.objects.filter(email__iexact=email)                

        for user in users:                                               
            self._send_reset_email(user)                                 

        return Response(                                                                           
            {"detail": "You will receive an email with instructions on how to reset your password."},    
            status=status.HTTP_200_OK                                                                    
        )                                                                                              

    def _send_reset_email(self, user):                               
        from django_rest_passwordreset.models import ResetPasswordToken      
        token = ResetPasswordToken.objects.create(user=user)              
        reset_password_token_created.send(                                
            sender=self.__class__,                                      
            instance=self,                                             
            reset_password_token=token,                                 
            request=self.request                                        
        )                                                               

from django_rest_passwordreset.models import ResetPasswordToken            
from datetime import timedelta                                             
from django.utils import timezone                                           

TOKEN_EXPIRY_HOURS = getattr(settings, 'DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME', 24)  

class ValidateResetTokenView(APIView):                             
    permission_classes = [AllowAny]                                
    authentication_classes = []                                  
    def post(self, request):                                        
        token_key = request.data.get("token")                        
        if not token_key:                                          
            return Response({"detail": "Token not provided."}, status=status.HTTP_400_BAD_REQUEST)     

        try:                                                                                
            token_obj = ResetPasswordToken.objects.get(key=token_key)                       
        except ResetPasswordToken.DoesNotExist:                                          
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)   

        token_age = timezone.now() - token_obj.created_at                                   
        if token_age > timedelta(hours=TOKEN_EXPIRY_HOURS):                               
            token_obj.delete()                                                             
            return Response({"detail": "Token expired."}, status=status.HTTP_400_BAD_REQUEST)   

        return Response({"detail": "Token valid."}, status=status.HTTP_200_OK)               

from .permissions import IsStaff                                     

class PracticeCreateView(generics.CreateAPIView):
    queryset = Practice.objects.all()
    serializer_class = PracticeSerializer
    permission_classes = [IsStaff, IsAuthenticated]                     

    def perform_create(self, serializer):
        instance = serializer.save()
        from .serializers import PracticeSerializer                                
        practice_data = PracticeSerializer(instance).data                          
        notify_admins_about_practice_change(practice_data, event="practice_created")  

class PracticeResultsSetPagination(PageNumberPagination):             
    page_size = 10                                                   
    page_size_query_param = 'page_size'                               
    max_page_size = 100                                                 

class PracticeListView(generics.ListAPIView):                          
    queryset = Practice.objects.all()                                  
    serializer_class = PracticeSerializer                               
    permission_classes = [IsStaff]                                     
    pagination_class = PracticeResultsSetPagination                     

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






