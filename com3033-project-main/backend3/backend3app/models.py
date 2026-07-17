from django.db import models

# Create your models here.
class File(models.Model):                                                                  
    name = models.CharField(max_length=255)                                               
    s3_key = models.CharField(max_length=255)                                                
    s3_version_id = models.CharField(max_length=255, null=True, blank=True)               
    uploaded_at = models.DateTimeField(auto_now_add=True)                               
    practice_id = models.IntegerField()                                                    
    job_id = models.IntegerField()                                                    
    planning_draft_version = models.BooleanField(null=True, blank=True)                    
    planning_review_version = models.BooleanField(null=True, blank=True)                     
    comp_draft_version = models.BooleanField(null=True, blank=True)                          
    comp_review_version = models.BooleanField(null=True, blank=True)                     
    tax_accounting_approved_version = models.BooleanField(null=True, blank=True)           
    finalisation_prep_version = models.BooleanField(null=True, blank=True)                 
    finalisation_review_version = models.BooleanField(null=True, blank=True)                
    with_client_for_approval_version = models.BooleanField(null=True, blank=True)         
    approved_version = models.BooleanField(null=True, blank=True)                           
    submitted_version = models.BooleanField(null=True, blank=True)                          

    def __str__(self):                                                                
        return self.name                                                    


class LogoutAccessToken(models.Model):                                       
    token = models.CharField(max_length=2048)                      
    logged_out_at = models.DateTimeField(auto_now_add=True)               

    def __str__(self):                                                     
        return f"{self.token}" 