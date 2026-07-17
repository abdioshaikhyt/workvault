from django.contrib import admin

# Register your models here.

from .models import Course, LogoutAccessToken

@admin.register(Course)                                                                                  
class CourseAdmin(admin.ModelAdmin):                                                                     
    list_display = ('title', 'date', 'date_special', 'link', 'cpd_hours', 'course_type', 'date_scrapy_saved')

@admin.register(LogoutAccessToken)                           
class LogoutAccessTokenAdmin(admin.ModelAdmin):              
    list_display = ('token', 'logged_out_at')                