from celery import shared_task
from .models import LogoutAccessToken

@shared_task
def delete_all_logout_tokens():
    count, _ = LogoutAccessToken.objects.all().delete()
    print(f"[CELERY TASK] Deleted {count} LogoutAccessToken objects.")