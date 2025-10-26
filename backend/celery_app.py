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
    "crawl-un-careers-official-daily": {
        "task": "celery_app.crawl_un_careers_official",
        "schedule": crontab(hour=1, minute=0),  # Run at 1 AM UTC daily
    },
    "crawl-uncareer-daily": {
        "task": "celery_app.crawl_uncareer_jobs",
        "schedule": crontab(hour=2, minute=0),  # Run at 2 AM UTC daily
    },
    "crawl-who-daily": {
        "task": "celery_app.crawl_who_jobs",
        "schedule": crontab(hour=3, minute=0),  # Run at 3 AM UTC daily
    },
    "crawl-fao-daily": {
        "task": "celery_app.crawl_fao_jobs",
        "schedule": crontab(hour=4, minute=0),  # Run at 4 AM UTC daily
    },
    "crawl-unops-daily": {
        "task": "celery_app.crawl_unops_jobs",
        "schedule": crontab(hour=5, minute=0),  # Run at 5 AM UTC daily
    },
    "crawl-ilo-daily": {
        "task": "celery_app.crawl_ilo_jobs",
        "schedule": crontab(hour=6, minute=0),  # Run at 6 AM UTC daily
    },
    "crawl-undp-daily": {
        "task": "celery_app.crawl_undp_jobs",
        "schedule": crontab(hour=7, minute=0),  # Run at 7 AM UTC daily
    },
    "crawl-unicef-daily": {
        "task": "celery_app.crawl_unicef_jobs",
        "schedule": crontab(hour=8, minute=0),  # Run at 8 AM UTC daily
    },
}


@celery_app.task(name="celery_app.crawl_un_careers_official")
def crawl_un_careers_official():
    """Crawl UN Careers official website (careers.un.org)."""
    from crawlers.un_careers_official_spider import crawl_un_careers_official_sync
    return crawl_un_careers_official_sync(max_jobs=50)


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


@celery_app.task(name="celery_app.crawl_who_jobs")
def crawl_who_jobs():
    """Crawl WHO (World Health Organization) jobs."""
    from crawlers.who_spider import crawl_who_sync
    return crawl_who_sync(max_jobs=50)


@celery_app.task(name="celery_app.crawl_fao_jobs")
def crawl_fao_jobs():
    """Crawl FAO (Food and Agriculture Organization) jobs."""
    from crawlers.fao_spider import crawl_fao_sync
    return crawl_fao_sync(max_jobs=50)


@celery_app.task(name="celery_app.crawl_unops_jobs")
def crawl_unops_jobs():
    """Crawl UNOPS (United Nations Office for Project Services) jobs."""
    from crawlers.unops_spider import crawl_unops_sync
    return crawl_unops_sync(max_jobs=50)


@celery_app.task(name="celery_app.crawl_ilo_jobs")
def crawl_ilo_jobs():
    """Crawl ILO (International Labour Organization) jobs."""
    from crawlers.ilo_spider import crawl_ilo_sync
    return crawl_ilo_sync(max_jobs=50)


@celery_app.task(name="celery_app.crawl_undp_jobs")
def crawl_undp_jobs():
    """Crawl UNDP jobs website."""
    from crawlers.undp_spider import crawl_undp_sync
    return crawl_undp_sync(max_jobs=50)


@celery_app.task(name="celery_app.crawl_unicef_jobs")
def crawl_unicef_jobs():
    """Crawl UNICEF careers website."""
    from crawlers.unicef_spider import crawl_unicef_sync
    return crawl_unicef_sync(max_jobs=50)


@celery_app.task(name="celery_app.send_job_alerts")
def send_job_alerts():
    """Send job alert emails to users based on their subscriptions."""
    # TODO: Implement job alert sending logic
    pass


@celery_app.task(name="celery_app.crawl_all_jobs")
def crawl_all_jobs():
    """Crawl all UN organization jobs in one task."""
    from run_all_crawlers import main as run_all
    return run_all()



