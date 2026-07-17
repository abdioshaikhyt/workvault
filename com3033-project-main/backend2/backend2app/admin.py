from django.contrib import admin

from .models import JobSearch, LogoutAccessToken

# Defines the admin model used for search for jobs


@admin.register(JobSearch)
class JobSearchAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'company_name', 'job_selection',
                    'period_end', 'comp_stage', 'practice_id')

# Defines the admin model used to track used auth tokens


@admin.register(LogoutAccessToken)
class LogoutAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'logged_out_at')
