from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Practice

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Fields to display in the user list page
    list_display = ['id','username', 'email', 'first_name', 'last_name', 'is_staff', 'practice_id', 'practice_superuser']
    
    
admin.site.register(Practice)