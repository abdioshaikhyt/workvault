from rest_framework import serializers
from .models import Job

class JobCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Job
        fields = [
            'id', 'client', 'alt_description', 'period_start', 'period_end',
            'partner_staff', 'reviewer_staff', 'preparer_staff',
            'practice_id', 'job_selection', 'comp_stage', 'task_with_staff'
        ]
        read_only_fields = ['comp_stage']

from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'company_name', 'contact_name', 'contact_email', 'practice_id']

class ClientDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'company_name']

from .models import Staff

class StaffDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['staff_id', 'display_name']

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['staff_id', 'display_name']

class JobSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    partner_staff = StaffSerializer()
    reviewer_staff = StaffSerializer()
    preparer_staff = StaffSerializer()
    task_with_staff = StaffSerializer(allow_null=True)
    class Meta:
        model = Job
        fields = [
            'id', 'client', 'alt_description', 'period_start', 'period_end',
            'partner_staff', 'reviewer_staff', 'preparer_staff',
            'practice_id', 'job_selection', 'comp_stage', 'task_with_staff'
        ]
        read_only_fields = ['comp_stage', 'task_with_staff']

class ClientSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['company_name']
        
class JobSerializer2(serializers.ModelSerializer):
    client = ClientSerializer2()
    
    class Meta:
        model = Job
        fields = [
            'id', 'client', 'period_end',
             'job_selection', 'comp_stage'
        ]