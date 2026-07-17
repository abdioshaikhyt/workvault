
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model
from .models import LogoutAccessToken, CustomUser

User = get_user_model()

#Allows access only to staff users or practice superusers.
class IsStaffOrPracticeSuperuser(BasePermission):
    
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        token = auth_header.split('Bearer ')[1]

        if LogoutAccessToken.objects.filter(token=token).exists():
            return False
        
        username = getattr(request.user, 'username', None)
        if not username:
            return False
        try:
            user = User.objects.get(username=username)
            return user.is_staff or user.practice_superuser
        except User.DoesNotExist:
            return False
        
#Allows access only to staff users.
class IsStaff(BasePermission):
  
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        token = auth_header.split('Bearer ')[1]

        if LogoutAccessToken.objects.filter(token=token).exists():
            return False
       
        username = getattr(request.user, 'username', None)
        if not username:
            return False
        try:
            user = User.objects.get(username=username)
            return user.is_staff 
        except User.DoesNotExist:
            return False