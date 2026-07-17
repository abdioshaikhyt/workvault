from django.contrib import admin

# Register your models here.
from .models import File, LogoutAccessToken                                                      

@admin.register(File)                                                            
class FileAdmin(admin.ModelAdmin):                                                
    list_display = (                                                               
        'name', 's3_key', 's3_version_id', 'uploaded_at', 'practice_id', 'job_id',   
        'planning_draft_version', 'planning_review_version',                      
        'comp_draft_version', 'comp_review_version',                               
        'tax_accounting_approved_version',                                        
        'finalisation_prep_version', 'finalisation_review_version',             
        'with_client_for_approval_version',                                     
        'approved_version', 'submitted_version',                                
    )           


@admin.register(LogoutAccessToken)               
class LogoutAccessTokenAdmin(admin.ModelAdmin):              
    list_display = ('token', 'logged_out_at') 