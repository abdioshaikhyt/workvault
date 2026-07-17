from celery import shared_task
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from .models import Course, LogoutAccessToken 
from django.utils import timezone
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@shared_task                                                               
def delete_all_logout_tokens():                                            
    count, _ = LogoutAccessToken.objects.all().delete()                    
    print(f"[CELERY TASK] Deleted {count} LogoutAccessToken objects.")

@shared_task
def run_courses_spider():
    logger.info("=== Celery task STARTED: run_courses_spider ===")
    try:
       
        script_path = Path(__file__).resolve().parent / "run_courses_spider_script.py"

        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Script stdout:\n" + result.stdout)
        if result.stderr:
            logger.error("Script stderr:\n" + result.stderr)
        
        remove_old_rows.delay()

        return "Spider run completed successfully."

    except subprocess.CalledProcessError as e:
        logger.error("Script execution failed:")
        logger.error(e.stderr)
        return f"Spider run failed: {e.stderr}"


@shared_task
def remove_old_rows():
    ten_minutes_ago = timezone.now() - timedelta(minutes=10)
    deleted_count, _ = Course.objects.filter(date_scrapy_saved__lt=ten_minutes_ago).delete()
    logger.info(f"Removed {deleted_count} rows older than 10 minutes.")