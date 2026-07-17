from django.contrib import admin

# Register your models here.

from .models import Client, Job, Staff, LogoutAccessToken

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'contact_name', 'contact_email', 'practice_id')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    raw_id_fields = ('partner_staff', 'reviewer_staff', 'preparer_staff', 'task_with_staff')
    list_display = ('id', 'client', 'job_selection', 'alt_description', 'period_start', 'period_end', 
                    'partner_staff', 'reviewer_staff', 'preparer_staff', 'comp_stage', 'practice_id')
    
    

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'staff_id', 'practice_id', 'practice_name')

@admin.register(LogoutAccessToken)
class LogoutAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'logged_out_at')