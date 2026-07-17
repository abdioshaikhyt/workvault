from rest_framework import serializers

class CoursesSerializer(serializers.Serializer):
    title = serializers.CharField()
    date = serializers.DateTimeField(allow_null=True, required=False)
    date_special = serializers.CharField(allow_blank=True, required=False)
    link = serializers.URLField()
    cpd_hours = serializers.DecimalField(max_digits=4, decimal_places=2, required=False, allow_null=True)
    course_type = serializers.CharField(allow_blank=True, required=False)
