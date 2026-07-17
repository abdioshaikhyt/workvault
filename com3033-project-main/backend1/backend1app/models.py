from django.db import models

# Create your models here.
class Staff(models.Model):
    display_name = models.CharField(max_length=50)
    staff_id = models.IntegerField(primary_key=True)
    practice_id = models.IntegerField()
    practice_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.practice_name

class Client(models.Model):
    company_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    practice_id = models.IntegerField()

    def __str__(self):
        return self.company_name

class Job(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    alt_description = models.TextField(max_length=100, blank=True, null=True)
    period_start = models.DateField()
    period_end = models.DateField()
    partner_staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='partner_jobs')
    reviewer_staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='reviewer_jobs')
    preparer_staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='preparer_jobs')
    practice_id = models.IntegerField()
    task_with_staff = models.ForeignKey(
        'Staff',
        on_delete=models.CASCADE,
        related_name='task_with_jobs',
        blank=True,
        null=True
    )

    class JobCategory(models.TextChoices):
        CT_COMPLIANCE = 'CT_compliance', 'CT compliance'
        CT_ADVISORY = 'CT_advisory', 'CT advisory'
        GENERAL = 'General', 'General'
        R_AND_D = 'R&D', 'R&D'
        TAX_AUDIT = 'Tax_audit', 'Tax audit'
        TAX_DD = 'Tax_DD', 'Tax DD'

    job_selection = models.CharField(
        max_length=20,
        choices=JobCategory.choices,
    )

    class StageChoices(models.TextChoices):
        NA = 'NA', 'N/A'
        PLANNING_DRAFT = 'Planning_draft', 'Planning draft'
        PLANNING_REVIEW = 'Planning_review', 'Planning review'
        COMP_DRAFT = 'Comp_draft', 'Comp draft'
        COMP_REVIEW = 'Comp_review', 'Comp review'
        TAX_ACCOUNTING_APPROVED = 'Tax_accounting_approved', 'Tax accounting approved'
        FINALISATION_PREP = 'Finalisation_prep', 'Finalisation prep'
        FINALISATION_REVIEW = 'Finalisation_review', 'Finalisation review'
        WITH_CLIENT_FOR_APPROVAL = 'With_Client_for_approval', 'With Client for approval'
        APPROVED = 'Approved', 'Approved'
        SUBMITTED = 'Submitted', 'Submitted'

    comp_stage = models.CharField(
        max_length=30,
        choices=StageChoices.choices,
        default=StageChoices.NA,
        
    )

    def __str__(self):
        return f"Job {self.id} for client {self.client}"

class LogoutAccessToken(models.Model):
    token = models.CharField(max_length=2048)
    logged_out_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.token}"