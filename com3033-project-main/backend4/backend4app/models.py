from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=255)  
    date = models.DateTimeField(null=True, blank=True)
    date_special = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
                                
    link = models.URLField(max_length=500)    
    cpd_hours = models.DecimalField(          
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )
    course_type = models.CharField(         
        max_length=100,
        null=True,
        blank=True
    )
    date_scrapy_saved = models.DateTimeField( 
        auto_now=True
    )

    def __str__(self):
        return f"{self.title} ({self.date})"

    class Meta:
        ordering = ['date']

class LogoutAccessToken(models.Model):                           
    token = models.CharField(max_length=2048)                    
    logged_out_at = models.DateTimeField(auto_now_add=True)      

    def __str__(self):                                           
        return f"{self.token}"                                   