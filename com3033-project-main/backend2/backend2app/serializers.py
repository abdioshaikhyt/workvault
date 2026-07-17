from rest_framework import serializers
from datetime import datetime

# Defines an object to be used in JobSearchDocumentSerializer to only allow for period_end to be a date


class DateOnlyField(serializers.DateField):
    def to_representation(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except Exception:
                return None
        if hasattr(value, 'date'):
            value = value.date()
        return super().to_representation(value)

# Defines the serializer for job searching


class JobSearchDocumentSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    company_name = serializers.CharField()
    job_selection = serializers.CharField()
    alt_description = serializers.CharField()
    comp_stage = serializers.CharField()
    period_end = DateOnlyField()
