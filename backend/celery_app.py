"""Celery application and tasks."""
from celery import Celery
from celery.schedules import crontab
from config import settings

# Initialize Celery
celery_app = Celery(
    "unjobs",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "crawl-un-careers-daily": {
        "task": "celery_app.crawl_un_careers",
        "schedule": crontab(hour=2, minute=0),  # Run at 2 AM UTC daily
    },
    "crawl-undp-daily": {
        "task": "celery_app.crawl_undp_jobs",
        "schedule": crontab(hour=3, minute=0),  # Run at 3 AM UTC daily
    },
    "crawl-unicef-daily": {
        "task": "celery_app.crawl_unicef_jobs",
        "schedule": crontab(hour=4, minute=0),  # Run at 4 AM UTC daily
    },
    "crawl-uncareer-daily": {
        "task": "celery_app.crawl_uncareer_jobs",
        "schedule": crontab(hour=5, minute=0),  # Run at 5 AM UTC daily
    },
}


@celery_app.task(name="celery_app.crawl_un_careers")
def crawl_un_careers():
    """Crawl UN Careers website."""
    from crawlers.un_careers_spider import crawl_un_careers_sync
    return crawl_un_careers_sync()


@celery_app.task(name="celery_app.crawl_undp_jobs")
def crawl_undp_jobs():
    """Crawl UNDP jobs website."""
    from crawlers.undp_spider import crawl_undp_sync
    return crawl_undp_sync()


@celery_app.task(name="celery_app.crawl_unicef_jobs")
def crawl_unicef_jobs():
    """Crawl UNICEF careers website."""
    from crawlers.unicef_spider import crawl_unicef_sync
    return crawl_unicef_sync()


@celery_app.task(name="celery_app.crawl_uncareer_jobs")
def crawl_uncareer_jobs():
    """Crawl uncareer.net for UN jobs and internships."""
    from crawlers.uncareer_spider import crawl_uncareer_sync
    # Crawl both internships and jobs
    result_internships = crawl_uncareer_sync(max_pages=10, tag="internship")
    result_jobs = crawl_uncareer_sync(max_pages=10, tag="job")
    return {
        "internships": result_internships,
        "jobs": result_jobs
    }


@celery_app.task(name="celery_app.send_job_alerts")
def send_job_alerts():
    """Send job alert emails to users based on their subscriptions."""
    # TODO: Implement job alert sending logic
    pass



