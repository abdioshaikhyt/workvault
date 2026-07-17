from django.contrib.auth.models import AbstractUser
from django.db import models


class Practice(models.Model):
    practice_name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.practice_name
    

class CustomUser(AbstractUser):
    practice_id = models.ForeignKey(Practice, null=True, blank=True, on_delete=models.SET_NULL)
    practice_superuser = models.BooleanField(default=False)

class LogoutAccessToken(models.Model):
    token = models.CharField(max_length=2048)
    logged_out_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.token}"
   
from django_rest_passwordreset.signals import reset_password_token_created     
from django.dispatch import receiver                                         

from backendauthapp.tasks import send_reset_password_email_task             

@receiver(reset_password_token_created)                                     
def password_reset_token_created(reset_password_token, *args, **kwargs):      
    send_reset_password_email_task.delay(                                     
        user_id=reset_password_token.user.id,                                   
        email=reset_password_token.user.email,                                 
        token_key=reset_password_token.key,                                    
        is_active=reset_password_token.user.is_active                          
    )                                                                        
