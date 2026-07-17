from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

@shared_task
def send_reset_password_email_task(user_id, email, token_key, is_active):
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return 

    context = {
        'full_link': None,
        'email_address': email,   
        'active': is_active,
    }

    if is_active:
        sitelink = settings.URL_FOR_PW
        full_link = f"{sitelink}password-reset/{token_key}"
        context['full_link'] = full_link

    html_message = render_to_string("backendauthapp/email.html", context=context)
    plain_message = strip_tags(html_message)

    subject = (
        f"Request for resetting password for {email}"
        if is_active
        else "Email Verification Pending"
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )

    msg.attach_alternative(html_message, "text/html")
    msg.send()

from django.core.management import call_command          

@shared_task                                       
def flush_expired_tokens_task():                     
    call_command('flushexpiredtokens')               

@shared_task                                                            
def delete_all_logout_tokens():                                        
    from .models import LogoutAccessToken                               

    count, _ = LogoutAccessToken.objects.all().delete()               
    print(f"[CELERY TASK] Deleted {count} LogoutAccessToken objects.")    