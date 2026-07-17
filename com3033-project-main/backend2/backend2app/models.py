from django.db import models

# Defines the model used for searching


class JobSearch(models.Model):
    job_id = models.IntegerField(primary_key=True)
    company_name = models.CharField(max_length=100)
    job_selection = models.CharField(max_length=20)
    alt_description = models.TextField(null=True, blank=True)
    period_end = models.DateField()
    comp_stage = models.CharField(max_length=30)
    practice_id = models.IntegerField()

# Defines the model used to track auth tokens


class LogoutAccessToken(models.Model):
    token = models.CharField(max_length=2048)
    logged_out_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.token}"
